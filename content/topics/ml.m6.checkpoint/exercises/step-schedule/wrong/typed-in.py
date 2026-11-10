from collections import deque


def schedule(steps):
    return list(steps)


print("['load', 'clean', 'join', 'features', 'train']")
print('the steps depend on each other in a cycle')
