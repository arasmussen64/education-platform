def remember(func):
    def wrapper(*args):
        result = func(*args)
        wrapper.last = args
        return result

    wrapper.last = None
    return wrapper


@remember
def greet(greeting, name):
    return f"{greeting}, {name}"


print(greet.last)
print(greet("Hello", "Ada"))
print(greet("Bye", "Bob"))
print(greet.last)
