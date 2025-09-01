import os
from dotenv import load_dotenv
import chromadb

# Future-proof imports - use Google AI SDK instead. Vertex AI SDK will be deprecated.
try:
    import google.generativeai as genai

    USE_NEW_SDK = True
    print("Using new Google AI SDK")
except ImportError:
    # Fallback to Vertex AI
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from vertexai.language_models import TextEmbeddingModel

    USE_NEW_SDK = False
    print("Using Vertex AI SDK (will be deprecated)")

load_dotenv()

if USE_NEW_SDK:
    # Google AI SDK setup
    genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
    chat_model = genai.GenerativeModel("gemini-2.0-flash-lite")
    # Set up embedding model
    EMBEDDING_MODEL = "gemini-embedding-001"
else:
    # Vertex AI SDK setup
    PROJECT_ID = os.getenv("PROJECT_ID")
    vertexai.init(project=PROJECT_ID, location="us-central1")
    chat_model = GenerativeModel("gemini-2.0-flash-lite-001")
    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

# ChromaDB setup
chromadb_client = chromadb.PersistentClient(path="./chroma_db")
faq_collection = chromadb_client.get_or_create_collection("faq_docs")


def get_embeddings(texts):
    """Get embeddings for a list of texts using the appropriate SDK"""
    if USE_NEW_SDK:
        # Google AI SDK approach (google-generativeai package)
        if isinstance(texts, str):
            texts = [texts]

        try:
            # Process each text individually for Google AI SDK
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=EMBEDDING_MODEL,
                    content=text,
                    task_type="retrieval_document",  # Use lowercase for google-generativeai
                    output_dimensionality=768
                )
                # The result is a dict with 'embedding' key containing the vector
                if hasattr(result, 'embedding'):
                    embeddings.append(result.embedding)
                elif 'embedding' in result:
                    embeddings.append(result['embedding'])
                else:
                    print(f"Unexpected result format: {type(result)}")
                    print(f"Result keys: {result.keys() if hasattr(result, 'keys') else 'No keys'}")
                    return None
            return embeddings
        except Exception as e:
            print(f"Error with Google AI embeddings: {e}")
            print(f"Make sure your GOOGLE_AI_API_KEY is set correctly in .env file")
            return None
    else:
        # Vertex AI approach
        try: # calling embedding_model.get_embeddings() might fail
            embeddings = []
            for text in texts if isinstance(texts, list) else [texts]:
                vector = embedding_model.get_embeddings([text])[0].values
                embeddings.append(vector)
            return embeddings
        except Exception as e:
            print(f"Error with Vertex AI embeddings: {e}")
            return None


def get_query_embedding(query_text):
    """Get embedding for a single query text"""
    if USE_NEW_SDK:
        try: # calling genai.embed_content() might fail
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query_text,
                task_type="retrieval_query",  # Use lowercase for google-generativeai
                output_dimensionality=768
            )
            # The result structure varies, handle both cases
            if hasattr(result, 'embedding'):
                return result.embedding
            elif 'embedding' in result:
                return result['embedding']
            else:
                print(f"Unexpected query result format: {type(result)}")
                return None
        except Exception as e:
            print(f"Error with Google AI query embedding: {e}")
            print(f"Make sure your GOOGLE_AI_API_KEY is set correctly in .env file")
            return None
    else:
        try:
            return embedding_model.get_embeddings([query_text])[0].values
        except Exception as e:
            print(f"Error with Vertex AI query embedding: {e}")
            return None


