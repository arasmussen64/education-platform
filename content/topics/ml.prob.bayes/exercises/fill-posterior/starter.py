def posterior(prior, likelihood_if_true, likelihood_if_false):
    """The chance it's true after seeing evidence that happens with chance
    likelihood_if_true when it's true and likelihood_if_false when it isn't."""
    evidence = prior * likelihood_if_true + (1 - ...) * ...
    return prior * likelihood_if_true / evidence


print(round(posterior(0.01, 0.95, 0.10), 3))
print(round(posterior(0.088, 0.95, 0.10), 3))
print(round(posterior(0.5, 0.95, 0.10), 3))
print(round(posterior(0.01, 0.95, 0.01), 3))
