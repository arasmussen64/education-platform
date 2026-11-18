# Plan: Finance and Markets, Module 1

The writing plan for Module 1, "Money, time and risk", of the [Finance and Markets track](../../specs/finance-markets.md#module-1-money-time-and-risk), made on 2026-11-17 before any of it was written. The owner asked on 2026-11-17 for this module to be built before the cloud track's Module 4.

**This is a plan, not the source of truth.** Once a topic is written, its files under `content/topics/` are what counts. Where a writer finds that the plan is wrong (a number, a story that doesn't hold, a resource that says something else), the writer fixes the topic and records it in the devlog's Author notes.

## What every topic in this module does

These are the house rules in [content/README.md](../../../content/README.md), plus the choices that keep eleven topics written by several writers consistent.

**Shape.** Each topic is a regular topic in the style of the ML track's math refresher (`content/topics/ml.math.exponents-and-logs` is the model for Python exercises), with everything the cloud topics gained on 2026-11-16 (`content/topics/csa.linux.memory` is the model for those):

- `topic.yaml` with objectives, skills (three or four), resources with licenses, an explain prompt with a rubric and a model answer, `practice:`, `prove:` and `review_pool:`.
- `lesson.mdx`: `<Intro>` opening with a `<Puzzle>`, three or four `<Check>` questions placed in the lesson after the idea each tests, a `<Story>` where a real incident fits, then `<Resource index={0} />` and `<Recap>`.
- `glossary.yaml`: every finance term the topic teaches, three to eight, in plain words.
- Practice ladder: a worked example, a Parsons problem, quick questions (multiple choice, predict the output, at least three estimate items for each calculation skill, two typed items, one contrast question), a fill-in, and a write exercise.
- Proofs: a build (hidden tests, no starter, or a starter holding only the calling lines), a debug (symptoms and a count, never the fault), and the explain.
- A review pool of at least three, at least one where the learner produces the answer.
- Every skill has at least two questions that can come back ([ADR-0011](../../decisions/0011-mistakes-come-back.md)).
- `estimated_minutes` worked out by the README's rule; about 50 to 70 minutes a topic.

**Python the learner already has.** Python Foundations to its end and the ML track's math refresher topics this module names. Nothing from the ML track's Module 2 (no classes, comprehensions or dataclasses), no NumPy and no pandas: plain lists, dictionaries, loops and functions. `math` from the standard library is fine; `random` only with a fixed seed, and never where a test pins the drawn numbers (write the data into the exercise instead).

**Money in code.** One convention for the whole module, said once in the first topic and kept after that:

- A rate is a decimal: 5% is `0.05`. A prompt says "5% a year" and the code holds `0.05`.
- Money is a float and is rounded **only for printing**: `f"{amount:,.2f}"` prints `12,345.68`. The first topic says in one sentence why rounding along the way drifts, and why real banks use whole cents or `decimal`, which this module doesn't need.
- Tests compare money printed to the cent, or a returned float within `0.005`.
- Shared function names, so the checkpoint reads like the topics: `future_value(present, rate, periods)`, `present_value(future, rate, periods)`, `payment(principal, rate, periods)` (rate per period), `effective_annual_rate(apr, per_year)`, `simple_returns(prices)`, `annualized_return(...)`, `volatility(returns)`, `max_drawdown(prices)`.

**Data.** Prices are written into each exercise as short lists: made up, stated as made up, and chosen so the story holds (assert it, per the house rule). Real data is used only where it's public domain: the US Consumer Price Index from the Bureau of Labor Statistics (CPI-U, annual averages), fetched and checked by the writer from bls.gov, with the series id and the date read in the topic. No index levels or price histories from vendors (S&P, Yahoo Finance and the like are licensed).

**Not advice.** Every topic that touches investing has one sentence, in the intro or recap, that the module teaches how these things work and isn't advice on what to do. Never name a fund, a broker or a product as something to buy.

**Resources.** Each topic's first resource is a free reading or course page, fetched and its heading read before it's cited, its license recorded as the source states it. Candidates, to check:

- Investor.gov, the US Securities and Exchange Commission's site for investors (a US government work; check its terms page). Its compound-interest calculator and its pages on fees, diversification, order types and how trades settle fit topics 1, 7, 8, 9 and 10.
- Khan Academy, Finance and capital markets (CC BY-NC-SA 3.0 US, as the other tracks record it; check). Interest and debt, present value, stocks and bonds.
- The Bureau of Labor Statistics' CPI pages (public domain) for topic 4.
- Aswath Damodaran's free lectures and pages at NYU Stern (free to read; record the terms his site states, linked only) for topics 5 and 6.
- FINRA's investor pages for topic 10 (check the terms; link only).

**Incidents.** A `<Story>` is told in our own words with its source linked. Suggested, each to be checked against a primary or well-sourced report before it's used: Enron employees' 401(k) plans heavily in Enron stock (topic 7); the January 2021 GameStop trading restrictions, which brokers put on after the clearing house's deposit demands rose (topic 10, per the SEC staff report of October 2021); the 2010 flash crash (topic 10 or 11, per the SEC and CFTC joint report); payday-loan APRs (topic 4, from the Consumer Financial Protection Bureau's research); a fund's fees over decades (topic 8, from Investor.gov's bulletin on fees). A topic with no true story that fits goes without one.

