def min_coins(coins, amount):
    count = 0
    for coin in sorted(coins, reverse=True):
        count += amount // coin
        amount %= coin
    return count if amount == 0 else -1


print(min_coins([1, 5, 10, 25], 63))
print(min_coins([1, 15, 25], 30))
print(min_coins([4, 7], 10))
