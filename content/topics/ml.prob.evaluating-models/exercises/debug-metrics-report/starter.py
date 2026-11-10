import numpy as np


def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = (precision + recall) / 2
    return accuracy, precision, recall, f1


def accuracy_interval(accuracy, n, z=1.96):
    se = np.sqrt(accuracy * (1 - accuracy)) / n
    return accuracy - z * se, accuracy + z * se


accuracy, precision, recall, f1 = metrics(30, 10, 20, 140)
print("metrics", round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3))
low, high = accuracy_interval(accuracy, 200)
print("interval", round(float(low), 3), round(float(high), 3))
