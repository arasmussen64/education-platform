from checks import run


def test_mixed_week():
    """ssrsssrr: 5 sunny days, 3 rainy, longest streak 3, and two bars."""
    assert run("ssrsssrr\n") == (
        "Sunny days: 5\nRainy days: 3\nLongest sunny streak: 3\nSun:  #####\nRain: ###\n"
    )


def test_all_sun():
    """sss: the streak at the end counts, so the longest is 3."""
    assert run("sss\n") == (
        "Sunny days: 3\nRainy days: 0\nLongest sunny streak: 3\nSun:  ###\nRain: \n"
    )


def test_all_rain():
    """rrr: no sunny days, so the longest streak is 0 and the sun bar is empty."""
    assert run("rrr\n") == (
        "Sunny days: 0\nRainy days: 3\nLongest sunny streak: 0\nSun:  \nRain: ###\n"
    )
