import numpy as np

print(bin(37), hex(255), int("100101", 2), int("ff", 16))
places = " + ".join(str(2 ** (7 - i)) for i, bit in enumerate(f"{37:08b}") if bit == "1")
print(f"{37:08b}", "=", places, "=", 37)

small = np.array([120, 125, 127], dtype=np.int8)
print("int8 + 5:", small + 5)
counts = np.array([250, 255], dtype=np.uint8)
print("uint8 + 1:", counts + 1)
print("Python int:", 2 ** 100)

print("the bits of -1 and -128 in int8:", f"{(-1) & 0xFF:08b}", f"{(-128) & 0xFF:08b}")
print("the same bytes read as unsigned:", np.array([-1, -128, 127], dtype=np.int8).view(np.uint8))

for dtype in ("uint8", "float32", "float64"):
    batch = np.zeros((1000, 784), dtype=dtype)
    print(f"{dtype:>7}: {batch.nbytes:,} bytes for 1,000 images of 784 pixels")

READ, WRITE, EXEC = 1, 2, 4
perms = READ | EXEC
print("perms:", perms, f"{perms:03b}", "can write:", bool(perms & WRITE), "can run:", bool(perms & EXEC))
perms |= WRITE
perms &= ~EXEC
print("after granting write and revoking run:", f"{perms:03b}")
packed = (255 << 16) | (128 << 8) | 7
print("rgb packed:", hex(packed), "green:", (packed >> 8) & 0xFF, "| 1 << 10 =", 1 << 10, "| 1024 >> 3 =", 1024 >> 3)
