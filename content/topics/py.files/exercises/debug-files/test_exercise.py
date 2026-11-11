from pathlib import Path

from checks import function, printed, run


def test_program():
    """Running the program prints 1 buy milk, then 2 call Ada."""
    got = run()
    assert got == "1 buy milk\n2 call Ada\n", f"Your program printed:\n{got}"


def test_write_lines():
    """write_lines puts each item on its own line in the file."""
    function("write_lines")("w.txt", ["a", "b"])
    got = Path("w.txt").read_text(encoding="utf-8")
    assert got == "a\nb\n", f"the file contains {got!r}"


def test_print_lines():
    """print_lines prints each line of the file with its number: 1 x, then 2 y."""
    Path("p.txt").write_text("x\ny\n", encoding="utf-8")
    got = printed(function("print_lines"), "p.txt")
    assert got == "1 x\n2 y\n", f"print_lines printed:\n{got}"
