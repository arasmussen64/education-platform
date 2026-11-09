def longest_line(path):
    """Return the longest line in the file, without its line break."""
    longest = ""
    with open(path) as f:
        for line in f:
            if len(line) > len(longest):
                longest = line
    return longest
