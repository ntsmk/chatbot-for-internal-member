import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.chatbot import answer_question_supabase, supabase

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

    # Fake embedding
    monkeypatch.setattr(
        "app.chatbot.get_query_embedding",
        lambda q: [0.01] * 768
    )

    # Fake Supabase RPC
    fake_data = [
        {
            "content": "You can reset your password in the portal.",
            "title": "Password Reset",
            "url": "http://example.com",
            "similarity": 0.9,
        }
    ]

    class FakeRPCResult:
        def __init__(self, data):
            self.data = data

    class FakeRPC:
        def __init__(self, data):
            self._data = data

        def execute(self):
            return FakeRPCResult(self._data)

    monkeypatch.setattr(
        "app.chatbot.supabase.rpc",
        lambda fn, params: FakeRPC(fake_data)
    )

    # Fake Gemini response
    class FakeLLMResponse:
        text = "http://example.com\nYou can reset your password."

    def fake_generate_content(prompt):
        return FakeLLMResponse()

    # THIS is the critical mock
    monkeypatch.setattr(
        "app.chatbot.chat_model.generate_content",
        fake_generate_content
    )

    # Call real function
    from app.chatbot import answer_question_supabase

    result = answer_question_supabase("How do I reset my password?")

    assert "reset your password" in result.lower()

# After I modified lambda q: [0.01] * 768, it passed. The issue was only supabase dimension part
def test_answer_question_not_found(monkeypatch):
    """Check fallback behavior when nothing relevant"""

    # This is actually same as def test_answer_question_found(monkeypatch):, fake query embedding, using lambda because it needs to be callable.
    monkeypatch.setattr("app.chatbot.get_query_embedding", lambda q: [0.01] * 768) # changed here to match Supabase’s expectation.

    # 1. Fake Supabase response data
    fake_data = [
        {
            "content": "Reset password instructions",
            "title": "Password Reset",
            "url": "http://example.com",
            "similarity": 0.2 # setting 0.2 as example fake dataset wiki, to test if this is rejected as 0.2 < 0.5
            # this is not the point so changing it to 0.8
        }
    ]

    # 2. Fake object returned by .execute()
    class FakeRPCResult:
        def __init__(self, data):
            self.data = data

    # 3. Fake object returned by supabase.rpc(...)
    class FakeRPC:
        def __init__(self, data):
            self._data = data

        def execute(self):
            return FakeRPCResult(self._data)

    # 4. Monkeypatch supabase.rpc
    monkeypatch.setattr(
        supabase,
        "rpc",
        lambda fn_name, params: FakeRPC(fake_data)
    )
    result = answer_question_supabase("Some random unrelated question")
    print(result)
    assert "no relevant" in result.lower() or "not found" in result.lower()