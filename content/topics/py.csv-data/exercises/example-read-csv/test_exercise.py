from pathlib import Path

from checks import function, run


def test_program():
    """Running the program prints a line per person and the total age."""
    assert run() == "Ada lives in London\nBob lives in Leeds\nTotal age: 77\n"


def test_sample_file():
    """write_sample writes a header and two records."""
    function("write_sample")("sample.csv")
    assert Path("sample.csv").read_text(encoding="utf-8") == (
        "name,city,age\nAda,London,36\nBob,Leeds,41\n"
    )
