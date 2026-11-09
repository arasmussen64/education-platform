import csv


def read_rows(path):
    """Return the rows of a CSV file as a list of dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def total_amount(rows):
    """Return the total of the amount field."""
    total = 0
    for row in rows:
        total += float(row["amount"])
    return total


def main():
    with open("orders.csv", "w") as f:
        f.write("item,amount\n")
        f.write("pen,2.5\n")
        f.write("book,10\n")
    rows = read_rows("orders.csv")
    print(len(rows))
    print(total_amount(rows))
    print(rows[0]["item"])


if __name__ == "__main__":
    main()
