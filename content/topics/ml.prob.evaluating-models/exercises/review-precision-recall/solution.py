def precision_recall(tp, fp, fn):
    return tp / (tp + fp), tp / (tp + fn)


print(precision_recall(8, 2, 4))
print(precision_recall(30, 0, 70))
