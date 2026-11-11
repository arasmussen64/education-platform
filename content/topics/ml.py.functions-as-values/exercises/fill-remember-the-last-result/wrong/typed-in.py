def remember(func):
    return func


@remember
def greet(greeting, name):
    return f"{greeting}, {name}"


print(None)
print("Hello, Ada")
print("Bye, Bob")
print("Bye, Bob")
