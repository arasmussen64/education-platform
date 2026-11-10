def min_coins(coins, amount):
    """The fewest coins that make the amount, or -1 if none can: a table from 0 up to the amount."""
    best = [0] + [float("inf")] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] + 1 < best[total]:
                best[total] = best[total - coin] + 1
    return best[amount] if best[amount] != float("inf") else -1


print(min_coins([1, 5, 10, 25], 63))
print(min_coins([1, 15, 25], 30))
print(min_coins([4, 7], 10))
