"""Writes the topic ml.prob.bayes (Module 5's third topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.bayes")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=True
    )
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def numbered(program: str) -> str:
    return "".join(f"{i + 1:>3} {line}\n" for i, line in enumerate(program.splitlines()))


# --- the worked example ------------------------------------------------------------------

EXAMPLE = '''import numpy as np

prevalence = 0.01
sensitivity = 0.95
specificity = 0.90

people = 100000
sick = people * prevalence
healthy = people - sick
true_positives = sick * sensitivity
false_positives = healthy * (1 - specificity)
print(round(true_positives), round(false_positives))
print(round(true_positives / (true_positives + false_positives), 3))

evidence = prevalence * sensitivity + (1 - prevalence) * (1 - specificity)
posterior = prevalence * sensitivity / evidence
print(round(posterior, 3))

prior = posterior
evidence = prior * sensitivity + (1 - prior) * (1 - specificity)
print(round(prior * sensitivity / evidence, 3))

rng = np.random.default_rng(4)
has = rng.random(people) < prevalence
positive = np.where(has, rng.random(people) < sensitivity, rng.random(people) < 1 - specificity)
print(round(float(has[positive].mean()), 3))

biases = np.linspace(0, 1, 11)
belief = np.full(11, 1 / 11)
for flip in [1, 1, 0, 1, 1, 1, 0, 1]:
    likelihood = np.where(flip == 1, biases, 1 - biases)
    belief = belief * likelihood / (belief * likelihood).sum()
print(np.round(belief, 3))
print(round(float(biases[belief.argmax()]), 1))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
assert lines[0] == "950 9900" and lines[1] == "0.088" and lines[2] == "0.088" and lines[3] == "0.477", EXAMPLE_OUT
assert abs(float(lines[4]) - 0.088) < 0.01, lines[4]
assert lines[-1] == "0.7" and "e-" not in EXAMPLE_OUT, EXAMPLE_OUT
SIMULATED = lines[4]
BELIEF = lines[-2]

# --- the fill-in ---------------------------------------------------------------------------

FILL_HEAD = '''def posterior(prior, likelihood_if_true, likelihood_if_false):
    """The chance it's true after seeing evidence that happens with chance
    likelihood_if_true when it's true and likelihood_if_false when it isn't."""
    evidence = prior * likelihood_if_true + (1 - PRIOR) * LIKE_FALSE
    return prior * likelihood_if_true / evidence


print(round(posterior(0.01, 0.95, 0.10), 3))
print(round(posterior(0.088, 0.95, 0.10), 3))
print(round(posterior(0.5, 0.95, 0.10), 3))
print(round(posterior(0.01, 0.95, 0.01), 3))
'''
FILL_SOLUTION = FILL_HEAD.replace("(1 - PRIOR)", "(1 - prior)").replace("LIKE_FALSE", "likelihood_if_false")
FILL_STARTER = FILL_HEAD.replace("(1 - PRIOR)", "(1 - ...)").replace("LIKE_FALSE", "...")
FILL_NO_FALSE = FILL_SOLUTION.replace("    evidence = prior * likelihood_if_true + (1 - prior) * likelihood_if_false", "    evidence = prior * likelihood_if_true + (1 - prior) * likelihood_if_true")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "0.088\n0.478\n0.905\n0.49\n", FILL_OUT
assert out(FILL_NO_FALSE) != FILL_OUT

# --- the write --------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

biases = np.linspace(0, 1, 11)
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def update(belief, likelihood):
    weighted = belief * likelihood
    return weighted / weighted.sum()


belief = np.full(11, 1 / 11)
for flip in [1, 0, 0, 0, 1, 0, 0, 0, 0, 0]:
    belief = update(belief, np.where(flip == 1, biases, 1 - biases))
print(np.round(belief, 3))
print(round(float(biases[belief.argmax()]), 1), round(float(belief.max()), 3))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT.endswith("0.2 0.3\n") or WRITE_OUT.splitlines()[-1].startswith("0.2 "), WRITE_OUT
assert "e-" not in WRITE_OUT, WRITE_OUT

# --- the build: a naive Bayes spam filter ----------------------------------------------------------

BUILD_FUNCTIONS = '''def train(spam, ham):
    vocabulary = sorted({word for message in spam + ham for word in message.split()})
    probs = {}
    for label, messages in (("spam", spam), ("ham", ham)):
        counts = {word: 1 for word in vocabulary}
        for message in messages:
            for word in message.split():
                counts[word] += 1
        total = sum(counts.values())
        probs[label] = {word: count / total for word, count in counts.items()}
    total = len(spam) + len(ham)
    prior = {"spam": len(spam) / total, "ham": len(ham) / total}
    return probs, prior


def classify(message, probs, prior):
    scores = {}
    for label in probs:
        score = math.log(prior[label])
        for word in message.split():
            if word in probs[label]:
                score += math.log(probs[label][word])
        scores[label] = score
    top = max(scores.values())
    weights = {label: math.exp(score - top) for label, score in scores.items()}
    return weights["spam"] / sum(weights.values())
'''
CORPUS = '''SPAM = ["win cash now", "cash prize now", "win a prize", "claim cash now"]
HAM = ["meeting at noon", "lunch at noon", "cash for lunch", "see you at the meeting"]
'''
BUILD_SOLUTION = "import math\n\n\n" + BUILD_FUNCTIONS + "\n\n" + CORPUS + '''probs, prior = train(SPAM, HAM)
print("P(cash | spam)", round(probs["spam"]["cash"], 3), "P(cash | ham)", round(probs["ham"]["cash"], 3))
for message in ["win cash", "lunch at noon", "cash at noon", "hello"]:
    print(f"{message}: {round(classify(message, probs, prior), 3)}")
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
build_lines = BUILD_OUT.splitlines()
assert float(build_lines[1].split()[-1]) > 0.8 and float(build_lines[2].split()[-1]) < 0.1, BUILD_OUT
assert build_lines[4] == "hello: 0.5", BUILD_OUT
BUILD_NO_SMOOTHING = BUILD_SOLUTION.replace("        counts = {word: 1 for word in vocabulary}", "        counts = {word: 0 for word in vocabulary}")
BUILD_NO_PRIOR = BUILD_SOLUTION.replace("        score = math.log(prior[label])", "        score = 0.0")
BUILD_NOT_NORMALIZED = BUILD_SOLUTION.replace('    return weights["spam"] / sum(weights.values())', '    return weights["spam"]')
assert BUILD_NOT_NORMALIZED != BUILD_SOLUTION
# With four spam and four ham messages the prior changes nothing the program
# prints; the hidden test with three spam to one ham is what catches a
# dropped prior (the validator checks every known-wrong fails some test).
assert out(BUILD_NOT_NORMALIZED) != BUILD_OUT
crash = subprocess.run([sys.executable, "-c", BUILD_NO_SMOOTHING], capture_output=True, text=True)
assert crash.returncode != 0 and "ValueError" in crash.stderr, crash.stderr[-200:]

# --- the debug ---------------------------------------------------------------------------------------

DEBUG_SOLUTION = '''def table(people, prevalence, sensitivity, specificity):
    sick = people * prevalence
    healthy = people - sick
    true_positives = sick * sensitivity
    false_positives = healthy * (1 - specificity)
    return true_positives, false_positives


def chance_if_positive(prior, sensitivity, specificity):
    evidence = prior * sensitivity + (1 - prior) * (1 - specificity)
    return prior * sensitivity / evidence


true_positives, false_positives = table(100000, 0.01, 0.95, 0.90)
print("positives", round(true_positives), round(false_positives))
first = chance_if_positive(0.01, 0.95, 0.90)
print("after one positive", round(first, 3))
second = chance_if_positive(first, 0.95, 0.90)
print("after two positives", round(second, 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    false_positives = healthy * (1 - specificity)", "    false_positives = healthy * specificity").replace(
    "second = chance_if_positive(first, 0.95, 0.90)", "second = chance_if_positive(0.01, 0.95, 0.90)"
)
DEBUG_TABLE_ONLY = DEBUG_SOLUTION.replace("second = chance_if_positive(first, 0.95, 0.90)", "second = chance_if_positive(0.01, 0.95, 0.90)")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "positives 950 9900\nafter one positive 0.088\nafter two positives 0.477\n", DEBUG_OUT
assert out(DEBUG_TABLE_ONLY) != DEBUG_OUT
assert out(DEBUG_STARTER).startswith("positives 950 89100\n"), out(DEBUG_STARTER)

# --- predict items ------------------------------------------------------------------------------------

PREDICT_TABLE = '''import numpy as np

# rows: has the condition, doesn't; columns: tests positive, tests negative
table = np.array([[30, 10], [20, 40]])
has, positive = table[0].sum(), table[:, 0].sum()
print(table.sum(), has, positive)
print(round(table[0, 0] / has, 2))
print(round(table[0, 0] / positive, 2))
'''
PREDICT_TABLE_OUT = out(PREDICT_TABLE)
print("predict table:\n" + PREDICT_TABLE_OUT)
assert PREDICT_TABLE_OUT == "100 40 50\n0.75\n0.6\n", PREDICT_TABLE_OUT

REVIEW_TABLE = '''import numpy as np

# rows: it rained, it didn't; columns: took an umbrella, didn't
table = np.array([[18, 2], [12, 68]])
rained = table[0].sum()
umbrella = table[:, 0].sum()
print(round(table[0, 0] / rained, 2), round(table[0, 0] / umbrella, 2))
print(round(rained / table.sum(), 2))
'''
REVIEW_TABLE_OUT = out(REVIEW_TABLE)
print("review table:\n" + REVIEW_TABLE_OUT)
assert REVIEW_TABLE_OUT == "0.9 0.6\n0.2\n", REVIEW_TABLE_OUT

REVIEW_CODE_STARTER = ""
REVIEW_CODE_SOLUTION = '''def bayes(prior, likelihood_if_true, likelihood_if_false):
    evidence = prior * likelihood_if_true + (1 - prior) * likelihood_if_false
    return prior * likelihood_if_true / evidence


print(round(bayes(0.01, 0.95, 0.10), 3))
print(round(bayes(0.3, 0.8, 0.2), 3))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "0.088\n0.632\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.bayes
kind: topic
status: ready
title: "Bayes' rule, properly"
summary: "Conditional probability, Bayes' rule with base rates, updating a belief as evidence arrives, and a naive Bayes spam filter."
prerequisites: [ml.prob.distributions]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Compute a conditional probability from a joint table."
  - "Apply Bayes' rule to a test result with a base rate, and say why the answer surprises people."
  - "Update a belief step by step as evidence arrives, in code."
  - "Build a naive Bayes classifier for short messages, and say what 'naive' assumes."
# Linked, never copied or embedded: 3Blue1Brown's videos are under the
# standard YouTube licence; OpenStax is CC BY 4.0; NumPy's documentation is
# under the NumPy licence (BSD-3-Clause).
resources:
  - title: "3Blue1Brown: Probability (Grant Sanderson), the lessons Bayes theorem, the geometry of changing beliefs, and The medical test paradox"
    url: https://www.3blue1brown.com/topics/probability
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "OpenStax Introductory Statistics 2e: sections 3.3 (Two Basic Rules of Probability) and 3.4 (Contingency Tables and Probability Trees)"
    url: https://openstax.org/details/books/introductory-statistics-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "numpy.linspace (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linspace.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-a-test-and-a-base-rate
  - parsons-bayes-in-one-line
  - mcq-ninety-five-percent-accurate
  - predict-a-joint-table
  - mcq-what-naive-means
  - fill-posterior
  - write-update-a-belief
prove:
  build: build-a-spam-filter
  debug: debug-base-rate-report
  explain:
    prompt: |
      A friend has tested positive for a condition that 1 person in 100 has, with a test that catches 95 percent of cases and wrongly flags 10 percent of healthy people, and is sure they have it. In your own words: what does Bayes' rule say, and what is the base rate's part in it? Walk them through a table of 100,000 people. Why would a second positive test change the picture so much more than the first? And what does "naive" mean in naive Bayes, and why does the method work anyway?
    rubric:
      - id: rule
        required: true
        description: "The chance of the condition given a positive test is the prior (base rate) times the test's hit rate, divided by the total chance of a positive from both groups: posterior = prior × likelihood / evidence; the direction matters, P(positive | sick) is not P(sick | positive)."
      - id: table
        required: true
        description: "Of 100,000 people, 1,000 have it and 950 test positive; 99,000 don't and 9,900 test positive anyway; so a positive person is one of 10,850, of whom 950 have it: about 9 percent. The healthy group is 99 times larger, so its small false-positive rate outweighs the sick group's high hit rate."
      - id: update
        required: true
        description: "After the first test the prior is no longer 1 percent but 9 percent; the same rule with that prior gives about 48 percent after a second positive. Each piece of independent evidence multiplies in, and the posterior becomes the next prior."
      - id: naive
        required: false
        description: "Naive Bayes assumes the words of a message are independent given its class, so their likelihoods just multiply; that's false (words come in phrases), so its probabilities are overconfident, but the ranking of spam against not-spam is usually right, which is all a filter needs."
    model_answer: |
      Bayes' rule turns the question round. The test's 95 percent is the chance of a positive given that you're sick; what your friend wants is the chance of being sick given a positive, and getting from one to the other needs the base rate, how common the condition is to begin with. Take 100,000 people. One in a hundred has it: 1,000 people, and the test catches 950 of them. The other 99,000 don't have it, and the test wrongly flags 10 percent, 9,900 people. So the positives are 950 plus 9,900, and only 950 of those 10,850 have the condition: about 9 percent. The healthy group is 99 times bigger than the sick group, so even a small false-positive rate on it swamps the hits. Written as a formula, that's the prior, 0.01, times the likelihood of a positive when sick, 0.95, divided by the total chance of a positive from both groups, which is Bayes' rule. A second positive test changes much more because it starts from a different place: the prior is no longer 1 percent but 9 percent, and running the same rule again gives about 48 percent. Each independent piece of evidence multiplies in, and yesterday's posterior is today's prior; a third positive would take it past 90. Naive Bayes is the same rule applied to a message word by word, and "naive" is the assumption that the words are independent once you know whether the message is spam, so their likelihoods simply multiply. That isn't true, since words come in phrases, so the probabilities it reports are too confident; but the comparison between spam and not-spam usually comes out the right way round, which is all a filter needs.
review_pool:
  - review-predict-rain-and-umbrellas
  - review-mcq-which-way-round
  - review-mcq-two-tests-at-once
  - review-mcq-why-add-one
  - review-bayes
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: conditional
    description: "Compute a conditional probability from a joint table, and keep P(A given B) apart from P(B given A)"
  - id: bayes
    description: "Apply Bayes' rule with a base rate, by table and by formula, and say why a positive test is still probably a false alarm when the condition is rare"
  - id: update
    description: "Update a belief step by step as evidence arrives, with the posterior as the next prior"
  - id: naive-bayes
    description: "Build a naive Bayes classifier and say what 'naive' assumes"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Module 1 put 1,000 people in a table and discovered that a positive test for a rare condition is usually a false alarm. This topic turns that table into a rule, **Bayes' rule**, applies it twice in a row to see evidence compound, keeps a whole belief in an array and updates it flip by flip, and finishes with the rule's most famous application in software: a **naive Bayes** spam filter, built from scratch in twenty lines.

The main resource is **3Blue1Brown's _Bayes theorem_** (the geometry of changing beliefs) and its sequel **_The medical test paradox_**; about 35 minutes, and the second one is this topic's worked example drawn as rectangles. OpenStax _Introductory Statistics 2e_ sections 3.3 and 3.4 have the rules and contingency tables as text. Watch for:

- **Conditional probability as restricting attention:** "given a positive test" means looking only at the positive column.
- **The base rate** (how common the thing is to begin with) deciding the answer.
- **Evidence multiplies in**, and the posterior becomes the next prior.

</Intro>

<Resource index={{0}} />

<Recap>

- **A joint table** (a **contingency table**) counts every combination: rows for has-it or not, columns for tests-positive or not. A **conditional probability** `P(A | B)`, read "the probability of A given B", restricts attention to the B row or column: `P(positive | has it)` is the positives in the has-it row over that row's total; `P(has it | positive)` is the same cell over the positive **column's** total. They are different numbers, and mixing them up is the commonest mistake in probability.
- **Bayes' rule** goes from one to the other: `P(has it | positive) = P(has it) * P(positive | has it) / P(positive)`. In words, **posterior** = **prior** (the base rate) times **likelihood** (how probable the evidence is if it's true), divided by the **evidence** (how probable the evidence is overall, from both groups): `prior * like_true + (1 - prior) * like_false`.
- **The base rate decides.** A condition 1 in 100 has, a test with **sensitivity** 0.95 (it catches 95 percent of cases) and **specificity** 0.90 (it clears 90 percent of the healthy, so a 10 percent **false-positive** rate): of 100,000 people, 950 true positives and 9,900 false ones, so a positive person has the condition with probability `950 / 10850 = 0.088`. The healthy group is 99 times larger, and its small error rate outweighs the sick group's high hit rate. A simulation of 100,000 people gave {SIMULATED}.
- **Evidence compounds.** After one positive the prior is no longer 0.01 but 0.088; a second independent positive, through the same rule, gives 0.477, and a third would pass 0.9. The posterior after each piece of evidence is the prior for the next.
- **A belief as an array.** For a coin of unknown bias, keep a probability for each candidate bias (`np.linspace(0, 1, 11)`, each starting at 1/11). After each flip, multiply by the likelihood of that flip under each bias (`biases` for heads, `1 - biases` for tails) and divide by the sum so the beliefs add to 1. After six heads in eight flips the belief peaks at 0.7: `{BELIEF}`.
- **Naive Bayes.** For a message, the evidence is its words. Train: count each word in spam and in not-spam (**ham**), with 1 added to every count (**add-one smoothing**, so an unseen word has a small probability instead of zero, which would veto everything). Classify: start from the log of each class's prior, add the log of each word's probability under that class, and turn the two log scores back into a probability for spam. The logs are there because a product of fifty small probabilities underflows to zero; sums of logs don't.
- **"Naive"** is the assumption that the words are independent given the class, so their likelihoods multiply. It's false (words come in phrases), so the probabilities it reports are overconfident, but the ranking is usually right, which is why the method filtered spam for years.
- **In machine learning:** every classifier that outputs a probability is reporting a posterior; the base rate is why a model that is 99 percent accurate can be useless on a rare class; and the belief array updated flip by flip is Bayesian inference in miniature, the idea behind every "update your estimate as data arrives" system.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-bayes-in-one-line.yaml",
    '''id: parsons-bayes-in-one-line
type: parsons
rev: 1
prompt: |
  Put the lines in order to compute the chance of having a condition after one positive test, from a base rate of 1 percent, a sensitivity of 0.95 and a false-positive rate of 0.10, printing `0.088`. One line is a decoy that doesn't belong.
lines:
  - 'prior, hit, false_alarm = 0.01, 0.95, 0.10'
  - 'evidence = prior * hit + (1 - prior) * false_alarm'
  - 'posterior = prior * hit / evidence'
  - 'print(round(posterior, 3))'
distractors:
  - 'posterior = hit'
explanation: |
  The posterior is the prior times the hit rate, divided by the total chance of a positive from both groups. The decoy answers the question the other way round: 0.95 is the chance of a positive **given** the condition, not the chance of the condition given a positive, and it ignores the base rate entirely.
skills: [bayes, conditional]
''',
)

write(
    "recall/mcq-ninety-five-percent-accurate.yaml",
    '''id: mcq-ninety-five-percent-accurate
type: mcq
rev: 1
prompt: |
  A condition affects 1 person in 100. A test catches 95 percent of cases and wrongly flags 10 percent of healthy people. You test positive. Roughly what is the chance you have it?
choices:
  - 'About 95 percent, the test''s accuracy'
  - 'About 50 percent: you either have it or you don''t'
  - 'About 1 percent: the test changes nothing'
  - 'About 9 percent: among 100,000 people, 950 true positives against 9,900 false ones'
answer: 3
explanation: |
  The healthy group is 99 times larger than the sick one, so its 10 percent false-positive rate produces 9,900 false alarms against 950 real hits. A positive person is one of 10,850, of whom 950 have the condition: 0.088. The test did change things, from 1 percent to 9, but not to 95; that number is the chance of a positive given the condition, the other way round.
skills: [bayes]
''',
)

write(
    "recall/predict-a-joint-table.yaml",
    f'''id: predict-a-joint-table
type: predict_output
rev: 1
prompt: |
  A joint table of 100 people. What does the program print?
code: |
{block(PREDICT_TABLE)}expected_output: |
{block(PREDICT_TABLE_OUT)}explanation: |
  40 people have the condition (the first row) and 50 test positive (the first column). `P(positive | has it)` restricts attention to the first row: 30 of 40, 0.75. `P(has it | positive)` restricts attention to the first column: the same 30, but out of 50, 0.6. Same cell, different denominator, different question.
skills: [conditional]
''',
)

write(
    "recall/mcq-what-naive-means.yaml",
    '''id: mcq-what-naive-means
type: mcq
rev: 1
prompt: |
  What is "naive" about naive Bayes, and why does it still work as a spam filter?
choices:
  - 'It assumes the words of a message are independent given its class, so their likelihoods multiply; that''s false, so its probabilities are overconfident, but the ranking of spam against not-spam is usually right'
  - 'It uses no training data, only a dictionary of spam words'
  - 'It assumes every message is equally likely to be spam, so it ignores the prior'
  - 'It is naive because it adds one to every count, which is a crude guess'
answer: 0
explanation: |
  The independence assumption is the naivety: "win" and "cash" are not independent clues, yet the filter multiplies them as if they were. The result is too confident, but a decision only needs the comparison to come out the right way round. It does use training counts and the prior; the add-one smoothing is a fix for unseen words, not the naive part.
skills: [naive-bayes]
''',
)

write(
    "recall/review-predict-rain-and-umbrellas.yaml",
    f'''id: review-predict-rain-and-umbrellas
type: predict_output
rev: 1
prompt: |
  A hundred days, by rain and by umbrella. What does the program print?
code: |
{block(REVIEW_TABLE)}expected_output: |
{block(REVIEW_TABLE_OUT)}explanation: |
  It rained on 20 days and umbrellas went out on 30. `P(umbrella | rain)` is 18 of the 20 rainy days, 0.9; `P(rain | umbrella)` is the same 18 days out of the 30 with umbrellas, 0.6. The base rate of rain is 0.2. Seeing an umbrella is good evidence of rain, but 12 of 30 umbrellas went out on dry days.
skills: [conditional]
''',
)

write(
    "recall/review-mcq-which-way-round.yaml",
    '''id: review-mcq-which-way-round
type: mcq
rev: 1
prompt: |
  A forensic match would occur by chance for 1 person in 10,000 who is innocent. A suspect matches. A lawyer says: "so there is only a 1 in 10,000 chance the suspect is innocent." What is wrong?
choices:
  - 'Nothing; that is what the match rate means'
  - 'The number is `P(match | innocent)`, not `P(innocent | match)`; in a city of a million, about 100 innocent people match too, so without other evidence the suspect is one of roughly 101'
  - 'The rate should be squared, because a match was found twice'
  - 'The lawyer should have said 1 in 5,000, since guilt and innocence are equally likely'
answer: 1
explanation: |
  This is the base-rate mistake with a courtroom name, the prosecutor''s fallacy. The match rate is the chance of the evidence given innocence; turning it into the chance of innocence given the evidence needs the prior, how many people could have been the source. Among a million, a 1-in-10,000 rate matches about a hundred innocent people, and the suspect is one of them plus the guilty one until other evidence narrows it.
skills: [conditional, bayes]
''',
)

write(
    "recall/review-mcq-why-add-one.yaml",
    '''id: review-mcq-why-add-one
type: mcq
rev: 1
prompt: |
  A naive Bayes filter was trained on messages in which the word "invoice" never appeared in spam. Without add-one smoothing, what happens to a new message that contains "invoice" along with five obvious spam words?
choices:
  - 'It is classified by the other five words; one unknown word makes no difference'
  - 'The word''s probability under spam is 0, so the spam score is log 0 and the message can never be spam, whatever the other words say; adding one to every count keeps every probability small but positive'
  - 'It is classified as spam with certainty, because a rare word is suspicious'
  - 'The filter asks for the word to be labelled by hand'
answer: 1
explanation: |
  The likelihoods multiply (the logs add), so a single zero vetoes the class no matter how strong the other evidence is, and `log(0)` isn't even a number. Add-one smoothing pretends every word was seen once in every class, which turns the zero into a small probability and lets the other five words decide.
skills: [naive-bayes]
''',
)

write(
    "recall/review-mcq-two-tests-at-once.yaml",
    '''id: review-mcq-two-tests-at-once
type: mcq
rev: 1
prompt: |
  With the topic''s numbers (base rate 0.01, sensitivity 0.95, false-positive rate 0.10), one positive test gives 0.088 and a second, independent positive gives 0.477. Why so much more the second time?
choices:
  - 'Because the second test is more accurate than the first'
  - 'It shouldn''t: two tests at once should give twice 0.088, about 0.18'
  - 'Because the second update starts from a prior of 0.088 instead of 0.01; each independent positive multiplies the odds by the same factor, 9.5, and the posterior after one test is the prior for the next'
  - 'Because the false positives were used up by the first test'
answer: 2
explanation: |
  Both tests are identical; what differs is the prior. Each independent positive multiplies the odds of having the condition by `0.95 / 0.10 = 9.5`: from odds of 1 to 99, to 9.5 to 99 (0.088), to 90 to 99 (0.477). Applying the rule twice is the same as applying it once with both results as evidence; nothing is doubled or used up.
skills: [update]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-test-and-a-base-rate/exercise.yaml",
    f'''id: example-a-test-and-a-base-rate
stage: worked_example
rev: 1
title: "A test, a base rate, and a belief that updates"
prompt: |
  This program works a positive test result three ways (a table of 100,000 people, Bayes' rule, and a simulation), applies the rule twice in a row, and then keeps a belief about a coin's bias in an array and updates it flip by flip. Press **Run**, then read how each part works.
steps:
  - label: "The table of 100,000 people"
    lines: "3-13"
    note: "A condition 1 in 100 has; a test with sensitivity 0.95 (it catches 95 percent of cases) and specificity 0.90 (it clears 90 percent of the healthy). Of 100,000 people, 1,000 are sick and 950 of them test positive; 99,000 are healthy and 9,900 of them test positive anyway. A positive person is one of 10,850, and 950 of those have the condition: 0.088."
  - label: "The same, as Bayes' rule"
    lines: "15-17"
    note: "Prior times likelihood, over the evidence. The evidence is the total chance of a positive from both groups, `0.01 * 0.95 + 0.99 * 0.10`; the posterior is the sick group's share of it. Same 0.088, without the 100,000 people."
  - label: "A second positive test"
    lines: "19-21"
    note: "The posterior becomes the prior and the same rule runs again: 0.477. The second test isn't better than the first; it starts from 0.088 instead of 0.01. A third would pass 0.9."
  - label: "A simulation agrees"
    lines: "23-26"
    note: "A hundred thousand simulated people: each has the condition with chance 0.01, and tests positive with chance 0.95 if so and 0.10 if not. Among those who tested positive, the fraction who have it is {SIMULATED}, close to the rule's 0.088. Chance alone made the difference."
  - label: "A belief about a coin, updated flip by flip"
    lines: "28-34"
    note: "Eleven candidate biases, 0 to 1, each believed equally at first. Each flip multiplies every candidate's belief by the likelihood of that flip under it (`biases` for heads, `1 - biases` for tails), and dividing by the sum keeps the beliefs adding to 1. After six heads in eight flips the belief peaks at 0.7, with 0.8 close behind. That loop is Bayesian inference: the posterior after each flip is the prior for the next."
''',
)
write("exercises/example-a-test-and-a-base-rate/solution.py", EXAMPLE)
write(
    "exercises/example-a-test-and-a-base-rate/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the table, the rule, a second test, a simulation and a belief updated flip by flip."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-posterior/exercise.yaml",
    f'''id: fill-posterior
stage: fill_in
rev: 1
title: "Bayes' rule as a function"
prompt: |
  `posterior(prior, likelihood_if_true, likelihood_if_false)` should return the chance something is true after seeing evidence, where the evidence happens with chance `likelihood_if_true` when it's true and `likelihood_if_false` when it isn't. The evidence's total probability adds up both ways it can happen. Replace each `...` so the program prints a first positive test, a second, a test on someone already thought a coin-flip likely to have it, and a test whose false alarms are rare:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The evidence can come from the group that has it, with chance `prior`, or from the group that doesn't, with chance `1 - prior`."
  - "In the second group the evidence happens with chance `likelihood_if_false`."
skills: [bayes, update]
''',
)
write("exercises/fill-posterior/starter.py", FILL_STARTER)
write("exercises/fill-posterior/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-posterior/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the four posteriors."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_edges():
    """Evidence that's equally likely either way leaves the prior alone; evidence impossible when false makes it certain."""
    posterior = function("posterior")
    assert abs(posterior(0.3, 0.5, 0.5) - 0.3) < 1e-12
    assert abs(posterior(0.3, 0.8, 0.0) - 1.0) < 1e-12
