"""Writes the topic ml.tf.tokens-and-embeddings (Module 9's first topic). Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed
in. The corpus is generated in code from a tiny grammar with a seed, so
nothing is downloaded; the bigram model is a lookup table of logits trained
with Module 8's loop; bits per character are printed to two decimals and the
generator checks that a tenth-decimal nudge of one table entry leaves every
printed line unchanged. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.tf.tokens-and-embeddings")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def differs(program: str, expected: str) -> bool:
    """True if the program fails or prints something other than expected: what a known-wrong must do."""
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True)
    return result.returncode != 0 or result.stdout.replace("\r\n", "\n") != expected


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def quoted(text: str) -> str:
    """A single-quoted YAML scalar: the one place where '' is an apostrophe."""
    return "'" + text.replace("'", "''") + "'"


def mcq(item_id: str, prompt: str, choices: list[str], answer: int, explanation: str, skills: list[str]) -> None:
    """An MCQ whose right answer is never the longest choice, with plain apostrophes in the block scalars."""
    lengths = [len(c) for c in choices]
    assert lengths[answer] < max(length for i, length in enumerate(lengths) if i != answer), (item_id, lengths)
    assert "''" not in prompt and "''" not in explanation, item_id
    write(
        f"recall/{item_id}.yaml",
        f"id: {item_id}\ntype: mcq\nrev: 1\nprompt: |\n{block(prompt)}choices:\n"
        + "".join(f"  - {quoted(c)}\n" for c in choices)
        + f"answer: {answer}\nexplanation: |\n{block(explanation)}skills: [{', '.join(skills)}]\n",
    )


# Module 8's pieces, as Checkpoint 8 left them (the ones a language model needs).
MODULE = '''class Sequential:
    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def backward(self, grad):
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
        return grad

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]

    def gradients(self):
        return [g for layer in self.layers for g in layer.gradients()]

    def train(self):
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = True

    def eval(self):
        for layer in self.layers:
            if hasattr(layer, "training"):
                layer.training = False


class SoftmaxCrossEntropy:
    def forward(self, logits, labels):
        shifted = logits - logits.max(axis=1, keepdims=True)
        log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
        self.probs = np.exp(log_probs)
        self.labels = labels
        return float(-log_probs[np.arange(len(labels)), labels].mean())

    def backward(self):
        grad = self.probs.copy()
        grad[np.arange(len(self.labels)), self.labels] -= 1
        return grad / len(self.labels)


class Adam:
    def __init__(self, rate, weight_decay=0.0, beta1=0.9, beta2=0.999, eps=1e-8):
        self.rate, self.weight_decay = rate, weight_decay
        self.beta1, self.beta2, self.eps = beta1, beta2, eps
        self.m, self.v, self.t = None, None, 0

    def step(self, params, grads):
        if self.m is None:
            self.m = [np.zeros_like(p) for p in params]
            self.v = [np.zeros_like(p) for p in params]
        self.t += 1
        for i, (param, grad) in enumerate(zip(params, grads)):
            grad = grad + self.weight_decay * param
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            param -= self.rate * m_hat / (np.sqrt(v_hat) + self.eps)


def numeric_gradient(f, param, h=1e-6):
    """The central-difference gradient of f() with respect to every entry of param, which f reads."""
    grad = np.zeros_like(param)
    for index in np.ndindex(param.shape):
        old = param[index]
        param[index] = old + h
        up = f()
        param[index] = old - h
        down = f()
        param[index] = old
        grad[index] = (up - down) / (2 * h)
    return grad


def gradient_check(net, loss, X, y):
    """The largest gap between any parameter's backward gradient and its numeric one, in eval mode."""
    net.eval()
    loss.forward(net.forward(X), y)
    net.backward(loss.backward())
    worst = 0.0
    for param, grad in zip(net.parameters(), net.gradients()):
        numeric = numeric_gradient(lambda: loss.forward(net.forward(X), y), param)
        worst = max(worst, float(np.abs(grad - numeric).max()))
    return worst


def batches(n, batch_size, rng):
    order = rng.permutation(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


def evaluate(net, loss, X, y):
    net.eval()
    logits = net.forward(X)
    return loss.forward(logits, y), float((logits.argmax(axis=1) == y).mean())


def fit(net, loss, optimizer, X_train, y_train, X_val, y_val, epochs, batch_size=32, seed=0):
    rng = np.random.default_rng(seed)
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}
    for epoch in range(epochs):
        net.train()
        for index in batches(len(X_train), batch_size, rng):
            loss.forward(net.forward(X_train[index]), y_train[index])
            net.backward(loss.backward())
            optimizer.step(net.parameters(), net.gradients())
        train_loss, _ = evaluate(net, loss, X_train, y_train)
        val_loss, val_accuracy = evaluate(net, loss, X_val, y_val)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_accuracy)
    return history
'''

# This topic's additions.
TEXT = '''

def make_corpus(n_sentences, seed):
    """A tiny world in text, who did what where, one sentence after another, drawn with a seed so nothing is downloaded."""
    rng = np.random.default_rng(seed)
    who = ["the cat", "the dog", "a bird", "my fox", "the owl"]
    did = ["sat", "ran", "slept", "hid", "sang"]
    where = ["on the mat", "in the box", "by the door", "under the bed", "near the pond"]
    return " ".join(f"{rng.choice(who)} {rng.choice(did)} {rng.choice(where)}." for _ in range(n_sentences))


def vocabulary(text):
    """Every distinct character, sorted, and the table from character to integer."""
    chars = sorted(set(text))
    return chars, {char: i for i, char in enumerate(chars)}


def encode(text, stoi):
    """Text to an array of token ids."""
    return np.array([stoi[char] for char in text])


def decode(ids, chars):
    """Token ids back to text."""
    return "".join(chars[int(i)] for i in ids)


class Embedding:
    """A table with one row of dim numbers per token. forward looks rows up; backward adds each row's gradient back into the row it came from, so a row used twice gets both."""

    def __init__(self, n_tokens, dim, seed=0, scale=None):
        rng = np.random.default_rng(seed)
        self.scale = 1 / np.sqrt(dim) if scale is None else scale
        self.W = rng.standard_normal((n_tokens, dim)) * self.scale
        self.dW = np.zeros_like(self.W)

    def forward(self, ids):
        self.ids = ids
        return self.W[ids]

    def backward(self, grad_out):
        self.dW = np.zeros_like(self.W)
        np.add.at(self.dW, self.ids, grad_out)
        return None

    def parameters(self):
        return [self.W]

    def gradients(self):
        return [self.dW]


def pairs(ids):
    """Every character and the one after it: the inputs and the targets of a bigram model."""
    return ids[:-1], ids[1:]


def split_text(X, y, held_out=0.1):
    """The last share of the text is held out, in order: a text split is by position, never shuffled."""
    n_val = int(len(X) * held_out)
    return X[:-n_val], y[:-n_val], X[-n_val:], y[-n_val:]


def bits_per_char(loss):
    """A cross-entropy in nats, as bits per character: the average number of yes-or-no questions the model needs per character."""
    return loss / np.log(2)


def unigram_bits(ids, n_tokens):
    """The bits per character of guessing from the character frequencies alone, ignoring what came before."""
    p = np.bincount(ids, minlength=n_tokens) / len(ids)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def counted_bigram_bits(X_train, y_train, X_val, y_val, n_tokens):
    """The bits per character on the held-out pairs of a table of counted next-character frequencies (plus a tenth of a count, so nothing unseen is impossible)."""
    table = np.full((n_tokens, n_tokens), 0.1)
    np.add.at(table, (X_train, y_train), 1)
    probs = table / table.sum(axis=1, keepdims=True)
    return float(-np.log2(probs[X_val, y_val]).mean())


def sample(model, chars, stoi, start, length, rng):
    """Write length characters after start, drawing each from the model's probabilities given the character before it."""
    ids = [stoi[char] for char in start]
    for _ in range(length):
        logits = model.forward(np.array([ids[-1]]))[0]
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        ids.append(int(rng.choice(len(chars), p=probs)))
    return decode(ids, chars)


def greedy(model, chars, stoi, start, length):
    """Write length characters after start, always taking the likeliest next character."""
    ids = [stoi[char] for char in start]
    for _ in range(length):
        ids.append(int(model.forward(np.array([ids[-1]]))[0].argmax()))
    return decode(ids, chars)
'''

EXAMPLE_HEAD = "import numpy as np\n\n\n" + MODULE + TEXT
EXAMPLE_TAIL = '''

text = make_corpus(200, seed=0)
chars, stoi = vocabulary(text)
V = len(chars)
print(f"corpus: {len(text):,} characters, starting: {text[:46]}")
print(f"vocabulary: {V} characters: {''.join(chars)!r}")
ids = encode(text, stoi)
print("encode('the cat') ->", encode("the cat", stoi).tolist(), "| decode back:", repr(decode(encode("the cat", stoi), chars)), "| the whole corpus round-trips:", decode(ids, chars) == text)

