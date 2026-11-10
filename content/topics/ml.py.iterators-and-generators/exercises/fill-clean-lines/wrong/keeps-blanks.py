text = "alpha\n\n  beta  \ngamma\n"


def clean_lines(text):
    for line in text.split("\n"):
        stripped = line.strip()
        if True:
            yield stripped


print(list(clean_lines(text)))
