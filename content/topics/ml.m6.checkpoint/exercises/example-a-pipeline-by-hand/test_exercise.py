from checks import run


def test_the_walkthrough():
    """Prints the five lines of the tiny pipeline."""
    assert run() == "4 readings, 3 sensors\n['s1', 's3']\n[('s1', 'lab'), ('s3', 'hall')]\n3 ('hall', 1)\n['read', 'calibrate', 'store', 'plot']\n"
