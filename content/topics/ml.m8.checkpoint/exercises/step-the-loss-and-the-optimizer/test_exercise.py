import numpy as np

from checks import function, run


def test_the_output():
    """Prints the loss, the gradient row and the decayed weights."""
    printed = run()
    assert printed == '0.4228 [0.1111, -0.2222, 0.1111]\n[1.7, -0.7, 0.2]\n', f"Your program printed:\n{printed}"


def test_by_hand():
    """The gradient is probabilities minus one-hot over the batch; a decay of zero leaves an undefended weight alone."""
    SoftmaxCrossEntropy = function("SoftmaxCrossEntropy")
    Adam = function("Adam")
    loss = SoftmaxCrossEntropy()
    logits = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 5.0]])
    labels = np.array([2, 0])
    loss.forward(logits, labels)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    onehot = np.zeros_like(probs)
    onehot[np.arange(2), labels] = 1
    assert np.allclose(loss.backward(), (probs - onehot) / 2)
    still = np.array([2.0, -1.0])
    Adam(0.1).step([still], [np.zeros(2)])
    assert np.allclose(still, [2.0, -1.0])
