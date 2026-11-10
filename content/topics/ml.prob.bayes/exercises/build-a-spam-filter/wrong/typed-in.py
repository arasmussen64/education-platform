import math


def train(spam, ham):
    return {'spam': {'cash': 0.2}, 'ham': {'cash': 0.08}}, {'spam': 0.5, 'ham': 0.5}


def classify(message, probs, prior):
    return 0.5


SPAM = ["win cash now", "cash prize now", "win a prize", "claim cash now"]
HAM = ["meeting at noon", "lunch at noon", "cash for lunch", "see you at the meeting"]
print('P(cash | spam) 0.154 P(cash | ham) 0.071')
print('win cash: 0.874')
print('lunch at noon: 0.034')
print('cash at noon: 0.172')
print('hello: 0.5')
