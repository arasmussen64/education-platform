from checks import run


def test_the_table():
    """Prints both balances every ten years, then the share the fee took, two ways."""
    assert run() == (
        "Year 10: $19,671.51 without the fee, $17,790.56 with it\n"
        "Year 20: $38,696.84 without the fee, $31,650.42 with it\n"
        "Year 30: $76,122.55 without the fee, $56,307.88 with it\n"
        "The fee took 26.0%\n"
        "By the formula: 26.0%\n"
    )