# An embedding is a lookup, which is a one-hot row times the table; its gradient adds up.
table = Embedding(V, 4, seed=1)
some = encode("cat", stoi)
onehot = np.eye(V)[some]
print("a lookup equals one-hot @ W:", bool(np.allclose(table.forward(some), onehot @ table.W)))
table.forward(np.array([2, 5, 2]))
table.backward(np.ones((3, 4)))
print("the gradient for a row used twice is the sum of both:", table.dW[[2, 5]].sum(axis=1).tolist())
loss = SoftmaxCrossEntropy()
X_all, y_all = pairs(ids)
print("gradient check of a table of logits:", "passes" if gradient_check(Sequential([Embedding(V, V, seed=1)]), loss, X_all[:8], y_all[:8]) < 1e-6 else "fails")

# Positions: a set of vectors can't tell 'ab' from 'ba' until each vector carries its place.
positions = Embedding(8, 4, seed=2)


def as_a_set(rows):
    return sorted(tuple(np.round(row, 6)) for row in rows)


ab, ba = encode("ab", stoi), encode("ba", stoi)
print("'ab' and 'ba' as unordered sets of vectors are the same without positions:", as_a_set(table.forward(ab)) == as_a_set(table.forward(ba)), "| with positions added:", as_a_set(table.forward(ab) + positions.forward(np.arange(2))) == as_a_set(table.forward(ba) + positions.forward(np.arange(2))))

# The bigram model: a table of logits, one row per character, trained to predict the next.
X_train, y_train, X_val, y_val = split_text(X_all, y_all)
model = Sequential([Embedding(V, V, seed=1)])
first = loss.forward(model.forward(X_train), y_train)
print(f"first loss {first:.2f} nats = {bits_per_char(first):.2f} bits per character (log2 of {V} is {np.log2(V):.2f}) | guessing from character frequencies alone: {unigram_bits(ids, V):.2f} bits")
history = fit(model, loss, Adam(0.1), X_train, y_train, X_val, y_val, epochs=5, batch_size=64)
print("held-out bits per character after each epoch:", [round(float(bits_per_char(v)), 2) for v in history["val_loss"]], "| next-character accuracy:", round(history["val_accuracy"][-1], 2))
print(f"a table of counted next-character frequencies scores {counted_bigram_bits(X_train, y_train, X_val, y_val, V):.2f} bits on the same held-out text")
print("sample:", repr(sample(model, chars, stoi, "the ", 60, np.random.default_rng(3))))
print("greedy:", repr(greedy(model, chars, stoi, "the ", 24)))
'''
EXAMPLE = EXAMPLE_HEAD + EXAMPLE_TAIL
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 12, EX
assert EX[1].startswith("vocabulary: 23 characters: ' .abcd"), EX[1]
assert EX[2].endswith("| the whole corpus round-trips: True"), EX[2]
assert EX[3] == "a lookup equals one-hot @ W: True", EX[3]
assert EX[4] == "the gradient for a row used twice is the sum of both: [8.0, 4.0]", EX[4]
assert EX[5] == "gradient check of a table of logits: passes", EX[5]
assert EX[6].endswith("are the same without positions: True | with positions added: False"), EX[6]
FIRST_BITS = float(EX[7].split("= ")[1].split(" bits")[0])
UNIGRAM_BITS = float(EX[7].split("alone: ")[1].split(" bits")[0])
assert abs(FIRST_BITS - 4.52) < 0.1 and 3.3 < UNIGRAM_BITS < 4.4, EX[7]
EPOCH_BITS = eval(EX[8].split(": ")[1].split(" |")[0])
FINAL_BITS = EPOCH_BITS[-1]
ACCURACY = float(EX[8].split("accuracy: ")[1])
COUNTED_BITS = float(EX[9].split("scores ")[1].split(" bits")[0])
assert FINAL_BITS < UNIGRAM_BITS - 0.5 and abs(FINAL_BITS - COUNTED_BITS) < 0.1 and ACCURACY > 0.4, EX[8:10]
assert EPOCH_BITS == sorted(EPOCH_BITS, reverse=True), EPOCH_BITS
assert "the the" in EX[11], EX[11]
NUDGED = EXAMPLE.replace("model = Sequential([Embedding(V, V, seed=1)])\n", "model = Sequential([Embedding(V, V, seed=1)])\nmodel.layers[0].W[0, 0] += 1e-10\n")
assert NUDGED != EXAMPLE and out(NUDGED) == EXAMPLE_OUT, "a tenth-decimal nudge changed a printed line"
EXAMPLE_LINES = EXAMPLE.splitlines()
SAMPLE_TEXT = EX[10].split("sample: ")[1]


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_ENCODE = '''chars = sorted(set("hello world"))
stoi = {char: i for i, char in enumerate(chars)}
print(chars)
print([stoi[char] for char in "low"], "".join(chars[i] for i in [3, 2, 4, 4, 5]))
'''
PREDICT_ENCODE_OUT = out(PREDICT_ENCODE)
assert PREDICT_ENCODE_OUT == "[' ', 'd', 'e', 'h', 'l', 'o', 'r', 'w']\n[4, 5, 7] hello\n", PREDICT_ENCODE_OUT

PREDICT_LOOKUP = '''import numpy as np

W = np.array([[1.0, 0.0], [0.0, 1.0], [2.0, 3.0], [5.0, 5.0]])
ids = np.array([2, 0, 2])
print(W[ids].tolist())
print(bool(np.array_equal(W[ids], np.eye(4)[ids] @ W)), W[ids].shape)
'''
PREDICT_LOOKUP_OUT = out(PREDICT_LOOKUP)
assert PREDICT_LOOKUP_OUT == "[[2.0, 3.0], [1.0, 0.0], [2.0, 3.0]]\nTrue (3, 2)\n", PREDICT_LOOKUP_OUT

PREDICT_SCATTER = '''import numpy as np

ids = np.array([2, 0, 2])
grad_out = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
added = np.zeros((4, 2))
np.add.at(added, ids, grad_out)
assigned = np.zeros((4, 2))
assigned[ids] = grad_out
print(added.tolist())
print(assigned[2].tolist())
'''
PREDICT_SCATTER_OUT = out(PREDICT_SCATTER)
assert PREDICT_SCATTER_OUT == "[[2.0, 20.0], [0.0, 0.0], [4.0, 40.0], [0.0, 0.0]]\n[3.0, 30.0]\n", PREDICT_SCATTER_OUT

PREDICT_BITS = '''import numpy as np

print(round(2.0794 / np.log(2), 2), round(float(np.log2(27)), 2))
p = np.array([0.5, 0.25, 0.25])
print(float(-(p * np.log2(p)).sum()))
'''
PREDICT_BITS_OUT = out(PREDICT_BITS)
assert PREDICT_BITS_OUT == "3.0 4.75\n1.5\n", PREDICT_BITS_OUT

REVIEW_PREDICT = '''import numpy as np

ids = np.array([1, 3, 1, 1])
grad_out = np.ones((4, 2))
dW = np.zeros((5, 2))
np.add.at(dW, ids, grad_out)
print(dW[:, 0].tolist(), int((dW != 0).any(axis=1).sum()))
'''
REVIEW_PREDICT_OUT = out(REVIEW_PREDICT)
assert REVIEW_PREDICT_OUT == "[0.0, 3.0, 0.0, 1.0, 0.0] 2\n", REVIEW_PREDICT_OUT

PARSONS_LINES = [
    "import numpy as np",
    "ids = np.array([3, 1, 4, 1, 5])",
    "X, y = ids[:-1], ids[1:]",
    "print(X.tolist(), y.tolist(), len(X))",
]
PARSONS_OUT = out("\n".join(PARSONS_LINES) + "\n")
assert PARSONS_OUT == "[3, 1, 4, 1] [1, 4, 1, 5] 4\n", PARSONS_OUT

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = "import numpy as np\n\n\n" + "class Embedding:" + TEXT.split("class Embedding:")[1].split("def pairs")[0].rstrip("\n") + '''


