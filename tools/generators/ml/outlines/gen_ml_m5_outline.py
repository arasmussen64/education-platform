"""Outlines Module 5 of the ML Foundations track, probability and statistics
for ML: planned topic.yaml files, the module in the track file, and the spec's
prose bullet turned into a table. Run from the repository root under uv.
Never overwrites a topic that isn't a planned outline."""

import pathlib

import yaml

ROOT = pathlib.Path(".")
TOPICS = ROOT / "content" / "topics"
TRACK_PATH = ROOT / "content" / "tracks" / "ml-foundations.yaml"
SPEC = ROOT / "docs" / "specs" / "ml-foundations.md"

MODULE = {
    "id": "ml.m5",
    "title": "Probability and statistics for ML",
    "topics": [
        "ml.prob.distributions",
        "ml.prob.expectation-and-variance",
        "ml.prob.bayes",
        "ml.prob.maximum-likelihood",
        "ml.prob.sampling-and-confidence",
        "ml.prob.entropy",
        "ml.prob.evaluating-models",
    ],
    "checkpoint": "ml.m5.checkpoint",
}

# id: (kind, title, summary, prerequisites, minutes, objectives, "you'll be able to" for the spec)
OUTLINES = {
    "ml.prob.distributions": (
        "topic", "Random variables and distributions",
        "A random variable as a number with chances attached: Bernoulli, binomial, uniform and normal, simulated with NumPy and drawn as text histograms.",
        ["ml.math.probability-and-statistics", "ml.la.numpy-arrays"], 50,
        ["Name the Bernoulli, binomial, uniform and normal distributions, and say what each one models.",
         "Simulate draws from each with np.random.default_rng and a seed.",
         "Turn a sample into a histogram and compare it with the formula.",
         "Read a probability as an area under a density, and say why a single value has probability zero."],
        "name the Bernoulli, binomial, uniform and normal distributions and what each models; simulate draws with a seeded generator; turn a sample into a histogram and compare it with the formula; read a probability as an area under a density"),
    "ml.prob.expectation-and-variance": (
        "topic", "Expectation and variance",
        "The mean of a random variable, its spread, the rules they follow, and the law of large numbers watched in a simulation.",
        ["ml.prob.distributions"], 50,
        ["Compute the expected value and the variance of a discrete distribution from its table.",
         "Use linearity of expectation, and the rule for the variance of a sum of independent variables.",
         "Watch sample means settle on the expectation as the sample grows, and say what the law of large numbers promises.",
         "Standardize a value with the mean and the standard deviation, and read the result."],
        "compute an expected value and a variance from a distribution's table; use linearity of expectation and the variance of an independent sum; watch sample means settle on the expectation and say what the law of large numbers promises; standardize a value and read it"),
    "ml.prob.bayes": (
        "topic", "Bayes' rule, properly",
        "Conditional probability, Bayes' rule with base rates, updating a belief as evidence arrives, and a naive Bayes spam filter.",
        ["ml.prob.distributions"], 55,
        ["Compute a conditional probability from a joint table.",
         "Apply Bayes' rule to a test result with a base rate, and say why the answer surprises people.",
         "Update a belief step by step as evidence arrives, in code.",
         "Build a naive Bayes classifier for short messages, and say what 'naive' assumes."],
        "compute a conditional probability from a joint table; apply Bayes' rule to a test result with a base rate and say why the answer surprises people; update a belief step by step as evidence arrives; build a naive Bayes classifier and say what \"naive\" assumes"),
    "ml.prob.maximum-likelihood": (
        "topic", "Maximum likelihood",
        "The likelihood of data under a model, why logs turn it into a sum, fitting a coin and a normal by maximizing it, and why least squares and cross-entropy are maximum likelihood in disguise.",
        ["ml.prob.expectation-and-variance", "ml.calc.loss-functions"], 55,
        ["Write the likelihood of a dataset under a model with a parameter.",
         "Take the log, and find the maximum by calculus and by gradient descent.",
         "Fit a coin's bias and a normal's mean and spread by maximum likelihood, and check against the sample statistics.",
         "Say why least squares and cross-entropy are maximum-likelihood losses."],
        "write the likelihood of data under a model with a parameter; take the log and find the maximum by calculus and by descent; fit a coin's bias and a normal's mean and spread; say why least squares and cross-entropy are maximum-likelihood losses"),
    "ml.prob.sampling-and-confidence": (
        "topic", "Sampling and confidence",
        "The sampling distribution of a mean, the standard error, the central limit theorem seen by simulation, confidence intervals, and the bootstrap.",
        ["ml.prob.expectation-and-variance"], 55,
        ["Simulate many samples and watch their means form a normal shape, whatever the population looks like.",
         "Compute a standard error, and say what shrinks it.",
         "Build a confidence interval for a mean, and say what it does and doesn't promise.",
         "Bootstrap an interval for a statistic that has no formula."],
        "simulate many samples and watch their means form a normal shape; compute a standard error and say what shrinks it; build a confidence interval and say what it does and doesn't promise; bootstrap an interval for a statistic with no formula"),
    "ml.prob.entropy": (
        "topic", "Entropy, cross-entropy and KL divergence",
        "Surprise, the entropy of a distribution, cross-entropy as the average surprise under the wrong model, and the gap between the two.",
        ["ml.prob.expectation-and-variance", "ml.calc.loss-functions"], 50,
        ["Compute the surprise of an outcome and the entropy of a distribution, in bits and in nats.",
         "Compute the cross-entropy between two distributions, and say why it is never below the entropy.",
         "Compute the KL divergence and read it as the gap between the two.",
         "Connect Module 4's cross-entropy loss to its name, and say what a model minimizes when it minimizes it."],
        "compute the surprise of an outcome and the entropy of a distribution; compute a cross-entropy and say why it is never below the entropy; compute the KL divergence as the gap; connect Module 4's cross-entropy loss to its name"),
    "ml.prob.evaluating-models": (
        "topic", "Evaluating a model with statistics",
        "Train, validation and test splits, the confusion matrix and the metrics built from it, confidence intervals on an accuracy, and comparing two models fairly.",
        ["ml.prob.sampling-and-confidence", "ml.calc.loss-functions"], 60,
        ["Split data into train, validation and test sets, and say what each is for and what leaks between them.",
         "Build a confusion matrix and compute accuracy, precision, recall and F1 from it.",
         "Put a confidence interval on an accuracy, and say when a test set is too small to tell.",
         "Compare two models on the same test set, and say whether the difference is real."],
        "split data into train, validation and test and say what each is for; build a confusion matrix and compute accuracy, precision, recall and F1; put a confidence interval on an accuracy; compare two models on one test set and say whether the difference is real"),
    "ml.m5.checkpoint": (
        "checkpoint", "Checkpoint 5: is the model better?",
        "Two classifiers' predictions on a held-out set, judged with a confusion matrix, the metrics, bootstrap intervals and a decision.",
        ["ml.prob.bayes", "ml.prob.maximum-likelihood", "ml.prob.evaluating-models"], 120,
        ["Evaluate two models' predictions on a held-out set with a confusion matrix, precision, recall and a bootstrap interval on the difference, and recommend one.",
         "Find and fix three bugs in an evaluation report: a threshold chosen on the test set, precision and recall swapped, and an interval built from the wrong resamples.",
         "Explain Bayes' rule with a base rate, and what a confidence interval does and doesn't promise."],
        None),
}

