scores = {"Ada": 72, "Bob": 45, "Cy": 50}
results = {name: "pass" if score >= 50 else "fail" for name, score in scores.items()}
print(results)
