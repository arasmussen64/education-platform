from pathlib import Path

from checks import function, run


def test_program():
    """Running the program prints the three names in alphabetical order."""
    assert run() == "Harry\nHermione\nRon\n"


def test_round_trip():
    """save_names writes one name per line, and load_names reads them back without line breaks."""
    function("save_names")("trip.txt", ["a", "b"])
    assert Path("trip.txt").read_text(encoding="utf-8") == "a\nb\n"
    assert function("load_names")("trip.txt") == ["a", "b"]
