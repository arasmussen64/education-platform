scores = {"Ada": 72, "Bob": 91, "Cy": 85}
ranked = sorted(scores, key=lambda name: scores[name], reverse=True)
print(ranked)
print(max(scores, key=lambda name: scores[name]))
