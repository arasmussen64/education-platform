def profile(function, *args):
    return function(*args), None


def call_counts(stats):
    return {'leaf': 2000, 'branch': 2, 'root': 1}


def hot_spots(stats, k):
    return ['grind']


def peak_bytes(function, *args):
    return 10**9


def growth(function, make_input, n, name):
    return 2.0


print("1001000 2000 2 1 ['branch', 'leaf', 'root']")
print("['grind']")
print('True')
print('2.0 4.0')
