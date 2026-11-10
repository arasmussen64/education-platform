from checks import run


def test_the_walkthrough():
    """Prints the four Fibonacci lines, the edit distance with its table and edits, and the knapsack against greedy."""
    assert run() == "fib_plain(25) = 75025 after 242785 calls\nfib_memo(25) = 75025 after 49 calls\nfib_cached(25) = 75025 CacheInfo(hits=23, misses=26, maxsize=None, currsize=26)\nfib_bottom_up(90) = 2880067194370816120\nkitten -> sitting: 3 edits\n 0  1  2  3  4  5  6  7\n 1  1  2  3  4  5  6  7\n 2  2  1  2  3  4  5  6\n 3  3  2  1  2  3  4  5\n 4  4  3  2  1  2  3  4\n 5  5  4  3  2  2  3  4\n 6  6  5  4  3  3  2  3\n['substitute k with s', 'substitute e with i', 'insert g']\nknapsack of 9: (150, ['stove', 'water', 'book'])\ngreedy by value: ['water', 'tent'] worth 130\n"
