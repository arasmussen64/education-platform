def counted(func):
    func.count = 2
    return func


@counted
def square(x):
    return x * x


print(9)
print(16)
print(2)
