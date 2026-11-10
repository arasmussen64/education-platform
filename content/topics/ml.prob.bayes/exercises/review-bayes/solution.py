def bayes(prior, likelihood_if_true, likelihood_if_false):
    evidence = prior * likelihood_if_true + (1 - prior) * likelihood_if_false
    return prior * likelihood_if_true / evidence


print(round(bayes(0.01, 0.95, 0.10), 3))
print(round(bayes(0.3, 0.8, 0.2), 3))
