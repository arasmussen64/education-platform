"""Outlines Module 9 of the ML Foundations track, transformers: planned
topic.yaml files, the module in the track file, and the spec's prose bullet
turned into a table. Run from the repository root under uv. Never overwrites
a topic that isn't a planned outline."""

import pathlib

import yaml

ROOT = pathlib.Path(".")
TOPICS = ROOT / "content" / "topics"
TRACK_PATH = ROOT / "content" / "tracks" / "ml-foundations.yaml"
SPEC = ROOT / "docs" / "specs" / "ml-foundations.md"

MODULE = {
    "id": "ml.m9",
    "title": "Transformers",
    "topics": [
        "ml.tf.tokens-and-embeddings",
        "ml.tf.attention",
        "ml.tf.transformer-block",
        "ml.tf.language-model",
        "ml.tf.tokenizers",
        "ml.tf.generation-and-evaluation",
        "ml.tf.scaling",
    ],
    "checkpoint": "ml.m9.checkpoint",
}

# id: (kind, title, summary, prerequisites, minutes, objectives, "you'll be able to" for the spec)
OUTLINES = {
    "ml.tf.tokens-and-embeddings": (
        "topic", "Tokens, embeddings and positions",
        "Text becomes integers through a vocabulary; an embedding is a lookup into a matrix (a one-hot row times the matrix) whose gradient scatters back into the rows that were used; positions get a second table; and the first language model, a bigram table of next-character logits, is trained with the module's loop and sampled from.",
        ["ml.m8.checkpoint"], 50,
        ["Build a character vocabulary, encode text to integers and decode it back, and say what a token is.",
         "Implement an embedding layer with the module's interface, forward as a lookup and backward as a scatter-add into the rows used, and gradient-check it.",
         "Add a learned position table and say why a model that sums embeddings needs one.",
         "Train a bigram model on a corpus generated in code, read its loss in bits per character, and sample from it."],
        "encode text as tokens and back; implement an embedding layer with its scatter-add gradient; add learned positions; train and sample a bigram model"),
    "ml.tf.attention": (
        "topic", "Attention from scratch",
        "Queries, keys and values as three linear maps of the same rows; scaled dot-product scores; a softmax over positions that turns scores into weights; the causal mask that stops a position from seeing its future; the weighted sum of values; the whole thing as a layer with a backward pass that passes the gradient check.",
        ["ml.tf.tokens-and-embeddings"], 60,
        ["Compute single-head attention by hand for a few positions: scores, the scaling by the square root of the key size, the softmax, the weighted sum.",
         "Apply the causal mask and say what it forbids and why a language model needs it.",
         "Implement attention as a layer with forward, backward, parameters and gradients, and gradient-check it.",
         "Read an attention weight matrix and say what it means for one position to attend to another."],
        "compute scaled dot-product attention by hand; apply the causal mask; implement attention as a gradient-checked layer; read attention weights"),
    "ml.tf.transformer-block": (
        "topic", "Heads, residuals and the transformer block",
        "Several attention heads in parallel, each a slice of the model's width, concatenated; residual connections that give the gradient a straight road back; layer normalization and its gradient; the position-wise MLP; the block assembled from the module's layers, gradient-checked, and its parameter count from the model's width.",
        ["ml.tf.attention"], 60,
        ["Split the width into heads, run attention per head and concatenate, and say what heads buy.",
         "Implement residual connections and layer normalization with their backward passes, and say what each does to the gradient and the activations.",
         "Assemble a transformer block (attention, residual, norm, MLP, residual, norm) that passes the gradient check.",
         "Count a block's parameters from the width, the number of heads and the MLP's size."],
        "implement multi-head attention, residual connections and layer norm with their gradients; assemble a gradient-checked transformer block; count its parameters"),
    "ml.tf.language-model": (
        "topic", "Training a tiny language model",
        "Next-token prediction as a classification at every position; the loss over a sequence; batches of windows cut from one corpus; a two-block transformer trained with the module's loop and Adam; the loss curve in bits per character against a held-out slice; and samples drawn with a temperature, on a corpus generated in code so nothing is downloaded.",
        ["ml.tf.transformer-block"], 60,
        ["Turn a corpus into training windows and targets shifted by one, and say why the targets are the inputs moved one step.",
         "Compute the loss over every position of a batch of sequences and convert it to bits per character.",
         "Train a two-block transformer on the module's corpus to a held-out loss bar within the time the browser allows, with a seed.",
         "Sample from the model one token at a time with a temperature, and say what the temperature changes."],
        "cut a corpus into windows and shifted targets; compute the loss over a sequence; train a two-block transformer to a held-out loss bar; sample with a temperature"),
    "ml.tf.tokenizers": (
        "topic", "Tokenizers: byte-pair encoding",
        "Characters, words and subwords as three ways to cut text; the byte-pair encoding loop that merges the most frequent pair until the vocabulary is full; encoding and decoding that round-trip; the trade between vocabulary size and sequence length; and why the tokenizer is part of the model.",
        ["ml.tf.tokens-and-embeddings"], 50,
        ["Count pair frequencies and perform the merges of byte-pair encoding by hand on a small corpus.",
         "Implement a tokenizer that learns merges, encodes text to tokens and decodes it back, and check the round trip.",
         "Measure how the vocabulary size trades against the length of the encoded corpus, and say what each costs the model.",
         "Say why numbers, rare words and other languages come out in odd pieces, and why a model and its tokenizer can't be separated."],
        "perform byte-pair merges by hand; implement a tokenizer that learns, encodes and decodes; measure vocabulary size against sequence length; say why the tokenizer is part of the model"),
    "ml.tf.generation-and-evaluation": (
        "topic", "Generating and judging text",
        "Greedy decoding, temperature, top-k and nucleus sampling as choices over the same probabilities; why a small model repeats itself; held-out loss, bits per character and perplexity as the honest measure; comparing two models on the same held-out text; and what a model's samples can and can't tell you.",
        ["ml.tf.language-model"], 50,
        ["Implement greedy, temperature, top-k and nucleus decoding over one model's probabilities and say what each keeps and throws away.",
         "Explain why a model falls into repetition and what the decoding choice does about it.",
         "Compute perplexity from a held-out loss and say what it means in words.",
         "Compare two trained models on the same held-out text and defend the comparison."],
        "implement greedy, temperature, top-k and nucleus decoding; explain repetition; compute and read perplexity; compare two models on held-out text"),
    "ml.tf.scaling": (
        "topic", "What scaling changes",
        "A transformer's parameter count from its width, depth, vocabulary and context; training FLOPs as six times parameters times tokens; attention's quadratic cost in the context length; the memory of activations and of the key-value cache at inference; warmup and cosine learning-rate schedules; and a measured mini scaling study on the module's models.",
        ["ml.tf.language-model", "ml.hw.cost-of-a-model"], 50,
        ["Count a transformer's parameters from its hyperparameters and say which terms grow with width, depth, vocabulary and context.",
         "Estimate training FLOPs from parameters and tokens, and inference memory from the key-value cache, and say where the context length bites.",
         "Implement learning-rate warmup and cosine decay and say what each protects against.",
         "Train three sizes of the module's model on the same corpus, plot held-out loss against size, and say what changed and what didn't."],
        "count a transformer's parameters and FLOPs; estimate the key-value cache; implement warmup and cosine decay; run a mini scaling study"),
    "ml.m9.checkpoint": (
        "checkpoint", "Checkpoint 9: a tiny transformer that writes",
        "Build the tokenizer, the embedding, attention, the transformer block and the training loop from the module, train a small transformer on the module's corpus to the held-out loss bar, generate text from it, and find three bugs in a model that writes nonsense.",
        ["ml.tf.language-model", "ml.tf.tokenizers", "ml.tf.generation-and-evaluation", "ml.tf.scaling"], 150,
        ["Build a byte-pair tokenizer, an embedding with positions, multi-head causal attention, the transformer block and the loss over a sequence, and gradient-check the pieces.",
         "Train the model on the module's corpus, with a seed, to at least the held-out loss bar within the time the browser allows, and generate from it with a temperature.",
         "Find and fix three bugs in a model that writes nonsense (a missing causal mask, a softmax over the wrong axis, positions never added), and explain attention and why the mask matters in your own words."],
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
if not any(module["id"] == "ml.m9" for module in track["modules"]):
    track["modules"].append(MODULE)
    TRACK_PATH.write_bytes(dump(track).encode("utf-8"))
    print("wrote", TRACK_PATH)
else:
    print("track already has ml.m9")

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
if "## Module 9: Transformers" not in spec:
    rows = []
    for number, topic_id in enumerate(MODULE["topics"], start=57):
        kind, title, summary, prereqs, minutes, objectives, able = OUTLINES[topic_id]
        needs = ", ".join(f"`{p}`" for p in prereqs)
        rows.append(f"| {number} | {title} | `{topic_id}` | {needs} | {able} |")
    section = (
        "## Module 9: Transformers\n\n"
        "Module 8 built networks as layers that read images; this module builds the layer that reads sequences, attention, assembles the transformer block around it, and trains a tiny language model on a corpus generated in code, so nothing is downloaded and no licence has to be cleared. Everything runs in the browser in NumPy with a seed; the checks gradient-check attention and the block, hold a model to a held-out loss bar rather than to exact numbers after many steps, and check tokenizers by their round trip.\n\n"
        "| # | Topic | ID | Needs | You'll be able to… |\n"
        "| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n"
        "**Checkpoint 9: a tiny transformer that writes** (`ml.m9.checkpoint`). Build the tokenizer, the embedding with positions, multi-head causal attention, the transformer block and the loss over a sequence; gradient-check the pieces; train on the module's corpus to the held-out loss bar and generate from the model with a temperature; find three bugs in a model that writes nonsense (a missing causal mask, a softmax over the wrong axis, positions never added); and explain attention and why the mask matters. The way through for a stuck learner, as in the earlier checkpoints: a solved sibling, steps, fresh versions.\n\n"
    )
    old_bullet = "- **9. Transformers:** embeddings, attention, the transformer block; training a tiny language model; tokenizers; what scaling changes.\n"
    assert old_bullet in spec, "the Module 9 prose bullet has changed"
    spec = spec.replace(old_bullet, "")
    old_sentence = "as Modules 3 to 8 had before they were written (all six on 2026-11-10)."
    assert old_sentence in spec, "the later-modules sentence has changed"
    spec = spec.replace(old_sentence, "as Modules 3 to 8 had before they were written (all six on 2026-11-10) and Module 9 has (outlined 2026-11-10).")
    assert spec.count("## Later modules") == 1
    spec = spec.replace("## Later modules", section + "## Later modules")
    SPEC.write_bytes(spec.encode("utf-8"))
    print("wrote", SPEC)
else:
    print("spec already has Module 9")
