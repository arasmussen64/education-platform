import numpy as np

rng = np.random.default_rng(5)
correct = (rng.random(200) < 0.84).astype(int)
