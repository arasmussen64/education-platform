def table(people, prevalence, sensitivity, specificity):
    sick = people * prevalence
    healthy = people - sick
    true_positives = sick * sensitivity
    false_positives = healthy * (1 - specificity)
    return true_positives, false_positives


def chance_if_positive(prior, sensitivity, specificity):
    evidence = prior * sensitivity + (1 - prior) * (1 - specificity)
    return prior * sensitivity / evidence


true_positives, false_positives = table(100000, 0.01, 0.95, 0.90)
print("positives", round(true_positives), round(false_positives))
first = chance_if_positive(0.01, 0.95, 0.90)
print("after one positive", round(first, 3))
second = chance_if_positive(first, 0.95, 0.90)
print("after two positives", round(second, 3))
