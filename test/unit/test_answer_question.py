import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.main import answer_question, faq_collection

# passing monkeypatch to the function -> why? (the parameter) → is an instance of pytest’s MonkeyPatch fixture.
# when calling monkeypatch.setattr(), it needs to access monkeypatch fixture.
def test_answer_question_found(monkeypatch):
    """
    This is still **unit test** with mocking, according to gpt. sometimes called a mocked integration test.
    True integration test calls the real dependencies like relying on real API, DB etc.
    And as for solo dev, this is fine. Integration test is for a larger team.
    Mock DB so we can test answer_question(user_query) behavior
    This is the example of mocking external API calls
    """

    # 1 Fake query embedding
    monkeypatch.setattr("main.get_query_embedding", lambda q: [0.1, 0.2, 0.3])
    # calling get_query_embedding to test, and then? need to remember how monkeypatch.setattr() works.
    # monkeypatch is not actual test. Just a setup. Replacing with fake data.
    # Any call like main.get_query_embedding("reset password") → will return [0.1, 0.2, 0.3]. Real function never touched

    # monkeypatch.setattr("main.get_query_embedding", [0.1, 0.2, 0.3]) cant it be this? the answer is below
    # monkeypatch.setattr(target, value) and value must be callable function. That is why it has to be lambda, because lambda is simplified function
    # monkeypatch is replacing "main.get_query_embedding" as lambda q: [0.1, 0.2, 0.3],
    # def answer_question(user_query): is used in the function answer_question()

    # 2 Fake DB query faq_collection as fake_query
    # creating fake function to place with.
    def fake_query(*args, **kwargs):
        return {
            "documents": [["Reset password instructions"]],
            "metadatas": [[{"title": "Password Reset", "url": "http://example.com"}]],
            "distances": [[0.5]],
        }
    monkeypatch.setattr(faq_collection, "query", fake_query) # using this fake function defined
    # in the original code, results = faq_collection.query() that is why "query" in the monkeypatch, the last part has to be callable that is why creating fake function
    # monkeypatch.setattr(target, real function or attribute name inside of target, callable function, replacing it with this.)

    # 3 Fake chat model response
    class FakeResponse: # this is just putting dummy text to "text" variable.
        text = "http://example.com You can reset your password via Settings." # faking simple attribute ".text"
    monkeypatch.setattr("main.chat_model.generate_content", lambda prompt: FakeResponse()) # using fake class defined
    # "lambda prompt: FakeResponse()" what does this mean? -> anytime calling .chat_model.generate_content, returning fake class with simple text attribute
    # response = chat_model.generate_content(prompt) return response.text, this is used in answer_question(user_query)
    # making fake response and replacing it.

    # 4 one assert
    result = answer_question("How do I reset my password?") # calling real function answer_question() but anything used in this is a fake set up by monkeypatch
    assert "reset your password" in result.lower()
    # this is only assert in this function. it uses fake embedding, fake DB, and fake prompt to AI.
    # those are fake because used monkeypatch. With all external dependencies mocked using monkeypatch.

def test_answer_question_not_found(monkeypatch):
    """Check fallback behavior when nothing relevant"""

    # This is actually same as def test_answer_question_found(monkeypatch):, fake query embedding, using lambda because it needs to be callable.
    monkeypatch.setattr("main.get_query_embedding", lambda q: [0.1, 0.2, 0.3])

    # To make this unfound. Just faking empty input, same structure but just returning empty
    def fake_query(*args, **kwargs):
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    monkeypatch.setattr(faq_collection, "query", fake_query)

    # only assert. Testing if the function returns the desired output for edge case.
    result = answer_question("Some random unrelated question")
    assert "no relevant" in result.lower() or "not found" in result.lower()