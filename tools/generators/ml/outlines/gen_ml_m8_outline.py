"""Outlines Module 8 of the ML Foundations track, neural networks from scratch:
planned topic.yaml files, the module in the track file, and the spec's prose
bullet turned into a table. Run from the repository root under uv. Never
overwrites a topic that isn't a planned outline."""

import pathlib

import yaml

ROOT = pathlib.Path(".")
TOPICS = ROOT / "content" / "topics"
TRACK_PATH = ROOT / "content" / "tracks" / "ml-foundations.yaml"
SPEC = ROOT / "docs" / "specs" / "ml-foundations.md"

MODULE = {
    "id": "ml.m8",
    "title": "Neural networks from scratch",
    "topics": [
        "ml.nn.neurons-and-layers",
        "ml.nn.backward-layers",
        "ml.nn.initialization-and-activations",
        "ml.nn.training-loop",
        "ml.nn.regularization",
        "ml.nn.convolution",
        "ml.nn.debugging-training",
    ],
    "checkpoint": "ml.m8.checkpoint",
}

# id: (kind, title, summary, prerequisites, minutes, objectives, "you'll be able to" for the spec)
OUTLINES = {
    "ml.nn.neurons-and-layers": (
        "topic", "Neurons, layers and a network's shape",
        "A neuron as a weighted sum through an activation, a layer as a matrix multiply plus a bias, a network as layers in a list: the forward pass written as objects, the shape of the data at every step, and the parameter count that falls out of the layer sizes.",
        ["ml.m4.checkpoint", "ml.m7.checkpoint"], 50,
        ["Write a neuron and a dense layer as a weighted sum plus a bias through an activation, and say what each weight means.",
         "Compose layers into a network object with a forward pass, and track the shape of a batch through it.",
         "Count a network's parameters from its layer sizes.",
         "Explain why a network with no activation between its layers is one linear layer in disguise."],
        "write a neuron and a dense layer in NumPy; compose layers into a network with a forward pass and track shapes through it; count parameters; explain why the hidden activations are what make depth matter"),
    "ml.nn.backward-layers": (
        "topic", "Layers that carry their gradient",
        "Each layer keeps what it needs from the forward pass and implements backward, the gradient of the loss with respect to its input and its parameters; loss layers for mean squared error and softmax cross-entropy; a Sequential that runs the chain rule for you; and a gradient check on every piece.",
        ["ml.nn.neurons-and-layers"], 60,
        ["Implement backward for a dense layer and for ReLU, sigmoid and tanh, caching what the forward pass needs.",
         "Implement mean squared error and softmax cross-entropy as loss layers with their gradients.",
         "Chain the layers' backward calls in reverse to get every parameter's gradient, and check each against a numeric derivative.",
         "Say what the chain rule does at each layer boundary and why the backward pass costs about twice the forward."],
        "implement backward for dense and activation layers; implement MSE and softmax cross-entropy with their gradients; chain backward calls and gradient-check them; explain the chain rule at a layer boundary"),
    "ml.nn.initialization-and-activations": (
        "topic", "Starting weights and activation functions",
        "Why a network started at zero can't learn, why weights that are too big or too small kill a deep network's signal, the Xavier and He rules that keep it alive, and what sigmoid, tanh and ReLU each do to the gradient flowing back.",
        ["ml.nn.backward-layers"], 50,
        ["Show that zero or identical starting weights keep every neuron in a layer identical forever, and say why.",
         "Measure how the size of activations and gradients changes layer by layer under too-small, too-large and Xavier or He starting weights.",
         "Choose an activation function and its starting scale, and say what saturation and dead ReLUs are.",
         "Explain why these choices matter more as a network gets deeper."],
        "show why zero weights can't learn; measure activation and gradient scale through depth under different starting weights; choose an activation and its He or Xavier scale; explain saturation and dead ReLUs"),
    "ml.nn.training-loop": (
        "topic", "The training loop",
        "Epochs, mini-batches and shuffling; a fit function that trains a network with an optimizer and records the loss; evaluating on data the network hasn't seen; accuracy and a loss curve read from text; and what the batch size and the learning rate change.",
        ["ml.nn.backward-layers"], 55,
        ["Write a training loop over epochs and shuffled mini-batches, with a stochastic gradient descent or Adam step per batch.",
         "Split data into training and validation sets, and evaluate loss and accuracy on the validation set every epoch.",
         "Read a loss curve: converging, diverging, stalled.",
         "Say what the batch size trades (noise against speed) and how the learning rate interacts with it."],
        "write a mini-batch training loop with shuffling; split data and evaluate on a validation set; read a loss curve; say what batch size and learning rate trade"),
    "ml.nn.regularization": (
        "topic", "Regularization: learning what generalizes",
        "Overfitting seen as training loss falling while validation loss rises; weight decay; dropout with its train and eval modes; early stopping; and more data as the regularizer that always works.",
        ["ml.nn.training-loop"], 50,
        ["Produce and recognize overfitting from the training and validation curves.",
         "Implement weight decay as a term in the gradient, and inverted dropout as a layer with train and eval modes.",
         "Implement early stopping on validation loss with patience.",
         "Say what each regularizer assumes about the data and when it hurts."],
        "recognize overfitting from the two curves; implement weight decay and dropout with train and eval modes; implement early stopping; say what each regularizer assumes"),
    "ml.nn.convolution": (
        "topic", "Convolutions: a layer that reads images",
        "A 2-D cross-correlation by hand, a kernel as a feature detector, padding and stride, why a convolutional layer has far fewer parameters than a dense one on an image, pooling, and the forward and backward pass of a small convolutional layer checked numerically.",
        ["ml.nn.backward-layers"], 60,
        ["Compute a 2-D cross-correlation by hand and in code, and say what an edge-detecting kernel does.",
         "Count the parameters of a convolutional layer against a dense layer on the same image, and say where the saving comes from.",
         "Implement the forward and backward pass of a single-channel convolutional layer and gradient-check it.",
         "Say what pooling and stride do to the shape and to what the network can see."],
        "compute a 2-D cross-correlation and explain an edge kernel; count a conv layer's parameters against a dense layer's; implement and gradient-check a conv layer; say what pooling and stride do"),
    "ml.nn.debugging-training": (
        "topic", "When training goes wrong",
        "A checklist for a network that won't learn: overfit a single batch first, check the gradients, check the data, read the curves for a learning rate that is too high or too low, watch for dead ReLUs and exploding gradients, and change one thing at a time.",
        ["ml.nn.training-loop", "ml.nn.initialization-and-activations"], 50,
        ["Diagnose a learning rate that is too high or too low from the loss curve, and fix it.",
         "Use the overfit-one-batch test and the gradient check to tell a bug from a hard problem.",
         "Detect dead ReLUs and exploding gradients from activation and gradient statistics, and apply the standard fixes.",
         "Find a data bug (shuffled labels, unscaled inputs) from what training does, and say why each one fools a network."],
        "diagnose and fix a bad learning rate from the curve; use overfit-one-batch and the gradient check; detect dead ReLUs and exploding gradients; find a data bug from how training behaves"),
    "ml.m8.checkpoint": (
        "checkpoint", "Checkpoint 8: a network that reads digits",
        "Build the layers, the loss, the training loop and the regularizers from the module, train a small network on noisy, shifted images of the ten digits, reach the accuracy bar on images it hasn't seen, and find three bugs in a training script that won't learn.",
        ["ml.nn.regularization", "ml.nn.convolution", "ml.nn.debugging-training"], 150,
        ["Build dense and convolutional layers with forward and backward passes, softmax cross-entropy, and a mini-batch training loop with Adam, weight decay and dropout, and gradient-check the pieces.",
         "Train the network on the module's digit images, with a seed, to at least the accuracy bar on a held-out set, within the time the browser allows.",
         "Find and fix three bugs in a training script that won't learn (weights started at zero, dropout left on at evaluation, a learning rate ten times too high), and explain backpropagation and regularization in your own words."],
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
if not any(module["id"] == "ml.m8" for module in track["modules"]):
    track["modules"].append(MODULE)
    TRACK_PATH.write_bytes(dump(track).encode("utf-8"))
    print("wrote", TRACK_PATH)
else:
    print("track already has ml.m8")

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
if "## Module 8: Neural networks from scratch" not in spec:
    rows = []
    for number, topic_id in enumerate(MODULE["topics"], start=50):
        kind, title, summary, prereqs, minutes, objectives, able = OUTLINES[topic_id]
        needs = ", ".join(f"`{p}`" for p in prereqs)
        rows.append(f"| {number} | {title} | `{topic_id}` | {needs} | {able} |")
    section = (
        "## Module 8: Neural networks from scratch\n\n"
        "Module 4 built a two-layer network by hand to learn the calculus; this module builds networks the way libraries do, as layers that each know their forward and backward pass, and trains them properly: starting weights that keep the signal alive, mini-batches and shuffling, a validation set, regularization, a convolutional layer for images, and a checklist for when training fails. Everything runs in the browser in NumPy with a seed; the checks gradient-check the pieces and hold a network to an accuracy bar on data it hasn't seen, rather than to exact numbers after many steps.\n\n"
        "| # | Topic | ID | Needs | You'll be able to… |\n"
        "| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n"
        "**Checkpoint 8: a network that reads digits** (`ml.m8.checkpoint`). Build dense and convolutional layers with their backward passes, softmax cross-entropy, and a mini-batch training loop with Adam, weight decay and dropout; gradient-check the pieces; train on the module's digit images (a pixel font for the ten digits, shifted and noised with a seed, so no dataset has to be downloaded) to the accuracy bar on a held-out set; find three bugs in a training script that won't learn; and explain backpropagation and regularization. The way through for a stuck learner, as in the earlier checkpoints: a solved sibling, steps, fresh versions.\n\n"
    )
    old_bullet = "- **8. Neural networks from scratch:** a neuron, a layer, a loss; backpropagation by hand and in code; training loops; regularization; a small network that reads digits.\n"
    assert old_bullet in spec, "the Module 8 prose bullet has changed"
    spec = spec.replace(old_bullet, "")
    old_sentence = "as Modules 3 to 7 had before they were written (all five on 2026-11-10)."
    assert old_sentence in spec, "the later-modules sentence has changed"
    spec = spec.replace(old_sentence, "as Modules 3 to 7 had before they were written (all five on 2026-11-10) and Module 8 has (outlined 2026-11-10).")
    assert spec.count("## Later modules") == 1
    spec = spec.replace("## Later modules", section + "## Later modules")
    SPEC.write_bytes(spec.encode("utf-8"))
    print("wrote", SPEC)
else:
    print("spec already has Module 8")
