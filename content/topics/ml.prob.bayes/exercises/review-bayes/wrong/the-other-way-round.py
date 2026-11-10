def bayes(prior, likelihood_if_true, likelihood_if_false):
    return likelihood_if_true


print(round(bayes(0.01, 0.95, 0.10), 3))
print(round(bayes(0.3, 0.8, 0.2), 3))
