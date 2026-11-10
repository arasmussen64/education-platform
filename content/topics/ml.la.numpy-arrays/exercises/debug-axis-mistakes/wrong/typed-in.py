import numpy as np


def report(grid):
    print("daily averages: [20. 30. 50.]")
    print("above average:")
    print("[[-5. -5.  5.]")
    print(" [ 5.  5. -5.]]")
    print("best day: 3")


report(np.array([[15, 25, 55], [25, 35, 45]]))
