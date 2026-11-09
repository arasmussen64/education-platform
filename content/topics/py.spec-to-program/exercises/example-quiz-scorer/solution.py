# Spec: Score a multiple-choice quiz. Given the answer key and a student's
# answers, print the score like "Score: 7/10 (70.0%)", then PASS for 60% or
# more, otherwise FAIL. Missing answers count as wrong; extra ones are ignored.
#
# Examples, from the spec:
#   key ABCD, answers ABCD  -> Score: 4/4 (100.0%)  PASS
#   key ABCD, answers ABDD  -> Score: 3/4 (75.0%)   PASS
#   key ABCD, answers AB    -> Score: 2/4 (50.0%)   FAIL   (missing = wrong)
#   key ABCD, answers ABCDE -> Score: 4/4 (100.0%)  PASS   (extra ignored)
#   exactly 60%             -> PASS                        (the boundary)
# Gap: the spec doesn't say what an empty key means. Decided: 0/0 is 0.0%, FAIL.


# The plan: count_correct -> percent -> verdict, composed by summary
def count_correct(key, answers):
    """Return how many answers match the key, position by position."""
    correct = 0
    for i in range(len(key)):
        if i < len(answers) and answers[i] == key[i]:
            correct += 1
    return correct


def percent(correct, total):
    """Return correct out of total as a percentage, 0.0 when total is 0."""
    if total == 0:
        return 0.0
    return 100 * correct / total


def verdict(percentage):
    """Return PASS for 60% or more, otherwise FAIL."""
    if percentage >= 60:
        return "PASS"
    return "FAIL"


def summary(key, answers):
    """Return the two report lines for one student."""
    correct = count_correct(key, answers)
    pct = percent(correct, len(key))
    return [f"Score: {correct}/{len(key)} ({pct:.1f}%)", verdict(pct)]


# The tests: one assert per example, written before the bodies were
def test_quiz():
    assert count_correct("ABCD", "ABDD") == 3
    assert count_correct("ABCD", "AB") == 2
    assert count_correct("ABCD", "ABCDE") == 4
    assert percent(3, 4) == 75.0
    assert percent(0, 0) == 0.0
    assert verdict(60) == "PASS"
    assert verdict(59.9) == "FAIL"
    assert summary("ABCD", "ABDD") == ["Score: 3/4 (75.0%)", "PASS"]
    print("quiz: all checks passed")


def main():
    """Score one student against the key."""
    for line in summary("ABCDEFGHIJ", "ABCDEFGXYZ"):
        print(line)


if __name__ == "__main__":
    test_quiz()
    main()
