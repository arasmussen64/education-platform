from checks import run


def test_the_walkthrough():
    """Prints the call counts, the doubling test, the int8 column, the drift, the softmax and the model's cost."""
    assert run() == 'the loop: 2,000 calls to distance_squared for 400 rows | vectorized: 0 calls, same labels: True\ndoubling the rows: 4,000 calls, 2.0 times as many: linear in the rows either way; vectorizing changes the constant, not the order\nweekly clicks from an int8 column: [-116, 94, -68, 72] | widened to int64 first: [140, 350, 700, 840]\nmean loss from a float32 running total: 0.099986 | summed in float64: 0.100000\nsoftmax of a logit of 1,000: naive has NaN: True | stable rows sum to 1: True | first row: [0.269, 0.731]\nthe model the pipeline feeds, layers [4, 64, 32, 5]: 2,565 parameters, 6,156,000 FLOPs to train on the 400 rows, 54,480 bytes of state and activations at a batch of 32\n'
