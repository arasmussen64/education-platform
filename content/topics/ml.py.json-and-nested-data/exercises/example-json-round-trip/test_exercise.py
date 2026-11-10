from checks import run


def test_the_walkthrough():
    """Prints the JSON text, str, True, 17, the true/null line, math and no email."""
    assert run() == (
        '{"name": "Ada", "tags": ["math", "code"], "scores": {"quiz": 9, "exam": 17}}\n'
        "str\nTrue\n17\n"
        '{"ok": true, "missing": null}\n'
        "math\nno email\n"
    )