def generate_embeddings():
    """Generate embeddings from FAQ JSON and store in ChromaDB"""
    import json

    try:
        with open("faq.json", "r") as f:
            faqs = json.load(f)
    except FileNotFoundError:
        print("Error: faq.json file not found!")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in faq.json!")
        return

    print(f"Processing {len(faqs)} FAQs...")

    # Process in batches for efficiency
    batch_size = 10
    for i in range(0, len(faqs), batch_size):
        batch = faqs[i:i + batch_size]

        try:
            # Get embeddings for the batch
            texts = [faq["content"] for faq in batch]
            embeddings = get_embeddings(texts)

            if embeddings is None:
                print(f"Failed to generate embeddings for batch starting at index {i}")
                continue

            # Add to ChromaDB
            for j, (faq, embedding) in enumerate(zip(batch, embeddings)):
                idx = i + j
                faq_collection.add(
                    ids=[str(idx)],
                    documents=[faq["content"]],
                    metadatas=[{
                        "title": faq.get("title", "No title"),
                        "url": faq.get("url", "No URL"),
                        "category": faq.get("category", "General")
                    }],
                    embeddings=[embedding]
                )

            print(f"Processed batch {i // batch_size + 1} of {(len(faqs) - 1) // batch_size + 1}")

        except Exception as e:
            print(f"Error processing batch starting at index {i}: {e}")
            continue

    print("Successfully added all FAQs to Chroma vector db")

def check_db():
    """Check database contents"""
    try:
        collections = chromadb_client.list_collections()
        print("Collections:", [c.name for c in collections])

        collection = chromadb_client.get_collection("faq_docs")
        count = collection.count()
        print(f"Total documents in collection: {count}")

        if count > 0:
            results = collection.peek(limit=3)
            print("Sample records:")
            for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                print(f"  {i + 1}. {metadata.get('title', 'No title')}")
                print(f"     {doc[:100]}...")

    except Exception as e:
        print(f"Error checking database: {e}")

def answer_question(user_query):
    """Answer user question using RAG with proper embeddings"""
    try:
        # Get query embedding
        query_vector = get_query_embedding(user_query)

        if query_vector is None:
            return "Error: Could not generate embedding for your query."

        # Search the vector database
        results = faq_collection.query(
            query_embeddings=[query_vector],
            n_results=3,  # Get top 3 results for better context
            include=["documents", "metadatas", "distances"]
        )

        if not results["documents"] or not results["documents"][0]:
            return "No relevant documentation found for your query."

        # Check similarity threshold (lower distance = more similar)
        best_distance = results["distances"][0][0] if results.get("distances") else 0

        # If the best match is too distant, it's probably not relevant
        if best_distance > 1.2:  # Adjust threshold as needed
            return "Not found in the documentation."

        # Get the best result
        best_doc = results["documents"][0][0]
        best_metadata = results["metadatas"][0][0]
        best_title = best_metadata.get("title", "No title")
        best_url = best_metadata.get("url", "No URL")

        # Generate response using the LLM
        prompt = f"""You are a helpful IT support employee assisting with client IT issues.

        Your client asked: "{user_query}"
        
        Here is the most relevant FAQ:
        Title: {best_title}
        Content: {best_doc}
        Source: {best_url}
        
        Rules:
        - Always give a clear and concise answer.
        - Begin your answer with the source URL.
        - Only provide the answer; do not ask follow-up questions or suggest further discussion.
        - If the client's question does not closely match the FAQ content, Respond with exactly: "Not found in the documentation." 
        """

        response = chat_model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error processing your question: {e}"

def main():
    """Main interactive loop"""
    print("IT support FAQ Assistant")
    print(f"Using {'Google AI SDK' if USE_NEW_SDK else 'Vertex AI SDK'}")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 40)

    while True:
        user_input = input("\nPlease describe the IT issue for your client: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Thank you for using IT support FAQ Assistant")
            break

        if not user_input:
            print("Please enter a valid question.")
            continue

        print("\nProcessing your question...Just a moment.")
        answer = answer_question(user_input)
        print(f"\nAnswer: {answer}")
        print("-" * 40)


if __name__ == "__main__":
    # Uncomment these lines when needed:
    # generate_embeddings()  # Run once when JSON is updated
    # check_db()  # Use to verify database contents

    # Start the interactive session
    main()