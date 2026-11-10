import numpy as np

prevalence = 0.01
sensitivity = 0.95
specificity = 0.90

people = 100000
sick = people * prevalence
healthy = people - sick
true_positives = sick * sensitivity
false_positives = healthy * (1 - specificity)
print(round(true_positives), round(false_positives))
print(round(true_positives / (true_positives + false_positives), 3))

evidence = prevalence * sensitivity + (1 - prevalence) * (1 - specificity)
posterior = prevalence * sensitivity / evidence
print(round(posterior, 3))

prior = posterior
evidence = prior * sensitivity + (1 - prior) * (1 - specificity)
print(round(prior * sensitivity / evidence, 3))

rng = np.random.default_rng(4)
has = rng.random(people) < prevalence
positive = np.where(has, rng.random(people) < sensitivity, rng.random(people) < 1 - specificity)
print(round(float(has[positive].mean()), 3))

biases = np.linspace(0, 1, 11)
belief = np.full(11, 1 / 11)
for flip in [1, 1, 0, 1, 1, 1, 0, 1]:
    likelihood = np.where(flip == 1, biases, 1 - biases)
    belief = belief * likelihood / (belief * likelihood).sum()
print(np.round(belief, 3))
print(round(float(biases[belief.argmax()]), 1))
