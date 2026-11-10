def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + fn)
    recall = tp / (tp + fp)
    f1 = 2 * precision * recall / (precision + recall)
    return round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3)


print(metrics(8, 2, 4, 86))
print(metrics(30, 0, 70, 100))
print(metrics(100, 100, 0, 0))
