from checks import run


def test_the_walkthrough():
    """Prints the two walks and the depth, the two search counts, the top five and the heap list, and the three flowers."""
    assert run() == "depth-first: ['root', 'a', 'a1', 'a2', 'b', 'c', 'c1', 'c1x']\nbreadth-first: ['root', 'a', 'b', 'c', 'a1', 'a2', 'c1', 'c1x']\ndepth: 4\nshuffled insert order: finding 999 took 14 comparisons\nsorted insert order: finding 999 took 1000 comparisons\ntop 5 of 10,000: [999873, 999864, 999848, 999742, 999740]\nthe heap list itself: [999740, 999848, 999742, 999864, 999873] (smallest first; the rest is not sorted)\nheapq.nlargest agrees: True\n{'petal_length': 1.4, 'petal_width': 0.2} -> ('setosa', 1)\n{'petal_length': 4.7, 'petal_width': 1.4} -> ('versicolor', 2)\n{'petal_length': 5.9, 'petal_width': 2.1} -> ('virginica', 2)\n"
