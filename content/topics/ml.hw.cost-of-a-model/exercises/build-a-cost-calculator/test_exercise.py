from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == '235146 469504 84510720000\n4063904 8032000000\n0.0085 0.0282\n121.5\n'


def test_counts_by_hand():
    """[4, 3, 2] is 23 parameters and 36 forward FLOPs; [5, 1] is 6 and 10; [7] is 0 and 0."""
    parameter_count = function("parameter_count")
    forward_flops = function("forward_flops")
    assert parameter_count([4, 3, 2]) == 23 and forward_flops([4, 3, 2]) == 36
    assert parameter_count([5, 1]) == 6 and forward_flops([5, 1]) == 10
    assert parameter_count([7]) == 0 and forward_flops([7]) == 0


def test_training_flops():
    """Three times the forward pass per example, linear in the examples."""
    forward_flops = function("forward_flops")
    training_flops = function("training_flops")
    assert training_flops([4, 3, 2], 1) == 3 * forward_flops([4, 3, 2])
    assert training_flops([10, 20, 5], 200) == 2 * training_flops([10, 20, 5], 100)


def test_bytes():
    """A batch of 0 is 16 bytes per parameter in float32 and 8 in float16; activations add batch times values times bytes."""
    training_bytes = function("training_bytes")
    assert training_bytes(1000, 0, 500, 4) == 16000 and training_bytes(1000, 0, 500, 2) == 8000
    assert training_bytes(1000, 10, 500, 4) == 16000 + 20000


def test_seconds():
    """At full utilization the time is FLOPs over the peak; halving the utilization doubles it."""
    training_seconds = function("training_seconds")
    assert abs(training_seconds(1e12, 1e12, 1.0) - 1.0) < 1e-9
    assert abs(training_seconds(1e12, 1e12, 0.5) - 2.0) < 1e-9
