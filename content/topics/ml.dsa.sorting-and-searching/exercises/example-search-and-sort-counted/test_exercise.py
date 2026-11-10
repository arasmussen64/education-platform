from checks import run


def test_the_walkthrough():
    """Prints the search counts, the sort counts, the keyed sorts, the bands and the argsort order."""
    assert run() == "scan: found at 999999 and missing is -1 after 2000000 comparisons\nbinary search: found at 999999 and missing is -1 after 40 comparisons\n1000 shuffled items: {'insertion': 250099, 'merge': 8705}\n2000 shuffled items: {'insertion': 1020332, 'merge': 19362}\n2000 already sorted items: insertion 1999\n[('Lima', 12), ('Lima', 41), ('Oslo', 30), ('Oslo', 8), ('Pune', 19)]\n[('Lima', 41), ('Lima', 12), ('Oslo', 30), ('Oslo', 8), ('Pune', 19)]\n49 is in band 0\n65 is in band 2\n79 is in band 2\n95 is in band 4\n[1 3 0 2] ['bob' 'dee' 'ann' 'cy']\n"
