import math
import struct

import numpy as np

print(0.1 + 0.2 == 0.3, 0.1 + 0.2, f"{0.1:.20f}")

bits = struct.unpack(">I", struct.pack(">f", 0.1))[0]
pattern = f"{bits:032b}"
sign, exponent, mantissa = pattern[0], pattern[1:9], pattern[9:]
print("0.1 as float32:", sign, exponent, mantissa)
print("exponent", int(exponent, 2), "- 127 =", int(exponent, 2) - 127, "| mantissa 1 +", int(mantissa, 2), "/ 2**23")
print("which is", float(np.float32(0.1)))

print("epsilon: float32", float(np.finfo(np.float32).eps), "float64", np.finfo(np.float64).eps)
print("16777216 + 1 in float32:", float(np.float32(16777216) + np.float32(1)), "| in float64:", 16777216.0 + 1.0)
print("isclose:", math.isclose(0.1 + 0.2, 0.3), "| allclose:", np.allclose([0.1 + 0.2], [0.3]))

tenths = [0.1] * 10
total = 0.0
for tenth in tenths:
    total += tenth
print("ten tenths, one at a time:", total, "| sum():", sum(tenths), "| fsum:", math.fsum(tenths), "| 0.1 * 10:", 0.1 * 10)

total = np.float32(0)
for _ in range(100_000):
    total += np.float32(0.1)
print("100,000 tenths in float32, one at a time:", float(total))
print("the same with np.sum (pairwise):", float(np.sum(np.full(100_000, 0.1, dtype=np.float32))))

print("overflow:", 1e308 * 10, "| inf - inf:", float("inf") - float("inf"), "| nan == nan:", float("nan") == float("nan"))
logits = np.array([1000.0, 1001.0])
with np.errstate(over="ignore", invalid="ignore"):
    naive = np.exp(logits) / np.exp(logits).sum()
print("naive softmax of [1000, 1001]:", naive)
shifted = np.exp(logits - logits.max())
print("stable softmax:", shifted / shifted.sum(), "| log-sum-exp:", logits.max() + np.log(np.exp(logits - logits.max()).sum()))
