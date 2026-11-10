import math

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

SPAM = ["buy now", "buy cheap now"]
HAM = ["see you now", "see you soon"]


def test_the_output():
    """Prints the two word probabilities and four classifications."""
    assert run() == 'P(cash | spam) 0.154 P(cash | ham) 0.071\nwin cash: 0.874\nlunch at noon: 0.034\ncash at noon: 0.172\nhello: 0.5\n'


def test_smoothed_probabilities():
    """With add-one smoothing, 'buy' under spam is (2 + 1) / (5 + 6) and under ham (0 + 1) / (6 + 6)."""
    train = function("train")
    probs, prior = train(SPAM, HAM)
    assert abs(probs["spam"]["buy"] - 3 / 11) < 1e-12
    assert abs(probs["ham"]["buy"] - 1 / 12) < 1e-12
    assert prior == {"spam": 0.5, "ham": 0.5}
    assert abs(sum(probs["spam"].values()) - 1) < 1e-12


def test_classify():
    """A message of unknown words gets the prior; spam words push the probability up, ham words down; a word seen in one class only doesn't crash."""
    train = function("train")
    classify = function("classify")
    probs, prior = train(SPAM, HAM)
    assert abs(classify("hello there", probs, prior) - 0.5) < 1e-12
    assert classify("buy cheap", probs, prior) > 0.8
    assert classify("see you", probs, prior) < 0.2
    assert 0 < classify("cheap soon", probs, prior) < 1


def test_unequal_priors():
    """With three spam messages to one ham, an unknown message is spam with probability 0.75."""
    train = function("train")
    classify = function("classify")
    probs, prior = train(["a b", "c d", "e f"], ["g h"])
    assert abs(classify("zzz", probs, prior) - 0.75) < 1e-12
