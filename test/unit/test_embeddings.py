import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def test_get_embeddings(monkeypatch):
    monkeypatch.setattr(
        "chatbot.engine.get_embeddings",
        lambda q: [[0.01] * 768 for _ in texts] # because get_embeddings() returns a list of embeddings
    )

    from chatbot.engine import get_embeddings # this has to be after monkeypatch.setattr, because it needs to be patched one, not original one

    texts = ["How to login?", "How to install printer driver?"]
    embeddings = get_embeddings(texts)

    assert embeddings is not None
    assert len(embeddings) == len(texts)

    for vec in embeddings:
        assert len(vec) == 768
        assert isinstance(vec, (list, tuple))
        assert all(isinstance(x, (float, int)) for x in vec)


def test_get_query_embedding(monkeypatch):
    monkeypatch.setattr(
        "chatbot.engine.get_query_embedding",
        lambda q: [0.01] * 768
    )

    from chatbot.engine import get_query_embedding

    query = "How to reset my password?"
    embedding = get_query_embedding(query)

    assert embedding is not None
    assert len(embedding) == 768
    assert isinstance(embedding, (list, tuple))
    assert all(isinstance(x, (float, int)) for x in embedding)
