from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_project():
    """Prints Worth today: 189.49."""
    assert run() == "Worth today: 189.49\n"


def test_a_flow_today():
    """A flow at time 0 isn't discounted: [250] is worth 250 at any rate."""
    present_value_of_flows = function("present_value_of_flows")
    assert abs(present_value_of_flows([250], 0.09) - 250) < 0.005


def test_later_flows():
    """[0, 110] at 10% is worth 100, and [-1000, 700, 500] at 10% is worth 49.59."""
    present_value_of_flows = function("present_value_of_flows")
    assert abs(present_value_of_flows([0, 110], 0.1) - 100) < 0.005
    assert abs(present_value_of_flows([-1000, 700, 500], 0.1) - 49.59) < 0.005


def test_no_flows():
    """An empty list is worth 0."""
    present_value_of_flows = function("present_value_of_flows")
    assert abs(present_value_of_flows([], 0.05)) < 0.005


def test_another_list():
    """Works for another list: [-800, 300, 300, 300] at 7% is worth -12.71 today."""
    assert run_with({"flows": [-800, 300, 300, 300]}) == "Worth today: -12.71\n"