table = Embedding(5, 3, seed=0)
table.W[:] = np.arange(15.0).reshape(5, 3)
ids = np.array([4, 1, 4])
print(table.forward(ids).tolist())
table.backward(np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]]))
print(table.dW[:, 0].tolist())
'''
FILL_STARTER = FILL_SOLUTION.replace("        return self.W[ids]", "        return self.W[...]").replace("        np.add.at(self.dW, self.ids, grad_out)", "        np.add.at(self.dW, ..., grad_out)")
assert FILL_STARTER.count("...") == 2
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "[[12.0, 13.0, 14.0], [3.0, 4.0, 5.0], [12.0, 13.0, 14.0]]\n[0.0, 2.0, 0.0, 0.0, 4.0]\n", FILL_OUT
FILL_ASSIGNS = FILL_SOLUTION.replace("        np.add.at(self.dW, self.ids, grad_out)", "        self.dW[self.ids] = grad_out")
assert differs(FILL_ASSIGNS, FILL_OUT)

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import numpy as np


def vocabulary(text):
    """Every distinct character, sorted, and the table from character to integer."""
    chars = sorted(set(text))
    return chars, {char: i for i, char in enumerate(chars)}


def encode(text, stoi):
    """Text to an array of token ids."""
    return np.array([stoi[char] for char in text])


def decode(ids, chars):
    """Token ids back to text."""
    return "".join(chars[int(i)] for i in ids)


def bits_per_char(loss):
    """A cross-entropy in nats, as bits per character."""
    return loss / np.log(2)


chars, stoi = vocabulary("a cat sat. a bat sat.")
print(len(chars), "".join(chars))
print(encode("a bat", stoi).tolist(), decode(encode("tabs", stoi), chars), decode(encode("a cat sat. a bat sat.", stoi), chars) == "a cat sat. a bat sat.")
print(round(bits_per_char(np.log(len(chars))), 3), round(bits_per_char(1.0), 3))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT.startswith("7  .abcst\n[2, 0, 3, 2, 6] tabs True\n"), WRITE_OUT
WRITE_TAIL = "chars, stoi = vocabulary(" + WRITE_SOLUTION.split("\n\n\nchars, stoi = vocabulary(", 1)[1]
WRITE_UNSORTED = WRITE_SOLUTION.replace("    chars = sorted(set(text))", "    chars = list(dict.fromkeys(text))")
WRITE_LOG10 = WRITE_SOLUTION.replace("    return loss / np.log(2)", "    return loss / np.log(10)")
assert differs(WRITE_UNSORTED, WRITE_OUT) and differs(WRITE_LOG10, WRITE_OUT)

# --- the build ----------------------------------------------------------------------------------

BUILD_TAIL = '''

text = make_corpus(200, seed=0)
chars, stoi = vocabulary(text)
V = len(chars)
ids = encode(text, stoi)
print(V, decode(ids, chars) == text, encode("owl", stoi).tolist())
table = Embedding(V, 3, seed=1)
table.forward(np.array([4, 4, 1]))
table.backward(np.ones((3, 3)))
print(table.dW[:, 0].tolist().count(0.0), table.dW[4, 0], table.dW[1, 0])
loss = SoftmaxCrossEntropy()
X_all, y_all = pairs(ids)
X_train, y_train, X_val, y_val = split_text(X_all, y_all)
print(len(X_train), len(X_val), bool((X_all[1:] == y_all[:-1]).all()), "gradient check:", "passes" if gradient_check(Sequential([Embedding(V, V, seed=1)]), loss, X_all[:8], y_all[:8]) < 1e-6 else "fails")
model = Sequential([Embedding(V, V, seed=1)])
history = fit(model, loss, Adam(0.1), X_train, y_train, X_val, y_val, epochs=5, batch_size=64)
learned = bits_per_char(history["val_loss"][-1])
baseline = unigram_bits(ids, V)
counted = counted_bigram_bits(X_train, y_train, X_val, y_val, V)
print(f"{learned:.2f} bits | beats the unigram baseline by at least 0.5: {learned < baseline - 0.5} | within 0.1 of the counted table: {abs(learned - counted) < 0.1}")
print(repr(sample(model, chars, stoi, "the ", 40, np.random.default_rng(3))))
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + MODULE + TEXT + BUILD_TAIL
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
BUILD_LINES = BUILD_OUT.splitlines()
assert BUILD_LINES[0].startswith("23 True [") and BUILD_LINES[1] == "21 2.0 1.0", BUILD_OUT
assert BUILD_LINES[2].endswith("True gradient check: passes") and BUILD_LINES[3].endswith("| beats the unigram baseline by at least 0.5: True | within 0.1 of the counted table: True"), BUILD_OUT
assert out(BUILD_SOLUTION.replace("model = Sequential([Embedding(V, V, seed=1)])\n", "model = Sequential([Embedding(V, V, seed=1)])\nmodel.layers[0].W[0, 0] += 1e-10\n")) == BUILD_OUT
BUILD_WRONGS = {
    "gradient-assigned-not-added": BUILD_SOLUTION.replace("        np.add.at(self.dW, self.ids, grad_out)", "        self.dW[self.ids] = grad_out"),
    "targets-not-shifted": BUILD_SOLUTION.replace("    return ids[:-1], ids[1:]", "    return ids[:-1], ids[:-1]"),
    "split-shuffled": BUILD_SOLUTION.replace("    n_val = int(len(X) * held_out)\n    return X[:-n_val], y[:-n_val], X[-n_val:], y[-n_val:]", "    n_val = int(len(X) * held_out)\n    order = np.random.default_rng(0).permutation(len(X))\n    X, y = X[order], y[order]\n    return X[:-n_val], y[:-n_val], X[-n_val:], y[-n_val:]"),
    "bits-in-nats": BUILD_SOLUTION.replace("    return loss / np.log(2)", "    return loss"),
    "unsorted-vocabulary": BUILD_SOLUTION.replace("    chars = sorted(set(text))", "    chars = list(dict.fromkeys(text))"),
}
for key, code in BUILD_WRONGS.items():
    assert code != BUILD_SOLUTION, key

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = "import numpy as np\n\n\n" + MODULE + TEXT + '''

text = make_corpus(200, seed=0)
chars, stoi = vocabulary(text)
V = len(chars)
ids = encode(text, stoi)
loss = SoftmaxCrossEntropy()
X_all, y_all = pairs(ids)
X_train, y_train, X_val, y_val = split_text(X_all, y_all)
print("gradient check:", "passes" if gradient_check(Sequential([Embedding(V, V, seed=1)]), loss, X_all[:8], y_all[:8]) < 1e-6 else "fails")
model = Sequential([Embedding(V, V, seed=1)])
history = fit(model, loss, Adam(0.1), X_train, y_train, X_val, y_val, epochs=5, batch_size=64)
print(f"held-out bits per character {bits_per_char(history['val_loss'][-1]):.2f} | next-character accuracy {history['val_accuracy'][-1]:.2f}")
print("sample:", repr(sample(model, chars, stoi, "the ", 40, np.random.default_rng(3))))
'''
BUG_ASSIGN = ("        np.add.at(self.dW, self.ids, grad_out)", "        self.dW[self.ids] = grad_out")
BUG_SHIFT = ("    return ids[:-1], ids[1:]", "    return ids[:-1], ids[:-1]")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_ASSIGN).replace(*BUG_SHIFT)
DEBUG_STILL_ASSIGN = DEBUG_SOLUTION.replace(*BUG_ASSIGN)
DEBUG_STILL_SHIFT = DEBUG_SOLUTION.replace(*BUG_SHIFT)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
STILL_SHIFT_OUT = out(DEBUG_STILL_SHIFT)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT + "assign fixed:\n" + STILL_SHIFT_OUT)
assert DEBUG_OUT.startswith("gradient check: passes\nheld-out bits per character ") and 1.5 < float(DEBUG_OUT.splitlines()[1].split("character ")[1].split(" |")[0]) < 2.5, DEBUG_OUT
assert STARTER_OUT.startswith("gradient check: fails\nheld-out bits per character 0.0"), STARTER_OUT
assert STILL_SHIFT_OUT.startswith("gradient check: passes\nheld-out bits per character 0.0") and "accuracy 1.00" in STILL_SHIFT_OUT, STILL_SHIFT_OUT
assert differs(DEBUG_STILL_ASSIGN, DEBUG_OUT)
assert out(DEBUG_SOLUTION.replace("model = Sequential([Embedding(V, V, seed=1)])\n", "model = Sequential([Embedding(V, V, seed=1)])\nmodel.layers[0].W[0, 0] += 1e-10\n")) == DEBUG_OUT
DEBUG_BITS = DEBUG_OUT.splitlines()[1].split("character ")[1].split(" |")[0]
STILL_SHIFT_BITS = STILL_SHIFT_OUT.splitlines()[1].split("character ")[1].split(" |")[0]
STILL_SHIFT_SAMPLE = STILL_SHIFT_OUT.splitlines()[2].split("sample: ")[1]

