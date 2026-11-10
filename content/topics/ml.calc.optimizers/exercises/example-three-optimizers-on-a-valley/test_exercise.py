from checks import run


def test_the_walkthrough():
    """Prints plain descent's and momentum's losses, three points of a zigzag, a diverging rate, a fixed rate against a decayed one, Adam's losses and Adam's first step."""
    assert run() == "plain [81.7907, 36.6032, 13.398, 1.7951]\nmomentum [41.6475, 0.5882, 0.0009, 0.0]\n[[ 9.82  -0.8  ]\n [ 9.643  0.64 ]\n [ 9.47  -0.512]]\nrate 0.015 104857654.4\nfixed 0.01 [166.7608, 113.262, 101.7588, 100.0309]\ndecayed 0.01 [166.7608, 113.262, 101.7588, 0.2356]\nadam [62.1484, 0.235, 0.0029, 0.0]\nadam's first step [9.7 0.7]\n"
