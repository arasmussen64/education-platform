def remember(func):
    def wrapper(...):
        result = func(...)
        wrapper.last = ...
        return result

    wrapper.last = None
    return ...


@remember
def greet(greeting, name):
    return f"{greeting}, {name}"


print(greet.last)
print(greet("Hello", "Ada"))
print(greet("Bye", "Bob"))
print(greet.last)
