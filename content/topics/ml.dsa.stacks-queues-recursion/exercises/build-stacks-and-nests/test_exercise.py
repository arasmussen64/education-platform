from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == '14 14\nTrue False True\n0 1 3\n[1, 2, 3, 4, 5, 6]\n'


def test_postfix():
    """2 3 4 * + is 14, 10 2 - is 8, and a lone number is itself."""
    evaluate_postfix = function("evaluate_postfix")
    assert (evaluate_postfix("2 3 4 * +"), evaluate_postfix("10 2 -"), evaluate_postfix("7")) == (14, 8, 7)


def test_balanced():
    """Nested pairs of every kind pass; a crossed pair, a lone opener and a lone closer fail."""
    balanced = function("balanced")
    assert balanced("{[()]}") and balanced("a(b[c]{d})e")
    assert not balanced("{[(])}") and not balanced("(") and not balanced(")")


def test_max_depth():
    """Four empty lists nested are depth 4; [1, [2], [[3]]] is depth 3."""
    max_depth = function("max_depth")
    assert (max_depth([[[[]]]]), max_depth([1, [2], [[3]]])) == (4, 3)


def test_flatten_five_thousand_levels():
    """A nest 5,000 levels deep flattens to the 5,000 numbers in order, and a small nest keeps its order."""
    flatten_iterative = function("flatten_iterative")
    nested = [4999]
    for i in range(4998, -1, -1):
        nested = [i, nested]
    assert flatten_iterative(nested) == list(range(5000))
    assert flatten_iterative([[1, 2], [3, [4]], 5]) == [1, 2, 3, 4, 5]
