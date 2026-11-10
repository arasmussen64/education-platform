from checks import function, run

EXPECTED = '6\na d b c f e\n'


def test_the_output():
    """Prints 6 and the jobs in arrival order."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_jobs():
    """Nested parts are counted once each and run in queue order; an empty list holds no jobs."""
    count_jobs = function("count_jobs")
    run_all = function("run_all")
    assert count_jobs([[], ["q"]]) == 1 and count_jobs("x") == 1
    assert run_all(["x", ["y", ["z"]], "w"]) == ["x", "w", "y", "z"]
