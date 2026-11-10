import time

import numpy as np

rng = np.random.default_rng(0)
X = rng.standard_normal((2000, 8))
w = rng.standard_normal(8)


def predict_loop(X, w):
    """One row at a time, one element at a time: what every Python loop over an array does."""
    out = []
    for row in X:
        total = 0.0
        for x, weight in zip(row, w):
            total += x * weight
        out.append(total)
    return np.array(out)


def predict_vectorized(X, w):
    return X @ w


print("the loop and X @ w agree:", np.allclose(predict_loop(X, w), predict_vectorized(X, w)))

stretched = np.broadcast_to(w, X.shape)
print("w stretched to", stretched.shape, "has strides", stretched.strides, "| (X * w).sum(axis=1) agrees with X @ w:", np.allclose((X * w).sum(axis=1), X @ w))
print(f"the loop asks the interpreter for {X.size:,} multiplications and {X.size:,} additions, one at a time; X @ w asks once")


def seconds(function, *args, repeats=1):
    start = time.perf_counter()
    for _ in range(repeats):
        function(*args)
    return (time.perf_counter() - start) / repeats


def ratio(a, b):
    return f"{a / b:.1f}" if b > 0 else "n/a"


double = np.vstack([X, X])
loop_small, loop_double = seconds(predict_loop, X, w), seconds(predict_loop, double, w)
fast_small, fast_double = seconds(predict_vectorized, X, w, repeats=200), seconds(predict_vectorized, double, w, repeats=200)
print(f"loop: {loop_small * 1000:.1f} ms for 2,000 rows, {loop_double * 1000:.1f} ms for 4,000; ratio {ratio(loop_double, loop_small)}")
print(f"X @ w: {fast_small * 1000:.3f} ms for 2,000 rows, {fast_double * 1000:.3f} ms for 4,000; ratio {ratio(fast_double, fast_small)}")
print(f"at 4,000 rows the vectorized form is {ratio(loop_double, fast_double)} times faster")


def moving_average(X, alpha):
    """Each row's state depends on the row before, so the rows stay a loop; the 8 columns are one vector operation."""
    state = np.zeros(X.shape[1])
    out = np.empty_like(X)
    for t in range(len(X)):
        state = alpha * X[t] + (1 - alpha) * state
        out[t] = state
    return out


smoothed = moving_average(X, 0.1)
print(f"the moving average: {len(X):,} steps that each need the last, so {len(X):,} vector operations instead of {X.size:,} scalar ones")
print("a running total has a library form, np.cumsum:", np.allclose(np.cumsum(X[:, 0]), [X[: t + 1, 0].sum() for t in range(len(X))]))
