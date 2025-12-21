import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import app.chatbot as chatbot
from app.chatbot import answer_question_supabase

def test_answer_question_found(monkeypatch):

    # 1. Fake embedding
    monkeypatch.setattr(
        "app.chatbot.get_query_embedding",
        lambda q: [0.01] * 768
    )

    # 2. Fake Supabase RPC
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
        chatbot.supabase,
        "rpc",
        lambda fn_name, params: FakeRPC(fake_data)
    )

    # 3. Fake Gemini response
    class FakeLLMResponse:
        text = "http://example.com\nYou can reset your password."
        # why it needs to be class? -> because it needs to return response.text, the attribute ".text", following the production code.

    def fake_generate_content(prompt):
        return FakeLLMResponse()

    # THIS is the critical mock, because inside of answer_question_supabase, this function exists and cant use real API
    monkeypatch.setattr(
        "chatbot.chat_model.generate_content",
        fake_generate_content
    )

    # 4. Call real function
    result = answer_question_supabase("How do I reset my password?")
    assert "reset your password" in result.lower()

def test_answer_question_not_found(monkeypatch):

    # 1. Fake embedding
    monkeypatch.setattr(
        "app.chatbot.get_query_embedding",
        lambda q: [0.01] * 768
    )

    # 2. Fake Supabase RPC
    fake_data = [
        {
            "content": "Reset password instructions",
            "title": "Password Reset",
            "url": "http://example.com",
            "similarity": 0.2 # this making irrelevant to make happen "not found"
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
        chatbot.supabase,
        "rpc",
        lambda fn_name, params: FakeRPC(fake_data)
    )

    # why this pass without faking Gemini response unlike def test_answer_question_found
    # "similarity": 0.2 is not 0.9 in test_answer_question_found, that is why .generate_content not called first off.
    #        if best_similarity < 0.5:
    #        return "Not found in the documentation."
    # this is in chatbot.py answer_question_supabase function. This is why assert "not found" in result.lower() pass.

    # 4. Call real function, but it does not hit gemini real API because of low similarity, skipping Fake Gemini response part
    result = answer_question_supabase("Some random unrelated question")
    assert "no relevant" in result.lower() or "not found" in result.lower()