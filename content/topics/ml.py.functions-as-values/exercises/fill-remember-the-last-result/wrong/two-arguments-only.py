def remember(func):
    def wrapper(greeting, name):
        result = func(greeting, name)
        wrapper.last = result
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