MARKER = (
    "# A planned outline for the Machine Learning Foundations track\n"
    "# (docs/specs/ml-foundations.md). It becomes real content when written.\n"
)


class Dumper(yaml.SafeDumper):
    pass


def str_presenter(dumper, data):
    style = '"' if any(ch in data for ch in ":#'\"") else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


Dumper.add_representer(str, str_presenter)


def dump(data) -> str:
    return yaml.dump(data, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=1000)


# --- the track file ------------------------------------------------------------------------

track = yaml.safe_load(TRACK_PATH.read_bytes().decode("utf-8"))
if not any(module["id"] == "ml.m5" for module in track["modules"]):
    track["modules"].append(MODULE)
    TRACK_PATH.write_bytes(dump(track).encode("utf-8"))
    print("wrote", TRACK_PATH)
else:
    print("track already has ml.m5")

# --- the planned topics ------------------------------------------------------------------------

for topic_id, (kind, title, summary, prereqs, minutes, objectives, _) in OUTLINES.items():
    folder = TOPICS / topic_id
    path = folder / "topic.yaml"
    if path.exists() and "status: planned" not in path.read_bytes().decode("utf-8"):
        print("kept (being written)", path)
        continue
    folder.mkdir(parents=True, exist_ok=True)
    outline = {
        "id": topic_id,
        "kind": kind,
        "status": "planned",
        "title": title,
        "summary": summary,
        "prerequisites": prereqs,
        "estimated_minutes": minutes,
        "rev": 1,
        "objectives": objectives,
    }
    path.write_bytes((MARKER + dump(outline)).encode("utf-8"))
    print("wrote", path)

