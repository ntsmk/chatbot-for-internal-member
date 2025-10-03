import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from main import get_query_embedding, get_embeddings

def test_get_embeddings():
    """
    This is **unit test** because this only does assert
    Check batch embedding generation
    This is testing get_embeddings(texts) function.
    """
    texts = ["How to login?", "How to install printer driver?"] # preparing input data
    embeddings = get_embeddings(texts) # passing input data and getting output

    assert embeddings is not None
    assert len(embeddings) > 0
    assert len(embeddings) == len(texts) # testing if returned output matches input list
    # bare minimum. just testing it is not failing.

    # assert vec == 768 (for vec in embeddings) # ???, asked gpt how to do it
    for vec in embeddings:
        assert len(vec) == 768

    assert all(isinstance(vec, (list, tuple)) for vec in embeddings) # checking if the data is list or tuple one by one from embedding list
    # I reviewed this with gpt and for solo dev, this is enough


def test_get_query_embedding():
    """
    This is **unit test** because this only does assert
    Check that embeddings can be generated for a simple query
    This is checking get_query_embedding(query) functions
    """
    query = "How to reset my password?" # preparing dummy input mocking the user input as single data
    embedding = get_query_embedding(query) # getting output by calling the function.

    assert embedding is not None # it does not eliminate the case of empty, but at least it proves no error happened
    assert len(embedding) > 0  # it is checking if empty or not
    # above is bare minimum. testing at least it did not fail.

    assert isinstance(embedding, (list, tuple)) # (list, tuple) meaning list or tuple.
    # why -> even if it is single embedding, it will be "(e.g., [0.12, -0.34, 0.56, ...]". List is more common than tuple
    assert len(embedding) == 768  # added new one. This is coming from "output_dimensionality=768"
    # these are structure tests. Testing valid type and shape before checking the inside of data

    assert all(isinstance(x, (float, int)) for x in embedding) # if embedding = [0.12, "opps"] -> it fails. (float, int) means float or int
    assert all(not isinstance(x, (list, tuple)) for x in embedding) # testing inside of data is not tuple i.e. [12, 21, [1.3,4]] -> fails.  (list, tuple) meaning list or tuple.
    # these are content tests. checking the inside of data(list or tuple), if it is float or int?

