import os
from supabase import create_client

# Future-proof imports - use Google AI SDK instead. Vertex AI SDK will be deprecated.
try:  # importing new SDK might fail
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

if USE_NEW_SDK:
    # Google AI SDK setup
    genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
    chat_model = genai.GenerativeModel("gemini-2.5-flash-lite")
    # Set up embedding model
    EMBEDDING_MODEL = "gemini-embedding-001"
else:
    # Vertex AI SDK setup
    PROJECT_ID = os.getenv("PROJECT_ID")
    vertexai.init(project=PROJECT_ID, location="us-central1")
    chat_model = GenerativeModel("gemini-2.5-flash-lite-001")
    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

# Cloud version using Supabase vector. Not local ChromaDB
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(url, key)


def get_embeddings(texts):
    """
    Get embeddings for a list of texts using the appropriate SDK.
    This is for faq.json embedding because of task_type="retrieval_document"
    Takes faq text as input
    Returns list of embeddings

    """
    if USE_NEW_SDK:
        # Google AI SDK approach (google-generativeai package)
        if isinstance(texts,
                      str):
            texts = [texts]

        try:
            # Process each text individually for Google AI SDK
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=EMBEDDING_MODEL,
                    content=text,
                    task_type="retrieval_document",
                    output_dimensionality=768  # common dimension number used in NlP models
                )
                if hasattr(result,
                           'embedding'):
                    embeddings.append(result.embedding)
                elif 'embedding' in result:
                    embeddings.append(result['embedding'])
                else:
                    print(f"Unexpected result format: {type(result)}")
                    print(f"Result keys: {result.keys() if hasattr(result, 'keys') else 'No keys'}")
                    return None
            return embeddings  # retuning the list type of embeddings
        except Exception as e:
            print(f"Error with Google AI embeddings: {e}")
            print(f"Make sure your GOOGLE_AI_API_KEY is set correctly in .env file")
            return None
    else:
        # Using old Vertex AI SDK approach
        try:
            embeddings = []
            for text in texts if isinstance(texts, list) else [
                texts]:
                vector = embedding_model.get_embeddings([text])[0].values
                embeddings.append(vector)
            return embeddings
        except Exception as e:
            print(f"Error with Vertex AI embeddings: {e}")
            return None


def get_query_embedding(query_text):
    """
    Get embedding for a single query text
    This is for user input embedding because of task_type="retrieval_query"
    Takes user input as input
    Returns one single embedding result
    """
    if USE_NEW_SDK:
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query_text,
                task_type="retrieval_query",
                output_dimensionality=768  # common dimension number used in NLP models
            )
            # The result structure varies, handle both cases
            if hasattr(result,
                       'embedding'):
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

def answer_question_supabase(user_query):
    """
    Answer user question using RAG with proper embeddings. Core function in this system
    Takes user input as input, pass the data to get_query_embedding() function and then get embedding data from it
    Call chat_model.generate_content() and then pass prompt
    Returns gemini's response in human language.
    """
    try:
        # this is same
        # 1. Get query embedding
        query_vector = get_query_embedding(user_query)
        if query_vector is None:
            return "Error: Could not generate embedding for your query."

        # this is different.
        # rpc stands for Remote Procedure Call. It calls the function declared in SQL editor.
        # rpc itself is not the function to search query. The defined function does.
        # 2. Query Supabase vector search (match_faqs function)
        response = supabase.rpc(
            "match_faqs",
            # must exist in Supabase SQL Editor # I added "SQL-function" note in practice folder for actual code and explanation
            {  # these parameter will be sent to the SQL function "match_faqs"
                "query_embedding": query_vector,  # user word converted as vector. Input words.
                "match_threshold": 0.5,  # adjust based on testing
                "match_count": 3
            }
        ).execute()  # without this .execute(), it does not send HTTP request

        results = response.data

        # same, defensive programming
        # 3. Edge case: no matches
        if not results or len(results) == 0:
            return "No relevant documentation found for your query."

        # 4. Pick the best result (highest similarity)
        best = max(results, key=lambda x: x["similarity"])
        # this is going through results item, and then by max(), choosing item based on  the most high "similarity"
        # And key needs to be callable. That is why it needs to be using lambda to make it function
        best_doc = best["content"]
        best_title = best.get("title", "No title")
        best_url = best.get("url", "No URL")
        best_similarity = best.get("similarity", 0)

        # 5. Relevance check — if not similar enough
        # this is actually different, if best_distance > 0.5 is the original form in chroma DB
        if best_similarity < 0.5:
            return "Not found in the documentation."

        # no change here
        # 6.  Generate LLM response
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
        - If the client's question does not closely match the FAQ content, respond with exactly: "Not found in the documentation." and stop providing the source URL.
        """

        response = chat_model.generate_content(prompt) # this is the function need to be mocked
        return response.text

    except Exception as e:
        return f"Error processing your question: {e}"

def main():
    """
    Main interactive loop.
    Take user input as input using input() and then pass the data to call answer_question() function.
    print out gemini's response
     """
    print("Break/Fix FAQ Assistant")
    # print(f"Using {'Google AI SDK' if USE_NEW_SDK else 'Vertex AI SDK'}")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 40)

    while True:
        user_input = input("\nPlease describe the IT issue for your client: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Thank you for using Break/Fix FAQ Assistant")
            break

        if not user_input:
            print("Please enter a valid question.")
            continue

        print("\nProcessing your question...Just a moment.")
        answer = answer_question_supabase(user_input)
        print(f"\nAnswer: {answer}")
        print("-" * 40)

if __name__ == "__main__":
    main()