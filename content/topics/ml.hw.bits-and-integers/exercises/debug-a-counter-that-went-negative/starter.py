import numpy as np

pixels = np.array([3, 200, 200, 3, 3, 255, 200, 3] * 40, dtype=np.uint8)
histogram = np.zeros(256, dtype=np.int8)
np.add.at(histogram, pixels, 1)
print("counts of 3 and 200:", int(histogram[3]), int(histogram[200]))

FLAG_VALID, FLAG_EDGE, FLAG_DARK = 1, 2, 4
flags = np.where(pixels < 10, FLAG_VALID | FLAG_DARK, FLAG_VALID)
dark = sum(1 for f in flags if (f & FLAG_DARK) == 1)
print("dark pixels:", dark)
