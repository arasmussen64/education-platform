import numpy as np

heads, flips = 6, 8
ps = np.linspace(0.01, 0.99, 99)
likelihood = ps**heads * (1 - ps) ** (flips - heads)
print(round(float(ps[likelihood.argmax()]), 2), round(float(likelihood.max()), 5))
log_likelihood = heads * np.log(ps) + (flips - heads) * np.log(1 - ps)
print(round(float(ps[log_likelihood.argmax()]), 2), heads / flips)

p = 0.5
for step in range(200):
    slope = heads / p - (flips - heads) / (1 - p)
    p = p + 0.01 * slope
print(round(p, 4))

rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)
mus = np.linspace(165, 175, 101)
ll = np.array([-((x - mu) ** 2).sum() / (2 * 10**2) for mu in mus])
print(round(float(mus[ll.argmax()]), 1), round(float(x.mean()), 1))
print(round(float(np.sqrt(((x - x.mean()) ** 2).mean())), 2), round(float(x.std()), 2))

y = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
print(round(float(np.prod(np.where(y == 1, p_hat, 1 - p_hat))), 4))
print(round(float(-np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat))), 4), round(-np.log(0.3024), 4))
