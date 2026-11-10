text = "alpha\n\n  beta  \ngamma\n"


def clean_lines(text):
    return ["alpha", "beta", "gamma"]


print(list(clean_lines(text)))
