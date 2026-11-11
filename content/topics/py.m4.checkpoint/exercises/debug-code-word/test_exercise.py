from checks import function, run


def test_length_boundary():
    """has_min_length is True for a 5-character word and False for 4."""
    has_min_length = function("has_min_length")
    assert has_min_length("brave") is True, 'has_min_length("brave") should be True'
    assert has_min_length("cats") is False, 'has_min_length("cats") should be False'


def test_vowel_search():
    """has_vowel is True for brave and strong, and False for rhythm and crypt."""
    has_vowel = function("has_vowel")
    assert has_vowel("brave") is True, 'has_vowel("brave") should be True'
    assert has_vowel("strong") is True, 'has_vowel("strong") should be True'
    assert has_vowel("rhythm") is False, 'has_vowel("rhythm") should be False'
    assert has_vowel("crypt") is False, 'has_vowel("crypt") should be False'


def test_expectations():
    """test_check_word() runs to the end without an assert failing."""
    function("test_check_word")()


def test_program():
    """Run directly with brave, the program prints the tests' message and then OK."""
    got = run("brave\n")
    assert got == "check_word: all checks passed\nOK\n", f"Your program printed:\n{got}"
    got = run("crypt\n")
    assert got == "check_word: all checks passed\nneeds a vowel\n", (
        f"Your program printed:\n{got}"
    )
