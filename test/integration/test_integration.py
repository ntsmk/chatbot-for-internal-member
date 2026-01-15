import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from chatbot.engine import answer_question_supabase

pytestmark = pytest.mark.integration

# because no .env file set locally nor No shell export
@pytest.mark.skipif(
    not os.getenv("GOOGLE_AI_API_KEY"),
    reason="GOOGLE_AI_API_KEY not set"
)

def test_answer_question_integration():

    # 1. Prepare a real user query
    query = "How do I reset my password?"

    # 2. Call the actual function without mocking anything
    result = answer_question_supabase(query)

    # 3. Assertions
    assert result is not None  # function returns something
    assert len(result) > 0  # result is not empty
    assert isinstance(result, str)  # result should be a string
    assert "password" in result.lower()  # expected keyword in the response
