import math


def portfolio_volatility(w, vol_a, vol_b, corr):
    return w * vol_a + (1 - w) * vol_b


def lowest_risk_mix(vol_a, vol_b, corr):
    best_w = 0.0
    best_vol = portfolio_volatility(0.0, vol_a, vol_b, corr)
    for i in range(101):
        w = i / 100
        vol = portfolio_volatility(w, vol_a, vol_b, corr)
        if vol < best_vol:
            best_w = w
            best_vol = vol
    return best_w, best_vol


vol_a = 0.18
vol_b = 0.08
corr = 0.2

for i in range(0, 101, 10):
    w = i / 100
    print(f"{w:.0%} in A: {portfolio_volatility(w, vol_a, vol_b, corr):.2%}")
w, vol = lowest_risk_mix(vol_a, vol_b, corr)
print(f"Lowest risk: {w:.0%} in A, volatility {vol:.2%}")
