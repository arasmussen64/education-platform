import numpy as np


# Write max_pool and max_pool_backward here, above the data.


X = np.array([[[2.0, 7.0, 1.0, 0.0], [4.0, 3.0, 5.0, 8.0], [0.0, 1.0, 9.0, 2.0], [6.0, 0.0, 3.0, 3.0]]])
pooled, mask = max_pool(X)
print(pooled[0].tolist())
print(max_pool_backward(mask, np.array([[[1.0, 2.0], [3.0, 4.0]]]))[0].tolist())
