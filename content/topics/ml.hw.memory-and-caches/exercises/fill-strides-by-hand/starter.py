def c_strides(shape, itemsize):
    """The byte strides NumPy uses for a C-order (row-major) array: the last axis steps one item, each earlier axis steps a whole block."""
    strides = []
    step = ...
    for size in reversed(shape):
        strides.append(step)
        step *= ...
    return tuple(reversed(strides))


print(c_strides((3, 4), 8), c_strides((4, 5), 4), c_strides((2, 3, 4), 2))
