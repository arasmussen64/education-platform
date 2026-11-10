import numpy as np

a = np.array([1.5, 2.0, 3.5])
print(a)
print(a.shape, a.dtype)

grid = np.array([[1, 2, 3], [4, 5, 6]])
print(grid.shape)
print(grid[1, 2])
print(grid[:, 0])

print(a * 2)
print(grid + np.array([10, 20, 30]))
print(grid.sum(axis=0))
print(grid.mean(axis=1))

print(np.arange(5))
print(np.linspace(0, 1, 5))
