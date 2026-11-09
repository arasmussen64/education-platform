def longest_line(path):
    """Return the longest line in the file, without its line break."""
    longest = ""
    with open(path) as f:
        for line in f:
            text = line.rstrip("\n")
            if len(text) > len(longest):
                longest = text
    return longest