# --- the spec: the prose bullet becomes a table --------------------------------------------------

spec = SPEC.read_bytes().decode("utf-8")
if "## Module 5: Probability and statistics for ML" not in spec:
    rows = []
    for number, topic_id in enumerate(MODULE["topics"], start=29):
        kind, title, summary, prereqs, minutes, objectives, able = OUTLINES[topic_id]
        needs = ", ".join(f"`{p}`" for p in prereqs)
        rows.append(f"| {number} | {title} | `{topic_id}` | {needs} | {able} |")
    section = (
        "## Module 5: Probability and statistics for ML\n\n"
        "Module 1 counted chances with a table of 1,000 people, and Module 4 took cross-entropy on trust. This module is the probability and statistics that make a model's numbers mean something: distributions and their expectations, Bayes' rule with base rates, maximum likelihood as where the losses come from, sampling and confidence, entropy as cross-entropy's name, and the statistics of judging a model. Every topic is proven in code, with NumPy's random generator seeded so every run agrees.\n\n"
        "| # | Topic | ID | Needs | You'll be able to… |\n"
        "| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n"
        "**Checkpoint 5: is the model better?** (`ml.m5.checkpoint`). Judge two classifiers' predictions on a held-out set: a confusion matrix and the metrics for each, a bootstrap interval on the difference in accuracy, and a recommendation; debug an evaluation report with three bugs (a threshold chosen on the test set, precision and recall swapped, an interval built from the wrong resamples); explain Bayes' rule with a base rate and what a confidence interval does and doesn't promise. The way through for a stuck learner, as in the earlier checkpoints: a solved sibling, steps, fresh versions.\n\n"
    )
    old_bullet = "- **5. Probability and statistics for ML:** distributions; expectation and variance; Bayes' rule properly; maximum likelihood; sampling and confidence; the statistics of evaluating a model.\n"
    assert old_bullet in spec, "the Module 5 prose bullet has changed"
    spec = spec.replace(old_bullet, "")
    spec = spec.replace(
        "Planned in prose until Phase 3 plans them in detail; then they get outlines like the cloud track's, as Modules 3 and 4 had before they were written (both on 2026-11-10).",
        "Planned in prose until Phase 3 plans them in detail; then they get outlines like the cloud track's, as Modules 3 and 4 had before they were written (both on 2026-11-10) and Module 5 has (outlined 2026-11-10).",
    )
    assert spec.count("## Later modules") == 1
    spec = spec.replace("## Later modules", section + "## Later modules")
    SPEC.write_bytes(spec.encode("utf-8"))
    print("wrote", SPEC)
else:
    print("spec already has Module 5")
