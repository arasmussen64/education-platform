from checks import function, run


def test_program():
    """Run directly, the tests pass and the score prints."""
    assert run() == "quiz: all checks passed\nScore: 7/10 (70.0%)\nPASS\n"


def test_pieces():
    """count_correct handles missing answers, and verdict has its boundary at 60."""
    assert function("count_correct")("ABCD", "AB") == 2
    assert function("verdict")(60) == "PASS"
    assert function("verdict")(59.9) == "FAIL"
    assert function("percent")(0, 0) == 0.0
