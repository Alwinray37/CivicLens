import json
from utils.chunker import Chunker


with open("tests/chunker/example-text.txt") as file:
    text = file.read()

with open("tests/chunker/expected-fixed.json") as json_file:
    chunk_data = json.loads(json_file.read())

chunker = Chunker("qwen3-embedding:4b")

def test_fixed_chunk():
    actual = chunker.fixed_chunk(text, "fixed", '\n', 30, 0)

    expected = chunk_data["30"]["no_overlap"]

    assert actual == expected

def test_fixed_chunk_overlap():
    actual = chunker.fixed_chunk(text, "fixed", '\n', 30, 5)

    expected = chunk_data["30"]["overlap"]

    assert actual == expected

def test_fixed_chunk_negative_overlap():
    actual = chunker.fixed_chunk(text, "fixed", '\n', 30, -25)

    expected = chunk_data["30"]["overlap"]

    assert actual == expected

def test_fixed_chunk_oversized_chunk():
    # 124 lines in file, 200 chunk size
    actual = chunker.fixed_chunk(text, "fixed", '\n', 200, 0)

    expected = chunk_data["200"]["no_overlap"]

    assert actual == expected

def test_fixed_chunk_oversized_chunk_overlap():
    # 124 lines in file, 200 chunk size
    actual = chunker.fixed_chunk(text, "fixed", '\n', 200, 5)

    expected = chunk_data["200"]["no_overlap"]

    assert actual == expected

def test_fixed_chunk_zero():
    # 124 lines in file, 200 chunk size
    actual = chunker.fixed_chunk(text, "fixed", '\n', 0, 0)

    expected = chunk_data["200"]["no_overlap"]

    assert actual == expected
