calls = 0


def counted(func):
    def wrapper(*args):
        global calls
        calls = calls + 1
        wrapper.count = calls
        return func(*args)

    wrapper.count = 0
    return wrapper


@counted
def square(x):
    return x * x


print(square(3))
print(square(4))
print(square.count)
