from checks import run


def test_the_walkthrough():
    """Prints the good hash's counts, the bad hash's, the list scan's and the agreement with dict."""
    assert run() == "good hash: 2048 buckets, longest 3 | 1000 lookups: 1414 comparisons\nbad hash: 2048 buckets, longest 900 | 1000 lookups: 409600 comparisons\nlist scans: 1000 lookups: 500500 comparisons\nPython's dict agrees: True\n"
