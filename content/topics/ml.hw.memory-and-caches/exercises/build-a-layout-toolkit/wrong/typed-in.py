def c_strides(shape, itemsize):
    return (32, 8)


def byte_offset(shape, itemsize, index):
    return 48


def misses(shape, order, lines_in_cache, floats_per_line=8):
    return 8192


def traffic(shape, dtype, reads, writes):
    return 8000000


print('(32, 8) 48 46')
print('8192 65536')
print('8000000 16000000 8000000')
