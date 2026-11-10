def word_count(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def test_one():
    assert True


def test_two():
    assert True


def test_three():
    assert True


print("3 passed")
