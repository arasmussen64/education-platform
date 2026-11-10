from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_fit():
    """Prints the slope and intercept of the best line through the given points."""
    assert run() == "slope 2.0\nintercept 1.0\n"


def test_predict_and_error():
    """predict gives m * x + b, and error is the mean of the squared misses."""
    predict = function("predict")
    error = function("error")
    assert predict(2, 1, 3) == 7
    assert error(2, 1, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == 0.0
    assert error(0, 0, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == 57.0


def test_fit_other_data():
    """fit finds other lines too, including one that slopes down."""
    fit = function("fit")
    assert [round(v, 2) for v in fit([1, 2, 3, 4, 5], [1, 4, 7, 10, 13], 0.05, 2000)] == [3.0, -2.0]
    assert [round(v, 2) for v in fit([1, 2, 3, 4, 5], [30, 28, 26, 24, 22], 0.05, 2000)] == [-2.0, 32.0]
