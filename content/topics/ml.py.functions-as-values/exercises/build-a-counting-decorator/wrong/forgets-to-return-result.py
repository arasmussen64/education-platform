def counted(func):
    def wrapper(*args):
        wrapper.count = wrapper.count + 1
        func(*args)

    wrapper.count = 0
    return wrapper


@counted
def square(x):
    return x * x


print(9)
print(16)
print(square.count + 2)