''',
)
write("exercises/fill-posterior/wrong/false-alarms-ignored.py", FILL_NO_FALSE)
write(
    "exercises/fill-posterior/wrong/typed-in.py",
    "def posterior(prior, likelihood_if_true, likelihood_if_false):\n    return 0.088\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-update-a-belief/exercise.yaml",
    f'''id: write-update-a-belief
stage: write
rev: 1
title: "Update a belief"
prompt: |
  Write `update(belief, likelihood)`, which takes an array of probabilities over candidate biases and an array of likelihoods of the latest evidence under each candidate, multiplies them entry by entry, and returns the result scaled to sum to 1. Then start from an equal belief over the starter's eleven biases, update it with the ten flips `[1, 0, 0, 0, 1, 0, 0, 0, 0, 0]` (the likelihood of heads is `biases`, of tails `1 - biases`), and print the belief rounded to 3 places, then the most believed bias and its probability rounded to 3:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`np.where(flip == 1, biases, 1 - biases)` is the likelihood array for one flip."
  - "Divide the product by its own sum: `weighted / weighted.sum()`."
skills: [update]
''',
)
write("exercises/write-update-a-belief/starter.py", WRITE_STARTER)
write("exercises/write-update-a-belief/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-update-a-belief/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the belief after ten flips, its peak and the peak's probability."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_one_update():
    """A flat belief over three candidates updated with likelihoods [0.2, 0.3, 0.5] becomes those numbers; a second heads doubles down."""
    update = function("update")
    belief = update(np.array([1 / 3, 1 / 3, 1 / 3]), np.array([0.2, 0.3, 0.5]))
    assert np.allclose(belief, [0.2, 0.3, 0.5])
    assert abs(belief.sum() - 1) < 1e-12
    again = update(belief, np.array([0.2, 0.3, 0.5]))
    assert np.allclose(again, np.array([0.04, 0.09, 0.25]) / 0.38)
''',
)
write(
    "exercises/write-update-a-belief/wrong/not-normalized.py",
    WRITE_SOLUTION.replace("    return weighted / weighted.sum()", "    return weighted"),
)
write(
    "exercises/write-update-a-belief/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef update(belief, likelihood):\n    return belief\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof ------------------------------------------------------------------------------------------

write(
    "exercises/build-a-spam-filter/exercise.yaml",
    f'''id: build-a-spam-filter
stage: build
rev: 1
title: "A naive Bayes spam filter"
prompt: |
  Starting from a blank editor, write a naive Bayes filter for short messages (words separated by spaces):

  - `train(spam, ham)` takes two lists of messages and returns `(probs, prior)`. `probs["spam"]` and `probs["ham"]` map every word in the whole vocabulary to its probability under that class: the word's count in that class's messages **plus one** (add-one smoothing), divided by the class's total of those smoothed counts. `prior` maps each class to its share of the messages.
  - `classify(message, probs, prior)` returns the probability that the message is spam: for each class, start a score at the log of its prior and add the log of each word's probability under that class (skip words not in the vocabulary); then turn the two log scores into a probability for spam, `exp(spam_score) / (exp(spam_score) + exp(ham_score))`, subtracting the larger score from both first so the exponentials can't overflow.

  Then train on these messages and print `P(cash | spam)` and `P(cash | ham)` rounded to 3, and the spam probability of four messages:

  ```python
{block(CORPUS)}  ```

  ```
{block(BUILD_OUT)}  ```

  The checks train on other messages, including ones where a word appears in only one class and a message with no known words.
skills: [naive-bayes, bayes, conditional]
''',
)
write("exercises/build-a-spam-filter/starter.py", "")
write("exercises/build-a-spam-filter/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-spam-filter/test_exercise.py",
    f'''import math

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

SPAM = ["buy now", "buy cheap now"]
HAM = ["see you now", "see you soon"]


def test_the_output():
    """Prints the two word probabilities and four classifications."""
    assert run() == {BUILD_OUT!r}


def test_smoothed_probabilities():
    """With add-one smoothing, 'buy' under spam is (2 + 1) / (5 + 6) and under ham (0 + 1) / (6 + 6)."""
    train = function("train")
    probs, prior = train(SPAM, HAM)
    assert abs(probs["spam"]["buy"] - 3 / 11) < 1e-12
    assert abs(probs["ham"]["buy"] - 1 / 12) < 1e-12
    assert prior == {{"spam": 0.5, "ham": 0.5}}
    assert abs(sum(probs["spam"].values()) - 1) < 1e-12


def test_classify():
    """A message of unknown words gets the prior; spam words push the probability up, ham words down; a word seen in one class only doesn't crash."""
    train = function("train")
    classify = function("classify")
    probs, prior = train(SPAM, HAM)
    assert abs(classify("hello there", probs, prior) - 0.5) < 1e-12
    assert classify("buy cheap", probs, prior) > 0.8
    assert classify("see you", probs, prior) < 0.2
    assert 0 < classify("cheap soon", probs, prior) < 1


def test_unequal_priors():
    """With three spam messages to one ham, an unknown message is spam with probability 0.75."""
    train = function("train")
    classify = function("classify")
    probs, prior = train(["a b", "c d", "e f"], ["g h"])
    assert abs(classify("zzz", probs, prior) - 0.75) < 1e-12
''',
)
write("exercises/build-a-spam-filter/wrong/no-smoothing.py", BUILD_NO_SMOOTHING)
write("exercises/build-a-spam-filter/wrong/no-prior.py", BUILD_NO_PRIOR)
write("exercises/build-a-spam-filter/wrong/not-normalized.py", BUILD_NOT_NORMALIZED)
write(
    "exercises/build-a-spam-filter/wrong/typed-in.py",
    "import math\n\n\n"
    + "def train(spam, ham):\n    return {'spam': {'cash': 0.2}, 'ham': {'cash': 0.08}}, {'spam': 0.5, 'ham': 0.5}\n\n\n"
    + "def classify(message, probs, prior):\n    return 0.5\n\n\n"
    + CORPUS
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-base-rate-report/exercise.yaml",
    f'''id: debug-base-rate-report
stage: debug
rev: 1
title: "A base-rate report with two mistakes"
prompt: |
  This program builds the table for 100,000 people and applies Bayes' rule to one positive test and then a second. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the false positives come out as 89,100, nine tenths of the healthy, because `table` multiplies by the specificity, the fraction the test **clears**, where the false-positive rate is `1 - specificity`. Fix that, and the second line repeats the first: the second test must start from the posterior of the first, not from the original base rate.
skills: [bayes, update]
''',
)
write("exercises/debug-base-rate-report/starter.py", DEBUG_STARTER)
write("exercises/debug-base-rate-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-base-rate-report/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the positives and the chance after one and two positive tests."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_table_on_other_numbers():
    """A perfectly specific test has no false positives; a useless one flags everyone."""
    table = function("table")
    assert table(1000, 0.1, 0.9, 1.0) == (90.0, 0.0)
    assert table(1000, 0.1, 0.9, 0.0) == (90.0, 900.0)
''',
)
write("exercises/debug-base-rate-report/wrong/table-only.py", DEBUG_TABLE_ONLY)
write(
    "exercises/debug-base-rate-report/wrong/typed-in.py",
    "def table(people, prevalence, sensitivity, specificity):\n    return 950.0, 9900.0\n\n\n"
    + "def chance_if_positive(prior, sensitivity, specificity):\n    return 0.088\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ---------------------------------------------------------------------------

write(
    "exercises/review-bayes/exercise.yaml",
    f'''id: review-bayes
stage: review_code
rev: 1
title: "Bayes' rule, from memory"
prompt: |
  Write `bayes(prior, likelihood_if_true, likelihood_if_false)`, the posterior probability after evidence, and print it rounded to 3 places for a base rate of 0.01 with likelihoods 0.95 and 0.10, and for a prior of 0.3 with likelihoods 0.8 and 0.2:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [bayes]
''',
)
write("exercises/review-bayes/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-bayes/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-bayes/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 0.088 and 0.632."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_values():
    """Evidence equally likely either way leaves the prior; a prior of 0.5 with likelihoods 0.9 and 0.1 gives 0.9."""
    bayes = function("bayes")
    assert abs(bayes(0.2, 0.4, 0.4) - 0.2) < 1e-12
    assert abs(bayes(0.5, 0.9, 0.1) - 0.9) < 1e-12
''',
)
write(
    "exercises/review-bayes/wrong/the-other-way-round.py",
    '''def bayes(prior, likelihood_if_true, likelihood_if_false):
    return likelihood_if_true


print(round(bayes(0.01, 0.95, 0.10), 3))
print(round(bayes(0.3, 0.8, 0.2), 3))
''',
)
write(
    "exercises/review-bayes/wrong/typed-in.py",
    "def bayes(prior, likelihood_if_true, likelihood_if_false):\n    return 0.088\n\n\nprint(0.088)\nprint(0.632)\n",
)

print("ml.prob.bayes written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
