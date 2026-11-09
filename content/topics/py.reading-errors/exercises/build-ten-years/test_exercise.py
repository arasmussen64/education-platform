from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_ada():
    """Typing Ada and 36 prints Hello, Ada! In 10 years you'll be 46."""
    assert run("Ada\n36\n") == "Hello, Ada! In 10 years you'll be 46.\n"


def test_someone_else():
    """Works for any name and age: Sam and 9 gives 19."""
    assert run("Sam\n9\n") == "Hello, Sam! In 10 years you'll be 19.\n"
