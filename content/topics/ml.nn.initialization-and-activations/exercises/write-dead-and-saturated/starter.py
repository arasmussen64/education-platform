import numpy as np


# Write dead_fraction and saturated_fraction here, above the data.


H = np.array([[0.0, 1.5, 0.0, 2.0], [0.0, 0.0, 0.0, 0.5], [0.0, 3.0, 0.0, 0.0]])
Z = np.array([[5.0, -1.0, 0.5, -6.0], [3.9, 4.1, -4.0, 10.0]])
print(dead_fraction(H), saturated_fraction(Z), saturated_fraction(Z, threshold=3.0))
