import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import answer_question, get_query_embedding, get_embeddings, faq_collection

def test_get_query_embedding():
    """Check that embeddings can be generated for a simple query"""
    query = "How to reset my password?"
    embedding = get_query_embedding(query)
    assert embedding is not None
    assert isinstance(embedding, (list, tuple))
    assert len(embedding) > 0

def test_get_embeddings_batch():
    """Check batch embedding generation"""
    texts = ["How to login?", "How to install printer driver?"]
    embeddings = get_embeddings(texts)
    assert embeddings is not None
    assert len(embeddings) == len(texts)
    assert all(isinstance(vec, (list, tuple)) for vec in embeddings)

def test_answer_question_found(monkeypatch):
    """Mock DB so we can test answer_question behavior"""

    # Fake query embedding
    monkeypatch.setattr("main.get_query_embedding", lambda q: [0.1, 0.2, 0.3])

    # Fake DB query
    def fake_query(*args, **kwargs):
        return {
            "documents": [["Reset password instructions"]],
            "metadatas": [[{"title": "Password Reset", "url": "http://example.com"}]],
            "distances": [[0.5]],
        }
    monkeypatch.setattr(faq_collection, "query", fake_query)

    # Fake chat model response
    class FakeResponse:
        text = "http://example.com You can reset your password via Settings."
    monkeypatch.setattr("main.chat_model.generate_content", lambda prompt: FakeResponse())

    result = answer_question("How do I reset my password?")
    assert "reset your password" in result.lower()

def test_answer_question_not_found(monkeypatch):
    """Check fallback behavior when nothing relevant"""
    monkeypatch.setattr("main.get_query_embedding", lambda q: [0.1, 0.2, 0.3])

    def fake_query(*args, **kwargs):
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    monkeypatch.setattr(faq_collection, "query", fake_query)

    result = answer_question("Some random unrelated question")
    assert "no relevant" in result.lower() or "not found" in result.lower()
