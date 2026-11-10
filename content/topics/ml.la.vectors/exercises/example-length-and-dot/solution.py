import numpy as np

v = np.array([3.0, 4.0])
print(np.sqrt(np.sum(v * v)))
print(np.linalg.norm(v))
unit = v / np.linalg.norm(v)
print(unit)
print(np.linalg.norm(unit))

w = np.array([4.0, 3.0])
print(v @ w)
cos = (v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))
print(cos)
print(round(float(np.degrees(np.arccos(cos))), 2))

right = np.array([1.0, 0.0])
up = np.array([0.0, 1.0])
print(v @ right, v @ up)
print(right @ up)
