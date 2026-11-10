from checks import run


def test_the_walkthrough():
    """Prints the line, its residual, the top component with the share kept, and the compression error."""
    assert run() == (
        "line [ 0.8 -0.6]\nline residual 0.894\ntop component [0.772 0.635] kept 0.9836\ncompression error 0.695\n"
    )
