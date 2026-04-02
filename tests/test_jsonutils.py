import os

from boltons.jsonutils import (JSONLIterator,
                               DEFAULT_BLOCKSIZE,
                               reverse_iter_lines)

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
NEWLINES_DATA_PATH = CUR_PATH + '/newlines_test_data.txt'
JSONL_DATA_PATH = CUR_PATH + '/jsonl_test_data.txt'


def _test_reverse_iter_lines(filename, blocksize=DEFAULT_BLOCKSIZE):
    fo = open(filename)
    reference = fo.read()
    fo.seek(0, os.SEEK_SET)
    rev_lines = list(reverse_iter_lines(fo, blocksize))
    assert '\n'.join(rev_lines[::-1]) == reference


def _test_reverse_iter_lines_bytes(filename, blocksize=DEFAULT_BLOCKSIZE):
    fo = open(filename, 'rb')
    reference = fo.read()
    fo.seek(0, os.SEEK_SET)
    rev_lines = list(reverse_iter_lines(fo, blocksize))
    assert os.linesep.encode('ascii').join(rev_lines[::-1]) == reference



def test_reverse_iter_lines():
    for blocksize in (2, 4, 16, 4096):
        _test_reverse_iter_lines(NEWLINES_DATA_PATH, blocksize)
        _test_reverse_iter_lines_bytes(NEWLINES_DATA_PATH, blocksize)


def test_jsonl_iterator():
    ref = [{'4': 4}, {'3': 3}, {'2': 2}, {'1': 1}, {}]
    jsonl_iter = JSONLIterator(open(JSONL_DATA_PATH), reverse=True)
    jsonl_list = list(jsonl_iter)
    assert jsonl_list == ref


def test_jsonl_blank_lines():
    import io
    jsonl_content = '''{"a": 1}

{"b": 2}
   
{"c": 3}
\t
{"d": 4}
'''
    text_io = io.StringIO(jsonl_content)
    jsonl_iter = JSONLIterator(text_io)
    result = list(jsonl_iter)
    assert result == [{'a': 1}, {'b': 2}, {'c': 3}, {'d': 4}]


def test_jsonl_blank_lines_bytes():
    import io
    jsonl_content = b'''{"a": 1}

{"b": 2}
   
{"c": 3}
\t
{"d": 4}
'''
    bytes_io = io.BytesIO(jsonl_content)
    jsonl_iter = JSONLIterator(bytes_io)
    result = list(jsonl_iter)
    assert result == [{'a': 1}, {'b': 2}, {'c': 3}, {'d': 4}]


def test_jsonl_error_line_number():
    import io
    jsonl_content = '''{"a": 1}
{"b": 2}
invalid json
{"c": 3}
'''
    text_io = io.StringIO(jsonl_content)
    jsonl_iter = JSONLIterator(text_io)
    assert next(jsonl_iter) == {'a': 1}
    assert next(jsonl_iter) == {'b': 2}
    try:
        next(jsonl_iter)
        assert False, 'should have raised ValueError'
    except ValueError as e:
        assert 'line 3' in str(e)
        assert e.__cause__ is not None


def test_jsonl_error_line_number_with_blank_lines():
    import io
    jsonl_content = '''{"a": 1}

{"b": 2}

invalid json
{"c": 3}
'''
    text_io = io.StringIO(jsonl_content)
    jsonl_iter = JSONLIterator(text_io)
    assert next(jsonl_iter) == {'a': 1}
    assert next(jsonl_iter) == {'b': 2}
    try:
        next(jsonl_iter)
        assert False, 'should have raised ValueError'
    except ValueError as e:
        assert 'line 5' in str(e)


def test_jsonl_ignore_errors():
    import io
    jsonl_content = '''{"a": 1}
invalid json
{"b": 2}
also invalid
{"c": 3}
'''
    text_io = io.StringIO(jsonl_content)
    jsonl_iter = JSONLIterator(text_io, ignore_errors=True)
    result = list(jsonl_iter)
    assert result == [{'a': 1}, {'b': 2}, {'c': 3}]
