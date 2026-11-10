stock = {"pens": 12, "ink": 2, "paper": 40, "clips": 3}
plenty = {item: count for item, count in stock.items() if count > 3}
print(plenty)
