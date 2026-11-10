import math


def train(spam, ham):
    vocabulary = sorted({word for message in spam + ham for word in message.split()})
    probs = {}
    for label, messages in (("spam", spam), ("ham", ham)):
        counts = {word: 0 for word in vocabulary}
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


SPAM = ["win cash now", "cash prize now", "win a prize", "claim cash now"]
HAM = ["meeting at noon", "lunch at noon", "cash for lunch", "see you at the meeting"]
probs, prior = train(SPAM, HAM)
print("P(cash | spam)", round(probs["spam"]["cash"], 3), "P(cash | ham)", round(probs["ham"]["cash"], 3))
for message in ["win cash", "lunch at noon", "cash at noon", "hello"]:
    print(f"{message}: {round(classify(message, probs, prior), 3)}")
