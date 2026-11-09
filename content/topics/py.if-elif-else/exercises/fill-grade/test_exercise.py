from checks import run


def grade(score):
    return run(f"{score}\n")


def test_middle_of_each_band():
    """95 is an A, 85 a B, 75 a C and 60 an F."""
    for score, letter in [(95, "A"), (85, "B"), (75, "C"), (60, "F")]:
        printed = grade(score)
        assert printed == f"Grade: {letter}\n", (
            f"Typing {score} should print Grade: {letter}. Your program printed:\n{printed}"
        )


def test_boundaries():
    """80 is already a B and 70 already a C; 79 is a C and 69 an F."""
    for score, letter in [(80, "B"), (70, "C"), (79, "C"), (69, "F")]:
        printed = grade(score)
        assert printed == f"Grade: {letter}\n", (
            f"Typing {score} should print Grade: {letter}. Your program printed:\n{printed}"
        )
