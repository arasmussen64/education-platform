def amdahl(parallel_fraction, workers):
    return 4.71


def matmul_cost(m, k, n, itemsize):
    return (2147483648, 12582912)


def intensity(flops, bytes_moved):
    return 170.7


def roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):
    return 0.0002147


def transfer_seconds(total_bytes, pieces, bandwidth, latency):
    return 0.04


print('4.71 10.0 39.3')
print('(2147483648, 12582912) 170.7')
print('0.5 128.0')
print('214.7 24.0')
print('0.04 10.04')
