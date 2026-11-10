def word_count(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def test_mixed_case_counts_as_one_word():
    assert word_count("the cat and The dog") == {"the": 2, "cat": 1, "and": 1, "dog": 1}


def test_a_repeated_word_is_counted():
    assert word_count("a a a") == {"a": 3}


def test_empty_text_gives_an_empty_dict():
    assert word_count("") == {}

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
