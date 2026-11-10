from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_this_sale():
    """Prints the discount, the price after it, the tax and the total for 120, 15% and 8%."""
    assert run() == (
        "Discount: 18.00\nPrice after discount: 102.00\nTax: 8.16\nTotal: 110.16\n"
    )


def test_any_sale():
    """Works for any price, discount and tax: the tax is charged on the discounted price."""
    printed = run_with({"price": 50, "discount_percent": 10, "tax_percent": 20})
    assert printed == (
        "Discount: 5.00\nPrice after discount: 45.00\nTax: 9.00\nTotal: 54.00\n"
    )
