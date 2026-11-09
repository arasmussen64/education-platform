from pathlib import Path

from checks import function, run


def test_reads_a_file_the_test_wrote():
    """total_in adds the numbers in a file the test creates."""
    Path("scores.txt").write_text("10\n20\n", encoding="utf-8")
    assert function("total_in")("scores.txt") == 30


def test_program_writes_then_reads():
    """Running the program writes numbers.txt and prints 6."""
    assert run() == "6\n"
    assert Path("numbers.txt").read_text(encoding="utf-8") == "1\n2\n3\n"


def test_missing_file():
    """A file that isn't there raises FileNotFoundError."""
    try:
        function("total_in")("nowhere.txt")
    except FileNotFoundError:
        return
    assert False, "expected FileNotFoundError"
