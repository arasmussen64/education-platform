import csv


def write_sample(path):
    """Write a small CSV file to work with."""
    with open(path, "w") as f:
        f.write("name,city,age\n")
        f.write("Ada,London,36\n")
        f.write("Bob,Leeds,41\n")


def main():
    write_sample("people.csv")
    total_age = 0
    with open("people.csv") as f:
        for row in csv.DictReader(f):
            print(f"{row['name']} lives in {row['city']}")
            total_age += int(row["age"])
    print(f"Total age: {total_age}")


if __name__ == "__main__":
    main()
