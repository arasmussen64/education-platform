scores = {"Ada": 72, "Bob": 91, "Cy": 85}
ranked = sorted(scores, key=lambda name: scores[name], reverse=False)
print(ranked)
print(max(scores, key=lambda name: scores[name]))
