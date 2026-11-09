def count_letters(text):
    """Return a dictionary of each character (not spaces) to how often it appears."""
    counts = {}
    for ch in text:
        if ch == " ":
            continue
        if ch in counts:
            counts[ch] += 1
        else:
            counts[ch] = 1
    return counts


def most_common(counts):
    """Return the key with the highest count, the first one if two tie."""
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
