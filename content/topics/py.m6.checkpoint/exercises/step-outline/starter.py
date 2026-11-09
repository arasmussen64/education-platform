import csv


# The sample file
def write_sample(path):
    """Write the sample sales file."""
    with open(path, "w") as f:
        f.write("date,region,amount\n")
        f.write("2026-01-03,north,120.50\n")
        f.write("2026-01-03,south,80\n")
        f.write("2026-01-04,north,abc\n")
        f.write("2026-01-04,east,45.25\n")
        f.write("2026-01-05,south,\n")
        f.write("2026-01-05,north,30\n")


# Reading, and deciding which rows are good: read_rows, amount_of, good_rows


# Totals by region: totals_by_region


# The report as lines, and writing it: report_lines, write_report


# The tests: test_report


# The program: main


if __name__ == "__main__":
    test_report()
    main()
