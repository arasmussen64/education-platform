# Write early_stopping here, above the calls.


print(early_stopping([1.0, 0.8, 0.75, 0.9, 0.85, 0.7, 0.72, 0.74, 0.8], patience=3))
print(early_stopping([0.6, 0.5, 0.45, 0.44], patience=2))
print(early_stopping([0.5, 0.5, 0.5, 0.5], patience=2))
