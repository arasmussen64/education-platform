from checks import function, run

EXPECTED = "Player('Ada', 30)\n30\n"


def test_the_output():
    """Prints Player('Ada', 30), then 30."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_a_new_player_starts_at_zero():
    """A new Player has a score of 0, and add_points(7) makes it 7."""
    Player = function("Player")
    bob = Player("Bob")
    assert bob.score == 0
    bob.add_points(7)
    assert bob.score == 7
