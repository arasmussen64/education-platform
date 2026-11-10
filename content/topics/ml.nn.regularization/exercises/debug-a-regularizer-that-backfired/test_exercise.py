import numpy as np

from checks import function, run

EXPECTED = "validation loss at the end: 0.387 | evaluating twice gives the same answer: True\nthe first layer's weights shrank under decay: True | validation accuracy: 0.85\n"


def test_the_output():
    """Prints a repeatable validation loss and shrunken weights."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_pieces():
    """evaluate switches dropout off, and Adam's decay pulls an undefended weight towards zero."""
    Dropout = function("Dropout")
    Sequential = function("Sequential")
    Adam = function("Adam")
    evaluate = function("evaluate")

    class Plain:
        def forward(self, logits, labels):
            return float(logits.sum())

    layer = Dropout(0.5, seed=1)
    net = Sequential([layer])
    X = np.ones((50, 4))
    first = evaluate(net, Plain(), X, np.zeros(50, dtype=int))[0]
    assert first == 200.0 and layer.training is False
    pulled = np.array([1.0, -1.0])
    optimizer = Adam(0.01, weight_decay=0.1)
    for _ in range(30):
        optimizer.step([pulled], [np.zeros(2)])
    assert np.abs(pulled).max() < 1.0
