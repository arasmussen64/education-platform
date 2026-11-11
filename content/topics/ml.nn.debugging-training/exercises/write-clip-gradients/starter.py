import numpy as np


# Write gradient_norm and clip_gradients here, above the data.


grads = [np.array([[3.0, 0.0], [0.0, 0.0]]), np.array([4.0]), np.array([12.0])]
print(gradient_norm(grads))
clipped = clip_gradients(grads, 6.5)
print([grad.tolist() for grad in clipped], gradient_norm(clipped))
print(clip_gradients(grads, 100.0) is grads)
