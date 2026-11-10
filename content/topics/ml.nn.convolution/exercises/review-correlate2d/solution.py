import numpy as np


def correlate2d(image, kernel):
    """Slide the kernel over the image; each output cell is the sum of the kernel times the patch under it."""
    k = kernel.shape[0]
    h_out, w_out = image.shape[0] - k + 1, image.shape[1] - k + 1
    out = np.zeros((h_out, w_out))
    for y in range(h_out):
        for x in range(w_out):
            out[y, x] = (image[y : y + k, x : x + k] * kernel).sum()
    return out


image = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]])
print(correlate2d(image, np.array([[1.0, -1.0], [1.0, -1.0]])).tolist())
print(correlate2d(image, np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])).tolist())