REVIEW_CODE_SOLUTION = '''import numpy as np


def encode(text, stoi):
    """Text to an array of token ids."""
    return np.array([stoi[char] for char in text])


def decode(ids, chars):
    """Token ids back to text."""
    return "".join(chars[int(i)] for i in ids)


chars = sorted(set("no pain no gain"))
stoi = {char: i for i, char in enumerate(chars)}
print(encode("pan", stoi).tolist(), decode(encode("gain", stoi), chars), decode([0, 4, 5], chars))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "[6, 1, 4] gain  in\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace('    return "".join(chars[int(i)] for i in ids)', '    return "".join(chars[int(i) - 1] for i in ids)')
assert differs(REVIEW_CODE_WRONG, REVIEW_CODE_OUT)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.tf.tokens-and-embeddings
kind: topic
status: ready
title: "Tokens, embeddings and positions"
summary: "Text becomes integers through a vocabulary; an embedding is a lookup into a matrix (a one-hot row times the matrix) whose gradient scatters back into the rows that were used; positions get a second table; and the first language model, a bigram table of next-character logits, is trained with the module's loop and sampled from."
prerequisites: [ml.m8.checkpoint]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Build a character vocabulary, encode text to integers and decode it back, and say what a token is."
  - "Implement an embedding layer with the module's interface, forward as a lookup and backward as a scatter-add into the rows used, and gradient-check it."
  - "Add a learned position table and say why a model that treats its inputs as a set needs one."
  - "Train a bigram model on a corpus generated in code, read its loss in bits per character, and sample from it."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0; the video is
# under YouTube's standard licence.
resources:
  - title: "3Blue1Brown: Transformers, the tech behind LLMs (the first twelve minutes: tokens, the embedding matrix, and what a direction in embedding space can mean)"
    url: https://www.3blue1brown.com/lessons/gpt
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Wikipedia: Word embedding (the idea of a vector per token, and the Development and history section)"
    url: https://en.wikipedia.org/wiki/Word_embedding
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Word n-gram language model (the Unigram model and Bigram model sections: predicting the next token from the one before)"
    url: https://en.wikipedia.org/wiki/Word_n-gram_language_model
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-text-becomes-numbers
  - predict-encode-and-decode
  - mcq-what-a-token-is
  - predict-a-lookup
  - predict-scatter-add
  - mcq-why-the-gradient-adds
  - mcq-why-positions
  - predict-bits-per-character
  - mcq-the-first-loss
  - parsons-pairs
  - mcq-why-shift-by-one
  - mcq-sampling-against-greedy
  - fill-embedding
  - write-vocabulary-and-bits
prove:
  build: build-a-bigram-model
  debug: debug-a-model-that-is-too-good
  explain:
    prompt: |
      A teammate who has only ever called a tokenizer and an embedding layer from a library asks four things. "What is a token, and what does the model actually see?" "An embedding layer has no inputs in the usual sense, just integers; how does a gradient get into it, and what happens to a row that appears twice in a batch?" "Why does a model need a position table at all, if every token already has a vector?" "Your bigram model's first loss was about 4.5 bits and a table of counts scored about the same as the trained one; what did training buy, and why do its samples look like the grammar but read like nonsense?" Answer all four in your own words.
    rubric:
      - id: tokens
        required: true
        description: "A token is a piece of text with an integer id from a fixed vocabulary; the model sees only the integers (and learns a vector per integer), and decoding turns ids back into text; a character vocabulary is the simplest, with longer pieces (subwords) coming in a later topic."
      - id: embedding
        required: true
        description: "A lookup W[ids] is the same as one-hot rows times W, so the gradient with respect to W is the one-hot transposed times the output gradient: each output row's gradient lands in the row that was looked up, and a row used twice gets the sum of both (scatter-add), exactly as a shared weight does; there is no gradient for the ids, which are not continuous."
      - id: positions
        required: true
        description: "The token table gives the same vector to a character wherever it occurs, so a model that treats its inputs as a set of vectors (attention does) gets the same set for 'ab' and 'ba'; a second table indexed by place, added to each token's vector, makes the vectors in the two orders different sets, which is what lets later layers use order."
      - id: bigram
        required: true
        description: "The bigram model is a table of logits, one row per character, trained to predict the next character; the first loss is about log of the vocabulary size (4.52 bits for 23 characters; a random start sits a hair above it) because the start guesses nearly evenly; training reproduces what counting the next-character frequencies gives, so it buys the machinery (a loss, a loop, a gradient check, sampling) that the later models need, not a better bigram; samples follow the grammar's letter pairs but a one-character memory can't hold a word, so they read like the grammar's sound without its sense."
    model_answer: |
      A token is a piece of text that has been given an integer, and the vocabulary is the fixed list of those pieces: here every distinct character of the corpus, sorted, so 23 of them, with the space and the full stop among them. The model never sees text. Encoding turns a string into an array of ids, the model works entirely on those integers and on the vectors it learns for each one, and decoding turns ids back into characters at the end; the only thing the model knows about 't' is which row it is. An embedding layer looks up a row of its table for each id, and that lookup is the same arithmetic as a one-hot row (a 1 in the token's column, zeros elsewhere) multiplied by the table, which is how the gradient gets in. The gradient of a matrix product with respect to the table is the one-hot rows transposed times the gradient coming from above, and a one-hot transposed just places each output row's gradient into the row that was looked up. A row that appears twice in a batch gets both gradients added, because the same parameter was used twice, exactly as a kernel weight used at every position or a dense weight used by every row of the batch gets a sum; our backward does that with a scatter-add, and the gradient check confirms it. The ids themselves get no gradient, since there is nothing continuous to nudge. The position table exists because the token table is blind to place: 't' gets the same vector at the start of a sentence as at the end, so a model that treats its inputs as a set of vectors, which attention does, receives the same set for 'ab' as for 'ba' and cannot tell them apart. A second table, indexed by position and added to each token's vector, makes the first slot's vector differ from the second's, so the two orders are different sets and later layers can use order; a model that merely summed its inputs would still be blind, which is why the layer that comes next does more than sum. The bigram model is the smallest language model there is: a table with one row of logits per character, and training it to predict the next character. Its first loss was a hair above log of 23, 4.52 bits per character, because a table started near zero guesses every character nearly equally and that is what guessing evenly costs. After training it scored within a hundredth of a table built by counting how often each character follows each other one, which is the right answer for this model: training did not buy a better bigram, it bought the machinery, a loss over tokens, the loop, the gradient check, sampling with a temperature, that the next topics will point at models counting could never build. The samples follow the grammar's pairs of letters, so they are full of 'th' and 'at' and spaces in sensible places, but a one-character memory cannot hold a word, let alone a sentence, so the text has the grammar's sound without its sense; and greedy decoding, always taking the likeliest next character, falls into 'the the the', because the likeliest character after a space is 't' and the likeliest after 'e' is a space. A longer memory is what attention is for.
review_pool:
  - review-predict-scatter-add
  - review-mcq-what-the-model-sees
  - review-mcq-positions
  - review-encode-and-decode
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: tokens
    description: "Build a character vocabulary, encode text to integers and decode it back, and say what a token is"
  - id: embedding
    description: "Implement an embedding layer whose backward scatter-adds into the rows used, and gradient-check it"
  - id: positions
    description: "Add a learned position table and say why a model that treats its inputs as a set needs one"
  - id: bigram
    description: "Train a bigram model on a generated corpus, read its loss in bits per character, and sample from it"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A network takes numbers, and text isn't numbers. This topic is the bridge: a **vocabulary** that gives every distinct character an integer, an **embedding** that gives every integer a vector the network can learn, a second table for **positions**, and the smallest language model there is, a **bigram** table that predicts the next character from the one before it, trained with Module 8's loop on a corpus generated in code. Everything the transformer does later starts from these three tables and this loss.

The main resource is **3Blue1Brown's _Transformers, the tech behind LLMs_** (chapter 5 of the neural-networks series; the first twelve minutes cover tokens and the embedding matrix). Wikipedia's _Word embedding_ page has the idea of a vector per token and its history, and the _Word n-gram language model_ page's Unigram and Bigram sections are the counting view of what this topic trains. Watch for:

- **The embedding matrix**: one column (here, one row) per token.
- **Direction as meaning**: what nearby vectors share.
- **The next-token prediction**: the whole game, from a bigram table to a transformer.

</Intro>

<Resource index={{0}} />

<Recap>

- **Tokens.** `vocabulary(text)` is every distinct character sorted, 23 for the example's corpus (the space and the full stop included), with `stoi` from character to integer; `encode` turns text into an array of ids and `decode` turns ids back, and the whole corpus round-trips. The model sees only the integers. A character vocabulary is the simplest; Tokenizers: byte-pair encoding replaces characters with longer pieces.
- **The corpus is generated in code**: `make_corpus` draws "who did what where" sentences from a tiny grammar with a seed, {EX[0].split("corpus: ")[1].split(" characters")[0]} characters for 200 sentences, so nothing is downloaded and no licence is involved; its text is dull on purpose, which makes every number below checkable.
- **An embedding is a lookup, and a lookup is a matrix multiply.** `Embedding(n_tokens, dim)` keeps a table `W` with one row per token; `forward(ids)` returns `W[ids]`, which equals the one-hot rows of `ids` times `W` (the example checks it). That is why it has a gradient: `dW` is the one-hot rows transposed times the output gradient, which places each output row's gradient into the row that was looked up. `backward` does it with `np.add.at`, a **scatter-add**, so a row used twice gets the sum of both gradients (the example's row 2 received 8, row 5 received 4), as every shared parameter in Module 8 did. There is no gradient for the ids. The gradient check passes.
- **Positions.** The token table gives 't' the same vector wherever it sits, so a model that treats its inputs as a **set** of vectors (attention, next topic, does) receives the same set for `'ab'` and `'ba'`. A second `Embedding(max_length, dim)` indexed by place, added to each token's vector, makes the two orders different sets. (A model that only summed its vectors would stay blind even then: `(a + p0) + (b + p1)` equals `(b + p0) + (a + p1)`; attention does more than sum.)
- **Pairs and the split.** A bigram model's inputs are every character and its targets the character after it: `X, y = ids[:-1], ids[1:]`, the text moved one step. The held-out set is the last tenth of the text **by position**, never a shuffle, because shuffled characters would put the neighbours of every held-out pair into the training set.
- **Bits per character.** The cross-entropy comes out in nats; dividing by `log 2` gives **bits per character**, the average number of yes-or-no questions the model needs to pin down the next character. The first loss is {FIRST_BITS:.2f} bits, a hair above `log2(23)`, 4.52, because a table started near zero guesses nearly evenly; guessing from the character frequencies alone (the **unigram** baseline) costs {UNIGRAM_BITS:.2f} bits; the trained bigram reaches {FINAL_BITS:.2f} on held-out text, with next-character accuracy {ACCURACY:.0%}.
- **Counting gives the same answer.** A table of how often each character follows each other one, turned into probabilities, scores {COUNTED_BITS:.2f} bits on the same text. Training bought no better bigram; it bought the machinery, a loss over tokens, the loop, the gradient check and sampling, that the next topics' models need and counting can't build.
- **Sampling and greedy.** `sample` draws each next character from the model's probabilities (`rng.choice(V, p=probs)`), and the text follows the grammar's letter pairs without ever holding a word. `greedy` always takes the likeliest character and falls into `the the the`, because after a space the likeliest character is `t` and after `e` it is a space. A one-character memory is the limit of this model; attention is what lengthens it.
- **In machine learning** (names you'll meet later): `nn.Embedding` is this layer, `tokenizer.encode` and `decode` are these two functions over a learned vocabulary, **positional embeddings** are the second table (sinusoidal or rotary positions are formulas instead of a table), **bits per character** and **perplexity** (two to the power of it, per token) are the units language models are judged in, and `temperature`, `top_k` and `top_p` are the knobs on `sample` that Generating and judging text turns.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-encode-and-decode.yaml",
    f'''id: predict-encode-and-decode
