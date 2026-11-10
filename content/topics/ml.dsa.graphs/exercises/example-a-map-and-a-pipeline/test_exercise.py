from checks import run


def test_the_walkthrough():
    """Prints the neighbours, the hops and fewest-roads path, the distances and cheapest path, the pipeline order and its cycle, and the two passes."""
    assert run() == "neighbours of C: {'A': 2, 'B': 5, 'E': 3}\nhops from A: {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3}\nfewest roads A to F: ['A', 'B', 'D', 'F']\nkm from A: {'A': 0, 'B': 4, 'C': 2, 'E': 5, 'D': 9, 'F': 20}\ncheapest A to F: ['A', 'C', 'E', 'D', 'F'] at 20 km\npipeline order: ['load', 'clean', 'features', 'report', 'train', 'evaluate']\nafter evaluate -> clean: the graph has a cycle\nforward pass: ['x', 'w', 'b', 'y', 'times', 'plus', 'minus', 'square']\nbackward pass: ['square', 'minus', 'plus', 'times', 'y', 'b', 'w', 'x']\n"
