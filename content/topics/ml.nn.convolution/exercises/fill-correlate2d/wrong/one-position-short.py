import numpy as np


def correlate2d(image, kernel, padding=0, stride=1):
    """Slide the kernel over the image (padded with zeros by `padding` on every side), moving `stride` pixels at a time; each output cell is the sum of the kernel times the patch under it."""
    if padding:
        image = np.pad(image, padding)
    k = kernel.shape[0]
    h_out = (image.shape[0] - k) // stride
    w_out = (image.shape[1] - k) // stride
    out = np.zeros((h_out, w_out))
    for y in range(h_out):
        for x in range(w_out):
            patch = image[y * stride : y * stride + k, x * stride : x * stride + k]
            out[y, x] = (patch * kernel).sum()
    return out


image = (np.arange(36.0).reshape(6, 6) ** 2) % 7
kernel = np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])
print(correlate2d(image, kernel)[0].tolist())
print(correlate2d(image, kernel, padding=1).shape, correlate2d(image, kernel, stride=2).tolist())
