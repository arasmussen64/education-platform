# The data: one record per item
ITEMS = [
    {"name": "pens", "quantity": 40, "price": 1.5},
    {"name": "notebooks", "quantity": 5, "price": 4.0},
    {"name": "staplers", "quantity": 0, "price": 12.0},
]


# A number from a record, and a word from a number
def value(item):
    """Return the total value of an item's stock."""
    return item["quantity"] * item["price"]


def status(quantity):
    """Return out for none, low for 5 or fewer, otherwise ok."""
    if quantity == 0:
        return "out"
    if quantity <= 5:
        return "low"
    return "ok"


# The best record
def most_valuable(items):
    """Return the name of the item with the highest stock value, the first if two tie."""
    best = items[0]
    for item in items:
        if value(item) > value(best):
            best = item
    return best["name"]


# The report, as lines of text
def report_lines(items):
    """Return one line per item, like 'pens: $60.00 (ok)', then the most valuable."""
    lines = []
    for item in items:
        lines.append(f"{item['name']}: ${value(item):.2f} ({status(item['quantity'])})")
    lines.append(f"Most valuable: {most_valuable(items)}")
    return lines


# The tests
def test_inventory():
    assert value({"name": "x", "quantity": 2, "price": 1.5}) == 3.0
    assert status(0) == "out"
    assert status(5) == "low"
    assert status(6) == "ok"
    assert most_valuable(ITEMS) == "pens"
    assert report_lines(ITEMS)[0] == "pens: $60.00 (ok)"
    print("inventory: all checks passed")


# The program
def main():
    """Print the report."""
    for line in report_lines(ITEMS):
        print(line)


if __name__ == "__main__":
    test_inventory()
    main()
