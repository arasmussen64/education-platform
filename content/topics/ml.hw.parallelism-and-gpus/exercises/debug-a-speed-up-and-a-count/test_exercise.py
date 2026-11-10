from checks import function, run

EXPECTED = '8 workers on 90% parallel work: 4.71x\n1024-cube matmul: 2,147,483,648 FLOPs, 12,582,912 bytes, 170.7 FLOPs per byte\n'


def test_the_output():
    """Prints the right speed-up and the right counts."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_values():
    """Fully parallel work on 4 workers is 4 times; (2, 3) @ (3, 4) in float64 is 48 FLOPs and 208 bytes."""
    amdahl = function("amdahl")
    matmul_cost = function("matmul_cost")
    assert abs(amdahl(1.0, 4) - 4) < 1e-9 and abs(amdahl(0.5, 10**9) - 2) < 1e-6
    assert tuple(matmul_cost(2, 3, 4, 8)) == (48, 208)
