from checks import run


def test_the_walkthrough():
    """Prints the bracket checks, the queue counts, the countdown's frames, the flattened nest and the deep nest's two outcomes."""
    assert run() == "'([]{})' True\n'([)]' False\n'((' False\n'f(x[0]) + g({})' True\n2000 pops: the list moved 1999000 elements; the deque took 2000 steps\nstart 2\n  start 1\n    start 0\n    end 0\n  end 1\nend 2\n[1, 2, 3, 4, 5, 6] [1, 2, 3, 4, 5, 6]\n5000 levels with a stack: 5000 numbers\n5000 levels by recursion: RecursionError\n"
