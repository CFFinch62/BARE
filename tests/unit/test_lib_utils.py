"""Unit tests for bare_core.lib_utils.extract_sub_blocks."""

from bare_core.lib_utils import extract_sub_blocks


def test_empty_source():
    assert extract_sub_blocks("") == {}


def test_no_subs():
    assert extract_sub_blocks('print "hello"\nx = 1\n') == {}


def test_single_sub():
    source = "sub double(x)\n    return x * 2\nend\n"
    blocks = extract_sub_blocks(source)
    assert set(blocks) == {"double"}
    assert blocks["double"] == "sub double(x)\n    return x * 2\nend"


def test_multiple_subs_preserve_each_exactly():
    source = (
        "sub double(x)\n"
        "    return x * 2\n"
        "end\n"
        "\n"
        "sub triple(x)\n"
        "    return x * 3\n"
        "end\n"
    )
    blocks = extract_sub_blocks(source)
    assert set(blocks) == {"double", "triple"}
    assert blocks["double"] == "sub double(x)\n    return x * 2\nend"
    assert blocks["triple"] == "sub triple(x)\n    return x * 3\nend"


def test_sub_with_nested_if_and_while_not_cut_short():
    source = (
        "sub classify(x)\n"
        "    if x > 0\n"
        "        while x > 10\n"
        "            x = x - 1\n"
        "        end\n"
        "        return \"positive\"\n"
        "    else\n"
        "        return \"non-positive\"\n"
        "    end\n"
        "end\n"
    )
    blocks = extract_sub_blocks(source)
    assert set(blocks) == {"classify"}
    assert blocks["classify"] == source.strip("\n")


def test_top_level_statements_around_subs_are_excluded():
    source = 'print "before"\nsub greet()\n    print "hi"\nend\nprint "after"\n'
    blocks = extract_sub_blocks(source)
    assert set(blocks) == {"greet"}
    assert blocks["greet"] == "sub greet()\n    print \"hi\"\nend"
