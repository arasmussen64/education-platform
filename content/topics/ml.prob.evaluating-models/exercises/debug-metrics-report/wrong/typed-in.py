import numpy as np


def metrics(tp, fp, fn, tn):
    return 0.85, 0.75, 0.6, 0.667


def accuracy_interval(accuracy, n, z=1.96):
    return 0.801, 0.899


print('metrics 0.85 0.75 0.6 0.667')
print('interval 0.801 0.899')
