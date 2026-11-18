from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

TABLE = (
    "10 years: $44,771.19 without the fee, $41,315.73 with it, 7.7% lost\n"
    "20 years: $80,178.39 without the fee, $68,279.57 with it, 14.8% lost\n"
    "30 years: $143,587.28 without the fee, $112,840.79 with it, 21.4% lost\n"
    "40 years: $257,142.95 without the fee, $186,483.97 with it, 27.5% lost\n"
)

OTHER_TABLE = (
    "10 years: $2,593.74 without the fee, $2,119.28 with it, 18.3% lost\n"
    "20 years: $6,727.50 without the fee, $4,491.33 with it, 33.2% lost\n"
    "30 years: $17,449.40 without the fee, $9,518.38 with it, 45.5% lost\n"
    "40 years: $45,259.26 without the fee, $20,172.07 with it, 55.4% lost\n"
)


def is_number(x):
    return isinstance(x, (int, float))


def test_the_table():
    """Prints the four lines for $25,000 growing 6% a year with a 0.8% fee."""
    assert run() == TABLE


def test_other_numbers():
    """Works for other numbers: $1,000 growing 10% a year with a 2% fee."""
    assert run_with({"start": 1000, "growth": 0.1, "fee": 0.02}) == OTHER_TABLE


def test_final_amount():
    """final_amount(1000, 0.1, 0.01, 2) is about 1185.92, and with no fee about 1210.00."""
    final_amount = function("final_amount")
    with_fee = final_amount(1000, 0.1, 0.01, 2)
    without = final_amount(1000, 0.1, 0, 2)
    assert is_number(with_fee) and abs(with_fee - 1185.921) < 0.005
    assert is_number(without) and abs(without - 1210.0) < 0.005


def test_share_lost():
    """share_lost(500, 0.07, 0.02, 10) is about 0.1829."""
    share_lost = function("share_lost")
    got = share_lost(500, 0.07, 0.02, 10)
    assert is_number(got) and abs(got - 0.182927) < 1e-5