## The topics

Topic ids, titles and prerequisites are in the [spec's table](../../specs/finance-markets.md#module-1-money-time-and-risk). Below, for each: the skills, the puzzle, what the proofs ask, and what to watch for.

### 1. Compound interest (`fin.money.compounding`)

- **Skills:** `grow-by-loop` (grow an amount period by period in a loop), `grow-by-formula` (the `(1 + r) ** n` formula, and that it matches the loop), `doubling` (the rule of 72 and its exact form with logs), `simple-vs-compound`.
- **Puzzle:** $1,000 at 7% a year for 30 years; simple interest gives $3,100. Guess what compounding gives. (About $7,612.)
- **Build:** `future_value(present, rate, periods)` and a year-by-year table. **Debug:** a savings projector that adds interest on the original amount only, and starts counting at year 1 for the starting balance (two bugs; symptoms: the totals are too low and the table is a row short).
- **Explain:** two friends save the same total, one from 25 to 35 then stops, one from 35 to 65. Why can the first end up with more?
- **Watch:** the ML topic `ml.math.exponents-and-logs` already grows money once; say so in a sentence and go further (tables, doubling, comparing).

### 2. Present and future value (`fin.money.time-value`)

- **Skills:** `discount` (present value of one amount), `compare-offers` (move amounts to the same date before comparing), `uneven-flows` (present value of a list of cash flows, the first at time 0).
- **Puzzle:** $10,000 now or $11,000 in two years, if money earns 6%? (Now: $11,000 is worth about $9,790 today.)
- **Build:** `present_value_of_flows(flows, rate)`. **Debug:** an offer comparer whose discount exponent starts at 1 for the time-0 flow and that compares undiscounted totals in its final line (two bugs).
- **Explain:** why a dollar today is worth more than a dollar next year, with three reasons (it can earn, prices rise, the future is uncertain) and one number.
- **Watch:** this is NPV without the name. The lesson can say "Module 5 calls this net present value" once.

### 3. Loans and annuities (`fin.money.annuities`)

- **Skills:** `annuity-value` (present value of equal payments, by loop and by formula), `payment` (the loan payment formula, monthly rate and number of months), `amortization` (a schedule: interest, principal, balance; the last balance is zero to the cent).
- **Puzzle:** on a 30-year $300,000 mortgage at 6%, how much of the first $1,798.65 payment pays down the loan? (About $298.65; $1,500 is interest.)
- **Build:** an amortization schedule printed by month for a short loan, totals checked. **Debug:** a schedule that uses the yearly rate each month and takes the payment from the balance before interest is added (two bugs; symptom: the balance goes negative long before the end, or never reaches zero).
- **Explain:** why the early payments of a long loan are mostly interest, and what paying a little extra early does.
- **Watch:** the last payment's rounding. Choose figures whose schedule ends within a cent, and say how real lenders adjust the last payment.

### 4. Rates, inflation and real returns (`fin.money.rates`)

- **Skills:** `effective-rate` (APR to effective annual rate for a compounding frequency), `real-vs-nominal` (the exact `(1 + n) / (1 + i) - 1` and the rough `n - i`), `deflate` (turn prices into today's money with the CPI).
- **Puzzle:** a card charges 24% APR compounded monthly. Is the real yearly cost 24%? (No, about 26.8%.)
- **Build:** `effective_annual_rate(apr, per_year)` and a table across frequencies. **Debug:** a "real return" report that subtracts inflation in percent points from a decimal return, and uses the start year's CPI where it needs the end year's (two bugs).
- **Explain:** a savings account pays 4% while inflation runs at 5%. Did the saver get richer? With numbers.
- **Real data:** CPI-U annual averages for a handful of years, read from bls.gov by the writer, with the series id (CUUR0000SA0) and the date read written in the topic.

### 5. Measuring returns (`fin.money.returns`)

- **Skills:** `simple-returns` (from a list of prices), `compound-returns` (chain returns by multiplying growth factors; why +50% then −50% loses 25%), `annualize` (from a total over a number of years, and from monthly returns), `means` (arithmetic mean for one period's expectation, geometric for growth over many).
- **Puzzle:** a fund returns +50% then −50%. Average return 0%. Where's your money? (Down 25%.)
- **Build:** `simple_returns(prices)` and `annualized_return(prices, periods_per_year)`. **Debug:** a performance report that averages returns arithmetically for its "growth per year" and divides prices the wrong way round (two bugs).
- **Explain:** the friend's "+50%, −50%, so I broke even" (the checkpoint asks this too, with other numbers; keep this one about a fund's report).
- **Watch:** say what a log return is and that log returns add, briefly; don't make it a skill.

### 6. Risk (`fin.money.risk`)

- **Skills:** `volatility` (sample standard deviation of returns, and annualizing it by the square root of periods), `drawdown` (the running peak and the largest fall from it), `risk-return` (reading two investments' return and volatility together).
- **Puzzle:** two funds both averaged 8% a year over ten years. Could one of them still have lost you half your money along the way? (Yes: drawdown.)
- **Build:** `max_drawdown(prices)` returning the fall as a decimal and the two positions. **Debug:** a risk report that annualizes monthly volatility by multiplying by 12 and resets the running peak every month (two bugs).
- **Explain:** why "volatility" understates what it feels like to own something that falls 50%, and what drawdown adds.
- **Watch:** sample (n − 1) versus population standard deviation: pick sample, say so once, and test for it.

### 7. Diversification (`fin.money.diversification`)

- **Skills:** `correlation` (compute it from two return lists), `portfolio-volatility` (two-asset formula and its meaning), `diversify` (with simulated uncorrelated assets, volatility falls about as one over the square root of the count, then stops at the shared part).
- **Puzzle:** two investments are each risky. Can owning both be less risky than owning either? (Yes, unless they move together.)
- **Build:** portfolio volatility of a two-asset mix across weights, find the lowest. **Debug:** a correlation function that divides by population standard deviations with a sample covariance, and pairs the lists shifted by one (two bugs).
- **Explain:** why an index fund lowers risk without lowering expected return, and the risk it can't remove.
- **Story:** Enron employees' retirement savings.
- **Watch:** the simulated assets need fixed numbers in the exercise, not a seed the test pins.

### 8. Fees, taxes and compounding (`fin.money.costs`)

- **Skills:** `fee-drag` (a yearly percentage fee compounds against you), `tax-deferral` (taxed every year against taxed once at the end, in outline, with a flat made-up rate), `costs-compare` (two options' final amounts and the difference as a share of the better one).
- **Puzzle:** a 1% yearly fee on a 30-year investment growing 7%: what share of the final amount does it take? (About a quarter.)
- **Build:** final amounts with and without a fee, and the share lost. **Debug:** a fee calculator that charges the fee once on the starting amount and applies growth after the fee in one year and before it in others (two bugs).
- **Explain:** why fees matter more over long horizons, in a paragraph and a number.
- **Watch:** keep taxes generic (a flat made-up rate, "a tax-deferred account" in outline). No country's rules as fact, no advice.

### 9. Stocks, bonds and funds (`fin.markets.instruments`)

- **Skills:** `claims` (what a share and a bond are claims on), `bond-value` (a simple annual-coupon bond as cash flows, priced with `present_value_of_flows`), `funds` (mutual fund, ETF, index: what each is and how they differ), `price-drivers` (a share's price as the present value of what owners expect, moved by expectations and rates).
- **Puzzle:** a bond pays 5% on $1,000 for 3 years. Market rates rise to 7%. Is it still worth $1,000? (No, about $947.51.)
- **Build:** `bond_price(face, coupon_rate, years, market_rate)`. **Debug:** a bond pricer that discounts the face value at year 0 and pays the coupon at the market rate (two bugs).
- **Explain:** why a bond's price falls when market rates rise, with numbers (the spec's Phase 2 checkpoint asks this deeper; here it's one bond).
- **Watch:** this topic previews Module 8; keep to annual coupons and no yield calculation.

### 10. How a trade happens (`fin.markets.trading`)

- **Skills:** `order-journey` (broker, exchange, clearing house, settlement, T+1), `order-types` (market, limit, stop), `spread` (bid, ask, spread, and what a market order pays), `matching` (match orders in a small order book: best price first, then earliest).
- **Puzzle:** you press "buy" at 10:00. When do you own the share in the eyes of the law? (At settlement, one business day later in the US since May 2024.)
- **Build:** a small order book as dictionaries and lists that matches an incoming market order against resting limit orders and returns the fills. **Debug:** a matcher that takes the worst price first and doesn't reduce a partly filled resting order (two bugs).
- **Explain:** why a market order in a thinly traded stock can cost much more than the last price shown.
- **Story:** the January 2021 GameStop trading restrictions and the clearing house's deposits (SEC staff report, October 2021).
- **Watch:** check the T+1 date (SEC rule, compliance date 28 May 2024) and say it's the US.

### 11. Reading market data (`fin.markets.prices`)

- **Skills:** `ohlc` (open, high, low, close, volume), `adjust` (adjust past prices for a split and a dividend so returns are right), `indexes` (price-weighted and cap-weighted, built from three made-up companies).
- **Puzzle:** a stock's chart shows a 50% drop overnight, and nobody lost money. How? (A 2-for-1 split.)
- **Build:** adjust a short price history for one split and compute the true return. **Debug:** an index calculator that weights by price where it should weight by market value and forgets to divide by the starting level (two bugs).
- **Explain:** why the same three companies give two different index returns depending on the weighting.
- **Watch:** the dividend adjustment: use the simple multiplicative factor `1 − dividend / close before the ex-date` and say other methods exist.

## Checkpoint 1: the loan and the portfolio (`fin.m1.checkpoint`)

As in the [spec](../../specs/finance-markets.md#module-1-money-time-and-risk). The ML track's `ml.m1.checkpoint` is the model for its files.

- **Build:** `build-loan-schedule`. A monthly amortization schedule for a stated loan, printed by month with totals to the cent; then, for a stated price list, its annualized return, volatility and maximum drawdown. Prerequisites: all eleven topics.
- **The way through:** `example-savings-plan` (a solved sibling: a monthly savings plan's growth schedule), steps `step-monthly-rate`, `step-payment`, `step-one-row`, `step-the-schedule`, and two fresh versions with other loans and prices (`build-car-loan`, `build-equipment-loan`).
- **Debug:** `debug-retirement-calculator`. A friend's retirement calculator that promises far too much; four bugs, stated as a count and the symptom: a yearly rate applied monthly, nominal returns where real ones were needed, an off-by-one in the number of periods, and the arithmetic mean used for growth. Each known-wrong fixes three of the four.
- **Explain:** "+50% one year and −50% the next, so I broke even", with the rubric: the chained growth factors (1.5 × 0.5 = 0.75), the loss of 25%, why the arithmetic mean misleads for growth, and the geometric mean as the honest yearly figure.

## Writing order

Four writers in parallel, each on its own branch from `main` after the track file lands:

| Writer | Topics |
| --- | --- |
| A | 1, 2, 3 |
| B | 4, 5, 6 |
| C | 7, 8, 9 |
| D | 10, 11, then the checkpoint |

Each topic is its own pull request. A writer runs `validate_one.py` on each topic, then the full validator, then `npm run time:content` in `web/`, and marks the topic `ready` when all pass. After all twelve are merged, a cold review reads the whole module as a beginner would and checks every claim by running code; its findings are fixed in one last pull request.
