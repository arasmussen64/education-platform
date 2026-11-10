import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the entropies, three beliefs, both KL directions and the loss."""
    assert run() == 'entropy 1.157 uniform of 8 3.0\ncross-entropy 1.157 kl 0.0\ncross-entropy 1.28 kl 0.123\ncross-entropy 1.585 kl 0.428\nkl both ways 0.531 0.737\nloss 0.299\n'


def test_entropies():
    """A fair coin is 1 bit, [0.5, 0.25, 0.25] is 1.5, a certainty is 0 even with zeros in the table, and n equal outcomes give log2 n."""
    entropy = function("entropy")
    surprise = function("surprise")
    assert entropy([0.5, 0.5]) == 1.0 and entropy([0.5, 0.25, 0.25]) == 1.5
    assert entropy([1.0, 0.0, 0.0]) == 0
    assert abs(entropy([1 / 16] * 16) - 4.0) < 1e-12
    assert surprise(0.125) == 3.0


def test_the_inequality_and_kl():
    """Cross-entropy equals the entropy for the right belief, exceeds it otherwise, and kl is their gap, asymmetric."""
    entropy = function("entropy")
    cross_entropy = function("cross_entropy")
    kl = function("kl")
    p, q = [0.2, 0.5, 0.3], [0.4, 0.4, 0.2]
    assert abs(cross_entropy(p, p) - entropy(p)) < 1e-12
    assert cross_entropy(p, q) > entropy(p)
    assert abs(kl(p, q) - (cross_entropy(p, q) - entropy(p))) < 1e-12
    assert kl(p, q) != kl(q, p)


def test_loss_in_nats():
    """The loss matches Module 4's formula, and guessing a half costs ln 2."""
    loss_in_nats = function("loss_in_nats")
    y = np.array([1.0, 0.0, 0.0, 1.0])
    p = np.array([0.6, 0.3, 0.9, 0.95])
    expected = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert abs(loss_in_nats(y, p) - expected) < 1e-12
    assert abs(loss_in_nats(y, np.full(4, 0.5)) - np.log(2)) < 1e-12
