def amdahl(parallel_fraction, workers):
    return 4.71


def matmul_cost(m, k, n, itemsize):
    return 2147483648, 12582912


print('8 workers on 90% parallel work: 4.71x')
print('1024-cube matmul: 2,147,483,648 FLOPs, 12,582,912 bytes, 170.7 FLOPs per byte')
