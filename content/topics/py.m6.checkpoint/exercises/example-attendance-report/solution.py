# Spec: Attendance is kept in a CSV with the columns date,class,present. Some
# rows are bad: present is blank or isn't a whole number. Skip and count them,
# total the students present per class, write the report to a file and print
# it. Lines: one per class like "math: 52", then Rows, Bad rows and Total.
#
# Examples: rows math 25, art 18, math x, math 27 -> math: 52, art: 18,
# Rows: 4, Bad rows: 1, Total: 70. No rows at all -> Rows: 0, Bad rows: 0,
# Total: 0.
import csv


def write_sample(path):
    """Write the sample attendance file."""
    with open(path, "w") as f:
        f.write("date,class,present\n")
        f.write("2026-03-02,math,25\n")
        f.write("2026-03-02,art,18\n")
        f.write("2026-03-03,math,x\n")
        f.write("2026-03-03,math,27\n")


# Reading, and deciding which rows are good
def read_rows(path):
    """Return the rows of a CSV file as a list of dictionaries."""
    with open(path) as f:
        return list(csv.DictReader(f))


def present_in(row):
    """Return the row's present count as a whole number, or None if it isn't one."""
    try:
        return int(row["present"])
    except ValueError:
        return None


def good_rows(rows):
    """Return the rows whose present count is a number, in order."""
    good = []
    for row in rows:
        if present_in(row) is not None:
            good.append(row)
    return good


# Totals by class
def totals_by_class(rows):
    """Return a dictionary of class to students present, over the good rows."""
    totals = {}
    for row in good_rows(rows):
        name = row["class"]
        totals[name] = totals.get(name, 0) + present_in(row)
    return totals


# The report, as lines, and writing it
def report_lines(rows):
    """Return a line per class, then Rows, Bad rows and Total."""
    totals = totals_by_class(rows)
    lines = []
    total = 0
    for name in totals:
        lines.append(f"{name}: {totals[name]}")
        total += totals[name]
    lines.append(f"Rows: {len(rows)}")
    lines.append(f"Bad rows: {len(rows) - len(good_rows(rows))}")
    lines.append(f"Total: {total}")
    return lines


def write_report(path, lines):
    """Write the lines to the file, one per line, replacing what was there."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


# Tests, then the program
def test_attendance():
    rows = [
        {"date": "d", "class": "math", "present": "25"},
        {"date": "d", "class": "math", "present": "x"},
        {"date": "d", "class": "art", "present": ""},
        {"date": "d", "class": "math", "present": "27"},
    ]
    assert present_in(rows[0]) == 25
    assert present_in(rows[1]) is None
    assert present_in(rows[2]) is None
    assert len(good_rows(rows)) == 2
    assert totals_by_class(rows) == {"math": 52}
    assert report_lines(rows) == ["math: 52", "Rows: 4", "Bad rows: 2", "Total: 52"]
    print("attendance: all checks passed")


def main():
    """Write the sample, read it, write the report and print it."""
    write_sample("attendance.csv")
    rows = read_rows("attendance.csv")
    lines = report_lines(rows)
    write_report("attendance.txt", lines)
    for line in lines:
        print(line)


if __name__ == "__main__":
    test_attendance()
    main()