type: predict_output
rev: 1
prompt: |
  A character vocabulary from the text `"hello world"`: the distinct characters sorted, each given its position as an id. What does the program print?
code: |
{block(PREDICT_ENCODE)}expected_output: |
{block(PREDICT_ENCODE_OUT)}explanation: |
  The space sorts before the letters, so it is id 0 and the letters follow alphabetically: d, e, h, l, o, r, w. "low" is l, o, w, which are 4, 5, 7. Decoding [3, 2, 4, 4, 5] reads the characters at those ids: h, e, l, l, o. Encoding and decoding are the same table read in opposite directions.
skills: [tokens]
''',
)

mcq(
    "mcq-what-a-token-is",
    "A character-level model is trained on a corpus with 23 distinct characters. What does the model actually receive as input, and what is a token?",
    [
        "The characters themselves, as strings; a token is a word",
        "Integers from 0 to 22, one per character, each looked up in a table of learned vectors; a token is a piece of text that has been given one of those integers",
        "The ASCII codes of the characters, used directly as numbers, so that nearby codes mean nearby letters and the model can do arithmetic on them without a lookup",
        "A one-hot vector per word in the corpus",
    ],
    1,
    "The vocabulary fixes the pieces (here single characters) and gives each an id; encoding turns text into those ids and the model works on them and on the vector it learns for each. The ASCII code would impose an order (a near b) that means nothing; a lookup lets each id have its own learned vector. Words are tokens only when the vocabulary is made of words.",
    ["tokens"],
)

write(
    "recall/predict-a-lookup.yaml",
    f'''id: predict-a-lookup
type: predict_output
rev: 1
prompt: |
  A table of four rows of two numbers, and three ids. `W[ids]` looks up a row per id. What does the program print?
code: |
{block(PREDICT_LOOKUP)}expected_output: |
{block(PREDICT_LOOKUP_OUT)}explanation: |
  Row 2, row 0, row 2: a lookup repeats a row as often as its id appears, and the result has one row per id (3) with the table's width (2). The one-hot rows of the ids times the table give exactly the same array, because each one-hot row picks out one row of W, which is why an embedding is a matrix multiply in disguise and has a gradient.
skills: [embedding]
''',
)

write(
    "recall/predict-scatter-add.yaml",
    f'''id: predict-scatter-add
type: predict_output
rev: 1
prompt: |
  The gradient of a lookup: three output rows' gradients go back to the rows they came from, with `np.add.at`, and then with plain assignment. What does the program print?
code: |
{block(PREDICT_SCATTER)}expected_output: |
{block(PREDICT_SCATTER_OUT)}explanation: |
  Id 2 was looked up twice, so with `add.at` its row receives both gradients, [1, 10] + [3, 30] = [4, 40]; id 0 receives [2, 20]; rows 1 and 3 were never used and stay zero. Plain assignment writes the two gradients for row 2 one after the other and keeps only the last, [3, 30]: the gradient of a row used twice must be the sum, and assignment loses one.
skills: [embedding]
''',
)

mcq(
    "mcq-why-the-gradient-adds",
    "In a batch of ids, the same token appears three times. What is the gradient for its row of the embedding table, and why?",
    [
        "The sum of the three output rows' gradients, because the same parameters were used three times and each use contributes, as a shared weight always does",
        "The last of the three, because the latest use overwrites the earlier ones",
        "The average of the three, because a row that appears more often would otherwise be updated too strongly and drift away from the rows of rarer tokens, which the averaging keeps fair",
        "Zero, because integers have no derivative",
    ],
    0,
    "A lookup is one-hot rows times the table, and the gradient of that product with respect to the table is the one-hot rows transposed times the output gradient: every row of the batch adds its gradient into the row it looked up. That is the same rule that gave a kernel weight the sum over positions and a dense weight the sum over the batch. The ids have no gradient; the table does.",
    ["embedding"],
)

mcq(
    "mcq-why-positions",
    "Every token already has a learned vector. Why add a second table indexed by position?",
    [
        "To make the vectors longer, since more dimensions always help",
        "Because the token table gives 't' the same vector wherever it sits, so a model that treats its inputs as a set of vectors gets the same set for 'ab' and 'ba'; adding a vector per place makes the two orders different sets",
        "Because without it the ids would have to be sorted before the lookup, and sorting the ids of a sentence would destroy the sentence, so the position table records where each id came from so that the sort can be undone afterwards",
        "To store how many times each token has appeared so far",
    ],
    1,
    "Position is information the token table cannot carry: the same character gets the same row every time. Attention, in the next topic, looks at its inputs as a set, so without positions it cannot tell one order from another. A vector per place, added in, breaks the tie. Nothing is sorted, and the tables are not counters.",
    ["positions"],
)

write(
    "recall/predict-bits-per-character.yaml",
    f'''id: predict-bits-per-character
type: predict_output
rev: 1
prompt: |
  Converting a cross-entropy from nats to bits, the cost of guessing evenly among 27 characters, and the entropy of a three-way distribution. What does the program print?
code: |
{block(PREDICT_BITS)}expected_output: |
{block(PREDICT_BITS_OUT)}explanation: |
  Dividing by log 2 converts nats to bits: 2.0794 nats is log 8, which is 3 bits, three yes-or-no questions among eight options. Guessing evenly among 27 characters costs log2 of 27, 4.75 bits. A distribution of a half and two quarters costs 1 bit half the time and 2 bits the other half: 1.5.
