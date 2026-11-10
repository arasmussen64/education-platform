from checks import run


def test_the_walkthrough():
    """Prints the neuron, the layer, the shapes, the count, the collapse and the boundary."""
    assert run() == "one neuron: z = 0.5 * 1 + -0.25 * 2 + 0.1 = 0.1 | relu(z) = 0.1\na layer of 3 neurons on one input: z = [0.1, -0.3, 0.5] | relu: [0.1, 0.0, 0.5]\nthe same layer on a batch of 4 rows: (4, 3) | row 0 is the single input's answer: [0.1, -0.3, 0.5]\ninput (8, 35) | Dense -> (8, 16) | ReLU -> (8, 16) | Dense -> (8, 10)\nparameters: 746 = 35 * 16 + 16 + 16 * 10 + 10\ntwo Dense layers with nothing between equal one Dense: True | with a ReLU between: False\na neuron with w = [1, 1] and b = -1.5 fires where x + y > 1.5: [False, True, True, True, False]\n"
