def count_letters(text):
    """Return a dictionary of each character to how often it appears."""
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    return counts


def most_common(counts):
    """Return the key with the highest count."""
    best = None
    for key in counts:
        if best is None or counts[key] > counts[best]:
            best = key
    return best


def main():
    counts = count_letters("banana bread")
    print(f"Counts: {counts}")
    print(f"Most common: {most_common(counts)}")


main()