skills: [bigram]
''',
)

mcq(
    "mcq-the-first-loss",
    "A bigram table of logits starts near zero, and its first loss on a 23-character corpus is 4.52 bits per character. Where does that number come from, and what would a much larger first loss mean?",
    [
        "From the corpus: it is the entropy of the text, the best any model can do",
        "From log2 of 23: a table near zero gives every character the same probability, and guessing evenly among 23 costs 4.52 bits; a much larger first loss would mean the table started with big numbers, confidently wrong",
        "From the learning rate, which sets how large the first loss can be; a larger first loss would mean the rate was set too high and the first step had already overshot before the loss was measured",
        "From the batch size: 64 rows give about 4.5 bits",
    ],
    1,
    "Zero logits give equal probabilities, and the cost of equal probabilities among V options is log2 of V. That is the sanity check from When training goes wrong: a first loss near log of the number of classes means the start is honest, and a far larger one means the output starts with opinions. The entropy of the text is lower than this, which is what training reaches towards.",
    ["bigram"],
)

write(
    "recall/parsons-pairs.yaml",
    "id: parsons-pairs\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to turn a sequence of ids into a bigram model's inputs and targets, the sequence moved one step, and print them with their length. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("X, y = ids[1:], ids[:-1]")
    + "\nexplanation: |\n"
    + block("The inputs are every id but the last and the targets every id but the first, so target i is the id that followed input i; four pairs from five ids. The decoy swaps them, so the model would be trained to predict the character before, which is a different task and the wrong one for writing text forwards.")
    + "skills: [bigram]\n",
)

mcq(
    "mcq-why-shift-by-one",
    "A bigram model's targets are its inputs moved one step: `X, y = ids[:-1], ids[1:]`. What goes wrong if the targets are the inputs themselves?",
    [
        "Nothing: the model learns the same table either way, since the pairs contain the same ids",
        "The model learns to predict the character it was given, reaches almost zero loss and perfect accuracy, and its samples repeat one character forever: a loss too good to be true is a data bug",
        "The loss can't be computed, since the inputs and targets must differ",
        "Training is twice as slow, because every pair appears twice in the batch and the loop has to visit each one two times before the epoch is complete",
    ],
    1,
    "Predicting the input from the input is trivial: the table learns a diagonal and the loss falls to nearly zero. That is the signature, a result far better than the task allows. Sampling then feeds each character back in and gets itself out again. The loss computes fine, and nothing is slower; the model is simply solving the wrong problem.",
    ["bigram"],
)

mcq(
    "mcq-sampling-against-greedy",
    "From the same trained bigram table, drawing each next character from its probabilities gives text that looks like the grammar, while always taking the likeliest character gives `the the the`. Why the difference?",
    [
        "Greedy decoding uses a different table than sampling does",
        "Sampling follows the whole distribution, so less likely but valid characters appear and the text varies; greedy takes the single likeliest step every time, and with a one-character memory the likeliest steps form a short loop",
        "Sampling has a longer memory than greedy decoding, because the random draws let it remember which characters it has already produced, so it can avoid repeating itself in the way the greedy loop does",
        "Greedy decoding is only for models with at least two layers",
    ],
    1,
    "Both use the same table and the same one-character memory. Greedy is deterministic: after a space the likeliest character is t, after t it is h, after e it is a space, and the loop closes. Sampling takes the less likely branches in proportion to their probability, which is what makes the text look like the training data rather than its single most common path.",
    ["bigram"],
)

write(
    "recall/review-predict-scatter-add.yaml",
    f'''id: review-predict-scatter-add
type: predict_output
rev: 1
prompt: |
  Four output rows' gradients, all ones, go back into a five-row table with `np.add.at`. What does the program print?
code: |
{block(REVIEW_PREDICT)}expected_output: |
{block(REVIEW_PREDICT_OUT)}explanation: |
  Id 1 appears three times, so its row collects three ones; id 3 once; rows 0, 2 and 4 were never looked up and stay zero, so two rows of the table received any gradient. Rows that don't appear in a batch don't move: an embedding only ever learns about the tokens it sees.
skills: [embedding]
''',
)

mcq(
    "review-mcq-what-the-model-sees",
    "After encoding, what does a character-level language model receive, and what does it learn about each character?",
    [
        "Strings, and a rule for each letter of the alphabet",
        "Integer ids from a fixed vocabulary, and one learned vector per id; it knows nothing about a character except which row it is",
        "Integer ids whose numeric size carries meaning, so that characters with nearby ids are treated as similar from the start, which is why the vocabulary has to be sorted alphabetically",
        "One-hot vectors for every word",
    ],
    1,
    "Encoding reduces text to ids and the embedding gives each id a vector the loss shapes. The ids are labels, not quantities: sorting the vocabulary is only for reproducibility, and nothing about id 4 being near id 5 reaches the model, since each id picks its own row.",
    ["tokens"],
)

mcq(
    "review-mcq-positions",
    "Two sequences, 'ab' and 'ba', go through the same token table. When are their embeddings the same set of vectors, and what changes it?",
    [
        "Always the same set; only a bigger table changes it",
        "The same set without positions, since each character gets its row wherever it sits; adding a position vector to each slot makes them different sets",
        "Different sets already, because the lookup also records the order of the ids inside each vector, so a model that reads the vectors can recover where each one came from without any extra table",
        "The same set, and summing the vectors with positions added tells them apart",
    ],
    1,
    "A lookup carries no place: row a and row b are the same two vectors in either order. The position table adds a different vector to the first slot and the second, so a plus p0 and b plus p1 is not the set b plus p0 and a plus p1. A plain sum would still match in both orders, which is why the next layer does more than sum.",
    ["positions"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-text-becomes-numbers/exercise.yaml",
    f'''id: example-text-becomes-numbers
stage: worked_example
rev: 1
title: "Text becomes numbers"
prompt: |
  A corpus generated in code, a vocabulary that encodes and decodes it, an embedding checked against a one-hot matrix multiply and gradient-checked, a position table that tells 'ab' from 'ba', and a bigram table trained with Module 8's loop, read in bits per character, compared with counting, and sampled from. Press **Run**, then read how each part works.
steps:
  - label: "The corpus and the vocabulary"
    lines: "{ln('def make_corpus')}-{ln('return "".join(chars[int(i)] for i in ids)')}"
    note: "`make_corpus` draws who-did-what-where sentences from three short lists with a seed. `vocabulary` sorts the distinct characters and numbers them; `encode` and `decode` read that table in the two directions. Sorting is only so that every run gives the same ids."
  - label: "The embedding layer"
    lines: "{ln('class Embedding:')}-{ln('return [self.dW]')}"
    note: "One row of `dim` numbers per token. `forward` is `W[ids]`, a row per id. `backward` makes an empty gradient and scatter-adds each output row's gradient into the row that was looked up with `np.add.at`, so a row used twice gets both; it returns `None`, since integers have no gradient. The layer has the module's interface, so `Sequential`, `gradient_check` and `fit` take it as they are."
  - label: "Pairs, the split, bits, counting, sampling"
    lines: "{ln('def pairs')}-{ln('return decode(ids, chars)', ln('def greedy'))}"
    note: "`pairs` moves the text one step to make inputs and targets. `split_text` holds out the last tenth by position. `bits_per_char` divides nats by log 2. `unigram_bits` is the cost of guessing from character frequencies alone, and `counted_bigram_bits` the cost of a table of counted next-character frequencies, plus a tenth of a count so nothing unseen is impossible. `sample` draws each next character from the model's probabilities; `greedy` takes the likeliest."
  - label: "Round trip, lookup, gradient, check"
    lines: "{ln('text = make_corpus(200, seed=0)')}-{ln('gradient check of a table of logits')}"
    note: "23 characters, the space and the full stop among them, and the whole corpus decodes back to itself. The lookup for `cat` equals the one-hot rows times the table. Three ids with a repeat, gradients of ones: row 2 collects 8 (two rows of four ones) and row 5 collects 4. A table of logits used as a model passes the gradient check."
  - label: "Positions"
    lines: "{ln('positions = Embedding(8, 4, seed=2)')}-{ln('as unordered sets of vectors')}"
    note: "Seen as an unordered set of vectors, which is how attention will see them, `ab` and `ba` are the same two vectors without positions and two different pairs once a vector per place is added. A model that only summed them would still see no difference, since the same four vectors are added either way."
  - label: "The bigram model, trained, counted and sampled"
    lines: "{ln('X_train, y_train, X_val, y_val = split_text(X_all, y_all)')}-{ln('print("greedy:"')}"
    note: "The first loss is {FIRST_BITS:.2f} bits, a hair above log2 of 23 (4.52): a table near zero guesses nearly evenly. Guessing from character frequencies alone would cost {UNIGRAM_BITS:.2f}. Five epochs of Adam bring the held-out cost to {FINAL_BITS:.2f} bits with next-character accuracy {ACCURACY:.0%}, and a table of counted frequencies scores {COUNTED_BITS:.2f} on the same text: training reproduced counting, and bought the machinery. The sample follows the grammar's letter pairs; greedy decoding loops on `the the the`."
''',
)
write("exercises/example-text-becomes-numbers/solution.py", EXAMPLE)
write(
    "exercises/example-text-becomes-numbers/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the corpus, the checks, the training and the samples."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-embedding/exercise.yaml",
    f'''id: fill-embedding
stage: fill_in
rev: 1
title: "The embedding layer's lookup and gradient"
prompt: |
  `Embedding.forward` looks up one row of the table per id; `Embedding.backward` scatter-adds each output row's gradient into the row it came from. Replace each `...` so the program prints the three looked-up rows of a table whose entries are 0 to 14, then the first column of the gradient after three rows of gradients (ones, twos, threes) go back to ids 4, 1 and 4:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "`self.W[ids]` with an array of ids returns one row per id, in order, repeats included."
  - "`np.add.at(self.dW, self.ids, grad_out)` adds row i of `grad_out` into row `self.ids[i]` of `dW`, so row 4 collects 1 + 3."
