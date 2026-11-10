def counted(func):
    def wrapper(*args):
        wrapper.count = wrapper.count + 1
        return func(*args)

    wrapper.count = 0
    return wrapper


@counted
def square(x):
    return x * x


print(square(3))
print(square(4))
print(square.count)