skills: [embedding]
''',
)
write("exercises/fill-embedding/starter.py", FILL_STARTER)
write("exercises/fill-embedding/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-embedding/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the rows and the summed gradient."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_cases():
    """The lookup equals one-hot @ W for random ids, the gradient equals one-hot transposed @ grad_out, unused rows stay zero, and backward returns None."""
    Embedding = function("Embedding")
    rng = np.random.default_rng(1)
    table = Embedding(9, 4, seed=2)
    ids = rng.integers(0, 9, size=12)
    onehot = np.eye(9)[ids]
    assert np.allclose(table.forward(ids), onehot @ table.W)
    grad_out = rng.standard_normal((12, 4))
    assert table.backward(grad_out) is None
    assert np.allclose(table.dW, onehot.T @ grad_out)
    unused = [i for i in range(9) if i not in set(ids.tolist())]
    assert all(np.all(table.dW[i] == 0) for i in unused)
    assert table.parameters()[0] is table.W and table.gradients()[0] is table.dW
''',
)
write("exercises/fill-embedding/wrong/gradient-assigned-not-added.py", FILL_ASSIGNS)
write(
    "exercises/fill-embedding/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Embedding:\n    def __init__(self, n_tokens, dim, seed=0, scale=None):\n        self.W = np.zeros((n_tokens, dim))\n        self.dW = np.zeros_like(self.W)\n\n    def forward(self, ids):\n        return self.W[:len(ids)]\n\n    def backward(self, grad_out):\n        return None\n\n    def parameters(self):\n        return [self.W]\n\n    def gradients(self):\n        return [self.dW]\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-vocabulary-and-bits/exercise.yaml",
    f'''id: write-vocabulary-and-bits
stage: write
rev: 1
title: "A vocabulary, and bits per character"
prompt: |
  Write four functions: `vocabulary(text)`, returning the sorted list of distinct characters and the dict from character to id; `encode(text, stoi)`, text to a NumPy array of ids; `decode(ids, chars)`, ids (an array or a list) back to a string; and `bits_per_char(loss)`, a cross-entropy in nats divided by log 2. Called on the lines in the starter, the program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`sorted(set(text))` is the vocabulary; `enumerate` over it builds the dict."
  - "Decoding indexes `chars` with each id; an id that arrives as a NumPy integer still works as an index."
skills: [tokens, bigram]
''',
)
write("exercises/write-vocabulary-and-bits/starter.py", "import numpy as np\n\n\n# Write vocabulary, encode, decode and bits_per_char here, above the calls.\n\n\n" + WRITE_TAIL)
write("exercises/write-vocabulary-and-bits/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-vocabulary-and-bits/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the vocabulary, the ids and the bits."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_round_trips():
    """A random text round-trips, ids are sorted characters, encode returns an array, and bits convert from nats."""
    vocabulary = function("vocabulary")
    encode = vocabulary.__globals__["encode"]
    decode = vocabulary.__globals__["decode"]
    bits_per_char = vocabulary.__globals__["bits_per_char"]
    rng = np.random.default_rng(5)
    text = "".join(rng.choice(list("the quick brown fox."), size=200))
    chars, stoi = vocabulary(text)
    assert chars == sorted(set(text)) and all(stoi[c] == i for i, c in enumerate(chars))
    ids = encode(text, stoi)
    assert isinstance(ids, np.ndarray) and decode(ids, chars) == text and decode(ids.tolist(), chars) == text
    assert abs(bits_per_char(np.log(2)) - 1.0) < 1e-12 and abs(bits_per_char(np.log(1024)) - 10.0) < 1e-9
''',
)
write("exercises/write-vocabulary-and-bits/wrong/unsorted-vocabulary.py", WRITE_UNSORTED)
write("exercises/write-vocabulary-and-bits/wrong/bits-divided-by-log-10.py", WRITE_LOG10)
write(
    "exercises/write-vocabulary-and-bits/wrong/typed-in.py",
    "import numpy as np\n\n\ndef vocabulary(text):\n    return list(text), {{}}\n\n\ndef encode(text, stoi):\n    return np.zeros(len(text), dtype=int)\n\n\ndef decode(ids, chars):\n    return ''\n\n\ndef bits_per_char(loss):\n    return loss\n\n\n".replace("{{}}", "{}") + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-bigram-model/exercise.yaml",
    f'''id: build-a-bigram-model
stage: build
rev: 1
title: "A bigram model"
prompt: |
  Starting from a blank editor, paste Module 8's `Sequential`, `SoftmaxCrossEntropy`, `Adam`, `numeric_gradient`, `gradient_check`, `batches`, `evaluate` and `fit` as Checkpoint 8 left them, and the corpus below, then write:

  - `vocabulary(text)`: the sorted distinct characters and the dict from character to id. `encode(text, stoi)`: a NumPy array of ids. `decode(ids, chars)`: back to text.
  - `Embedding(n_tokens, dim, seed=0, scale=None)`: a table `W` of shape `(n_tokens, dim)` from `default_rng(seed).standard_normal` times `1 / sqrt(dim)` (or `scale`); `forward(ids)` returns `W[ids]`; `backward(grad_out)` sets `dW` by scatter-adding each row of `grad_out` into the row its id looked up and returns `None`; `parameters()` and `gradients()`.
  - `pairs(ids)`: `(ids[:-1], ids[1:])`. `split_text(X, y, held_out=0.1)`: the last `int(len(X) * held_out)` pairs held out, by position, the rest for training.
  - `bits_per_char(loss)`: nats to bits. `unigram_bits(ids, n_tokens)`: the entropy in bits of the character frequencies (`np.bincount` over `n_tokens`, zeros left out). `counted_bigram_bits(X_train, y_train, X_val, y_val, n_tokens)`: a table of a tenth plus the counts of each training pair, each row turned into probabilities, scored as mean negative log2 probability of the held-out pairs.
  - `sample(model, chars, stoi, start, length, rng)`: after `start`, `length` characters, each drawn with `rng.choice(len(chars), p=probs)` from the softmax of the model's logits for the previous character.

  ```python
  def make_corpus(n_sentences, seed):
      """A tiny world in text, who did what where, one sentence after another, drawn with a seed so nothing is downloaded."""
      rng = np.random.default_rng(seed)
      who = ["the cat", "the dog", "a bird", "my fox", "the owl"]
      did = ["sat", "ran", "slept", "hid", "sang"]
      where = ["on the mat", "in the box", "by the door", "under the bed", "near the pond"]
      return " ".join(f"{{rng.choice(who)}} {{rng.choice(did)}} {{rng.choice(where)}}." for _ in range(n_sentences))
  ```

  Then print:

  ```python
  text = make_corpus(200, seed=0)
  chars, stoi = vocabulary(text)
  V = len(chars)
  ids = encode(text, stoi)
  print(V, decode(ids, chars) == text, encode("owl", stoi).tolist())
  table = Embedding(V, 3, seed=1)
  table.forward(np.array([4, 4, 1]))
  table.backward(np.ones((3, 3)))
  print(table.dW[:, 0].tolist().count(0.0), table.dW[4, 0], table.dW[1, 0])
  loss = SoftmaxCrossEntropy()
  X_all, y_all = pairs(ids)
  X_train, y_train, X_val, y_val = split_text(X_all, y_all)
  print(len(X_train), len(X_val), bool((X_all[1:] == y_all[:-1]).all()), "gradient check:", "passes" if gradient_check(Sequential([Embedding(V, V, seed=1)]), loss, X_all[:8], y_all[:8]) < 1e-6 else "fails")
  model = Sequential([Embedding(V, V, seed=1)])
  history = fit(model, loss, Adam(0.1), X_train, y_train, X_val, y_val, epochs=5, batch_size=64)
  learned = bits_per_char(history["val_loss"][-1])
  baseline = unigram_bits(ids, V)
  counted = counted_bigram_bits(X_train, y_train, X_val, y_val, V)
  print(f"{{learned:.2f}} bits | beats the unigram baseline by at least 0.5: {{learned < baseline - 0.5}} | within 0.1 of the counted table: {{abs(learned - counted) < 0.1}}")
  print(repr(sample(model, chars, stoi, "the ", 40, np.random.default_rng(3))))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks test the round trip on other text, the lookup against one-hot rows and the gradient against their transpose, pairs and the split, the bits conversions and the unigram entropy on known distributions, the counted table on a tiny case, the trained model against the baseline and the counted table, the sample's length and alphabet, and that the same seeds repeat.
skills: [tokens, embedding, positions, bigram]
''',
)
write("exercises/build-a-bigram-model/starter.py", "")
write("exercises/build-a-bigram-model/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-bigram-model/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test imports the solution
# once (its training runs on import) and takes what it needs from that one
# import.


def module():
    return function("fit").__globals__


def test_the_output():
    """Prints the five lines (the sample follows from the same seeds)."""
    assert run() == {BUILD_OUT!r}


def test_tokens():
    """Other text round-trips, the vocabulary is sorted, encode returns an array of ids."""
    m = module()
    text = "a bird sang by the door. the owl hid."
    chars, stoi = m["vocabulary"](text)
    assert chars == sorted(set(text)) and all(stoi[c] == i for i, c in enumerate(chars))
    ids = m["encode"](text, stoi)
    assert isinstance(ids, np.ndarray) and ids.tolist() == [stoi[c] for c in text] and m["decode"](ids, chars) == text


def test_embedding():
    """The lookup is one-hot @ W, the gradient is one-hot.T @ grad_out, backward returns None, and a table of logits passes the gradient check."""
    m = module()
    rng = np.random.default_rng(2)
    table = m["Embedding"](7, 3, seed=1)
    assert table.W.shape == (7, 3) and 0.3 < table.W.std() < 0.9
    ids = rng.integers(0, 7, size=10)
    onehot = np.eye(7)[ids]
    assert np.allclose(table.forward(ids), onehot @ table.W)
    grad_out = rng.standard_normal((10, 3))
    assert table.backward(grad_out) is None and np.allclose(table.dW, onehot.T @ grad_out)
    net = m["Sequential"]([m["Embedding"](7, 7, seed=3)])
    assert m["gradient_check"](net, m["SoftmaxCrossEntropy"](), rng.integers(0, 7, size=6), rng.integers(0, 7, size=6)) < 1e-6


def test_pairs_split_and_bits():
    """pairs shifts by one, split_text holds out the last tenth in order, bits convert from nats, and the unigram entropy of four equal characters is 2 bits."""
    m = module()
    ids = np.arange(20)
    X, y = m["pairs"](ids)
    assert X.tolist() == list(range(19)) and y.tolist() == list(range(1, 20))
    X_train, y_train, X_val, y_val = m["split_text"](X, y, held_out=0.2)
    assert X_train.tolist() == list(range(16)) and X_val.tolist() == [16, 17, 18] and y_val.tolist() == [17, 18, 19]
    assert abs(m["bits_per_char"](np.log(2)) - 1.0) < 1e-12 and abs(m["bits_per_char"](np.log(8)) - 3.0) < 1e-12
    assert abs(m["unigram_bits"](np.array([0, 1, 2, 3] * 5), 4) - 2.0) < 1e-12
    assert abs(m["unigram_bits"](np.array([0, 0, 0, 0, 1, 1, 1, 1]), 6) - 1.0) < 1e-12


def test_counted_table():
    """On pairs that always go 0 -> 1 and 1 -> 0, with one held-out pair each way, the smoothed table scores the right bits."""
    m = module()
    X_train = np.array([0, 1] * 10)
    y_train = np.array([1, 0] * 10)
    expected = -np.log2(10.1 / 10.2)
    assert abs(m["counted_bigram_bits"](X_train, y_train, np.array([0, 1]), np.array([1, 0]), 2) - expected) < 1e-12


def test_the_trained_model():
    """The trained table beats the unigram baseline by half a bit, lands within a tenth of the counted table, samples the right length from the vocabulary, and repeats with the same seeds."""
    m = module()
    model, history, X_val, y_val, chars, stoi, ids, V = (m[name] for name in ("model", "history", "X_val", "y_val", "chars", "stoi", "ids", "V"))
    learned = m["bits_per_char"](history["val_loss"][-1])
    assert learned < m["unigram_bits"](ids, V) - 0.5
    assert abs(learned - m["counted_bigram_bits"](m["X_train"], m["y_train"], X_val, y_val, V)) < 0.1
    text = m["sample"](model, chars, stoi, "the ", 30, np.random.default_rng(9))
    assert len(text) == 34 and text.startswith("the ") and set(text) <= set(chars)
    again = m["Sequential"]([m["Embedding"](V, V, seed=1)])
    repeat = m["fit"](again, m["SoftmaxCrossEntropy"](), m["Adam"](0.1), m["X_train"], m["y_train"], X_val, y_val, epochs=2, batch_size=64)
    assert repeat["val_loss"] == history["val_loss"][:2]
''',
)
for key, code in BUILD_WRONGS.items():
    write(f"exercises/build-a-bigram-model/wrong/{key}.py", code)
write(
    "exercises/build-a-bigram-model/wrong/typed-in.py",
    "import numpy as np\n\n\ndef vocabulary(text):\n    return sorted(set(text)), {}\n\n\ndef encode(text, stoi):\n    return np.zeros(len(text), dtype=int)\n\n\ndef decode(ids, chars):\n    return ''\n\n\nclass Embedding:\n    def __init__(self, n_tokens, dim, seed=0, scale=None):\n        self.W = np.zeros((n_tokens, dim))\n        self.dW = np.zeros_like(self.W)\n\n\ndef fit(*args, **kwargs):\n    return {}\n\n\nmodel = history = X_val = y_val = chars = stoi = ids = V = X_train = y_train = None\n\n\n" + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-model-that-is-too-good/exercise.yaml",
    f'''id: debug-a-model-that-is-too-good
stage: debug
rev: 1
title: "A model that is too good to be true"
prompt: |
  The bigram model on the corpus. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the gradient check **fails**, because `Embedding.backward` assigns each output row's gradient to its row (`self.dW[self.ids] = grad_out`), so a row looked up twice in a batch keeps only the last gradient; the gradient of a shared row is the sum, which `np.add.at` gives. Fix that, and the check passes but the model is now **too good**: {STILL_SHIFT_BITS} bits per character with perfect next-character accuracy, and a sample that repeats one character, {STILL_SHIFT_SAMPLE}. A loss far better than the task allows is a data bug: `pairs` returns the ids twice, so the targets are the inputs and the model learns to predict the character it was given. The targets are the inputs moved one step, `ids[1:]`.
skills: [embedding, bigram]
''',
)
write("exercises/debug-a-model-that-is-too-good/starter.py", DEBUG_STARTER)
write("exercises/debug-a-model-that-is-too-good/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-model-that-is-too-good/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints a passing check, an honest held-out cost and a varied sample."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_pieces():
    """A row used twice gets the sum of both gradients, and the targets are the inputs moved one step."""
    pairs = function("pairs")
    Embedding = pairs.__globals__["Embedding"]
    table = Embedding(4, 2, seed=0)
    table.forward(np.array([1, 1, 3]))
    table.backward(np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]))
    assert table.dW.tolist() == [[0.0, 0.0], [4.0, 6.0], [0.0, 0.0], [5.0, 6.0]]
    X, y = pairs(np.array([7, 8, 9]))
    assert X.tolist() == [7, 8] and y.tolist() == [8, 9]
''',
)
write("exercises/debug-a-model-that-is-too-good/wrong/still-assigning.py", DEBUG_STILL_ASSIGN)
write("exercises/debug-a-model-that-is-too-good/wrong/still-unshifted.py", DEBUG_STILL_SHIFT)
write(
    "exercises/debug-a-model-that-is-too-good/wrong/typed-in.py",
    "import numpy as np\n\n\nclass Embedding:\n    def __init__(self, n_tokens, dim, seed=0, scale=None):\n        self.W = np.zeros((n_tokens, dim))\n        self.dW = np.zeros_like(self.W)\n\n    def forward(self, ids):\n        return self.W[ids]\n\n    def backward(self, grad_out):\n        return None\n\n\ndef pairs(ids):\n    return ids[:-1], ids[:-1]\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-encode-and-decode/exercise.yaml",
    f'''id: review-encode-and-decode
stage: review_code
rev: 1
title: "Encode and decode, from memory"
prompt: |
  Write `encode(text, stoi)`, text to a NumPy array of ids, and `decode(ids, chars)`, ids back to text. With the vocabulary of `"no pain no gain"` (its sorted distinct characters, numbered from 0), print the ids of `"pan"`, `"gain"` decoded from its own ids, and the text of `[0, 4, 5]`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [tokens]
''',
)
write("exercises/review-encode-and-decode/starter.py", "")
write("exercises/review-encode-and-decode/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-encode-and-decode/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the ids, the word and the text."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_round_trip():
    """Another text round-trips through any vocabulary that holds its characters."""
    encode = function("encode")
    decode = encode.__globals__["decode"]
    chars = sorted(set("the quick brown fox jumps"))
    stoi = {{c: i for i, c in enumerate(chars)}}
    ids = encode("quick fox", stoi)
    assert isinstance(ids, np.ndarray) and decode(ids, chars) == "quick fox" and decode(ids.tolist(), chars) == "quick fox"
''',
)
write("exercises/review-encode-and-decode/wrong/off-by-one.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-encode-and-decode/wrong/typed-in.py",
    "import numpy as np\n\n\ndef encode(text, stoi):\n    return np.zeros(len(text), dtype=int)\n\n\ndef decode(ids, chars):\n    return 'gain'\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.tf.tokens-and-embeddings written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
