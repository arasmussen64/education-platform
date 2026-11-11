"""Writes the ML Foundations track file and planned outlines for its first
two modules (docs/specs/ml-foundations.md). Run from the repository root.
Never overwrites a topic that isn't a planned outline."""

import pathlib

import yaml

ROOT = pathlib.Path(".")
TOPICS = ROOT / "content" / "topics"

TRACK = {
    "id": "ml-foundations",
    "title": "Machine Learning Foundations",
    "summary": "The math and the Python that machine learning is made of, from fractions to gradient descent, every topic proven in code.",
    "order": 3,
    "modules": [
        {
            "id": "ml.m1",
            "title": "Math refresher, in Python",
            "topics": [
                "ml.math.arithmetic",
                "ml.math.algebra",
                "ml.math.functions",
                "ml.math.exponents-and-logs",
                "ml.math.probability-and-statistics",
                "ml.math.vectors-and-matrices",
                "ml.math.calculus",
            ],
            "checkpoint": "ml.m1.checkpoint",
        },
        {
            "id": "ml.m2",
            "title": "Intermediate Python",
            "topics": [
                "ml.py.comprehensions",
                "ml.py.classes",
                "ml.py.dataclasses-and-typing",
                "ml.py.iterators-and-generators",
                "ml.py.functions-as-values",
                "ml.py.writing-tests",
                "ml.py.json-and-nested-data",
            ],
            "checkpoint": "ml.m2.checkpoint",
        },
        {
            "id": "ml.m3",
            "title": "Linear algebra for ML",
            "topics": [
                "ml.la.numpy-arrays",
                "ml.la.vectors",
                "ml.la.matrices-as-maps",
                "ml.la.systems",
                "ml.la.least-squares",
                "ml.la.eigen",
                "ml.la.pca",
            ],
            "checkpoint": "ml.m3.checkpoint",
        },
        {
            "id": "ml.m4",
            "title": "Calculus for ML",
            "topics": [
                "ml.calc.derivatives",
                "ml.calc.partials-and-gradient",
                "ml.calc.descent-in-many-dimensions",
                "ml.calc.chain-rule",
                "ml.calc.loss-functions",
                "ml.calc.backpropagation",
                "ml.calc.optimizers",
            ],
            "checkpoint": "ml.m4.checkpoint",
        },
    ],
}

# id: (kind, title, summary, prerequisites, minutes, objectives)
OUTLINES = {
    "ml.math.arithmetic": (
        "topic", "Arithmetic",
        "Fractions, decimals and percentages, computed in Python, in the right order.",
        ["py.arithmetic"], 45,
        ["Compute with fractions, decimals and percentages in Python.",
         "Apply the order of operations, and change it with parentheses.",
         "Work out a percentage of an amount and a percentage change, and round sensibly."]),
    "ml.math.algebra": (
        "topic", "Algebra",
        "Solve equations by undoing, check by substituting, and rearrange formulas.",
        ["ml.math.arithmetic"], 45,
        ["Solve a linear equation by undoing what was done to the unknown.",
         "Check an answer by substituting it back.",
         "Rearrange a formula to make another variable the subject.",
         "Apply the rules for multiplying powers."]),
    "ml.math.functions": (
        "topic", "Functions",
        "A function as a rule from input to output: lines, tables of values and composition.",
        ["ml.math.algebra", "py.return-values"], 45,
        ["Treat a function as a rule from input to output, and evaluate it.",
         "Read a line's slope and intercept, and say what each means.",
         "Put one function inside another.",
         "Make a table of values with a loop."]),
    "ml.math.exponents-and-logs": (
        "topic", "Exponents and logarithms",
        "Powers and their undoing: roots, logarithms, growth and decay, and why ML adds logs.",
        ["ml.math.functions"], 45,
        ["Use powers, roots and negative exponents.",
         "Say what a logarithm is, and compute one.",
         "Turn products into sums with the log rules.",
         "Model growth and decay in code, and say why machine learning adds log-probabilities."]),
    "ml.math.probability-and-statistics": (
        "topic", "Probability and statistics",
        "Mean, median and spread from a list; chance by counting; base rates with a table of 1,000 people.",
        ["ml.math.arithmetic", "py.list-algorithms"], 50,
        ["Compute mean, median and standard deviation from a list.",
         "Work out a probability by counting outcomes.",
         "Multiply probabilities for independent events.",
         "Reason about base rates with a table of 1,000 people."]),
    "ml.math.vectors-and-matrices": (
        "topic", "Vectors and matrices",
        "Vectors as lists and matrices as lists of lists: adding, scaling, the dot product, shapes and multiplication.",
        ["ml.math.arithmetic", "py.nested-data"], 50,
        ["Add and scale vectors held as lists.",
         "Compute a dot product and a vector's length.",
         "Hold a matrix as a list of lists, and read its shape.",
         "Multiply a matrix by a vector and by a matrix with loops, checking the shapes."]),
    "ml.math.calculus": (
        "topic", "Calculus",
        "The slope of a curve at a point, the power rule checked in code, and finding a minimum by going downhill.",
        ["ml.math.functions", "py.while-loops"], 50,
        ["Estimate a function's slope at a point from two nearby values.",
         "Check the power rule numerically.",
         "Read the sign of the derivative as going up or going down.",
         "Find a minimum by stepping against the slope."]),
    "ml.m1.checkpoint": (
        "checkpoint", "Checkpoint 1: fit a line",
        "Find the line that fits some points best by stepping downhill on the error.",
        ["ml.math.exponents-and-logs", "ml.math.probability-and-statistics",
         "ml.math.vectors-and-matrices", "ml.math.calculus"], 90,
        ["Fit a slope and an intercept to points by gradient descent, and print both rounded.",
         "Find and fix the mistakes in a statistics report: its mean, median and spread.",
         "Explain why stepping against the derivative finds the bottom of a valley."]),
    "ml.py.comprehensions": (
        "topic", "Comprehensions",
        "List, dict and set comprehensions, and when a loop is clearer.",
        ["py.m5.checkpoint"], 45,
        ["Write list, dict and set comprehensions with conditions.",
         "Say when a plain loop is clearer.",
         "Avoid the nested-comprehension trap."]),
    "ml.py.classes": (
        "topic", "Classes and objects",
        "Define a class with attributes and methods, and explain self.",
        ["py.m6.checkpoint"], 60,
        ["Define a class with __init__, attributes and methods.",
         "Explain self, and tell a class from an instance.",
         "Give a class a readable __repr__."]),
    "ml.py.dataclasses-and-typing": (
        "topic", "Dataclasses and type hints",
        "Records with @dataclass, and type hints that a checker can read.",
        ["ml.py.classes"], 45,
        ["Declare a record with @dataclass.",
         "Annotate parameters and return values, and read a checker's error.",
         "Say what type hints do and don't do when the program runs."]),
    "ml.py.iterators-and-generators": (
        "topic", "Iterators and generators",
        "What for really calls, and generators that produce values one at a time.",
        ["ml.py.comprehensions"], 50,
        ["Explain what for really calls.",
         "Write a generator with yield, and read a stream lazily.",
         "Say why a generator can be used once."]),
    "ml.py.functions-as-values": (
        "topic", "Functions as values",
        "Passing functions around: sort keys, lambda, and a decorator that times a call.",
        ["ml.py.comprehensions"], 50,
        ["Pass a function to another function, and sort with a key.",
         "Use lambda where it's clearer, and name the function where it isn't.",
         "Write a decorator that times a call."]),
    "ml.py.writing-tests": (
        "topic", "Writing tests",
        "pytest-style tests for a function, its edge cases, and a fixture.",
        ["py.m6.checkpoint"], 50,
        ["Write pytest-style tests for a function, including its edge cases.",
         "Use a fixture.",
         "Say what a test proves and what it can't."]),
    "ml.py.json-and-nested-data": (
        "topic", "JSON and nested data",
        "Read and write JSON, walk nested data safely, and validate what came in.",
        ["ml.py.dataclasses-and-typing", "py.csv-data"], 50,
        ["Read and write JSON.",
         "Walk nested lists and dicts safely.",
         "Turn records into dataclasses and back, validating what came in."]),
    "ml.m2.checkpoint": (
        "checkpoint", "Checkpoint 2: a small data library",
        "A Dataset class that loads JSON records, iterates lazily, summarizes a column and writes a report.",
        ["ml.py.iterators-and-generators", "ml.py.functions-as-values",
         "ml.py.writing-tests", "ml.py.json-and-nested-data"], 120,
        ["Build a Dataset class from a spec, with tests.",
         "Find and fix three bugs across a class's methods.",
         "Explain the difference between a class, an instance and a generator."]),
    "ml.la.numpy-arrays": (
        "topic", "NumPy arrays",
        "Arrays with a shape and a dtype: indexing, slicing, elementwise arithmetic and broadcasting, and why vectorized code beats a loop.",
        ["ml.py.comprehensions", "ml.math.vectors-and-matrices"], 50,
        ["Make arrays from lists and ranges, and read their shape and dtype.",
         "Index and slice arrays, in one and two dimensions.",
         "Do arithmetic on whole arrays at once, and say what broadcasting does.",
         "Replace a loop over numbers with one array operation, and say why it's faster."]),
    "ml.la.vectors": (
        "topic", "Vectors: length, angle and dot product",
        "Norms and unit vectors, the dot product as similarity, the angle between vectors, and projecting one onto another.",
        ["ml.la.numpy-arrays", "ml.math.exponents-and-logs"], 50,
        ["Compute a vector's length and make a unit vector.",
         "Compute a dot product and read it as a similarity.",
         "Find the angle between two vectors, and what a dot product of zero means.",
         "Project one vector onto another."]),
    "ml.la.matrices-as-maps": (
        "topic", "Matrices as transformations",
        "A matrix as a function on vectors: rotations, scalings and shears as pictures, composition as multiplication, the inverse and the determinant.",
        ["ml.la.vectors"], 55,
        ["Apply a matrix to a vector, and draw where the grid goes.",
         "Build rotation, scaling and shear matrices, and compose them by multiplying.",
         "Say what the identity and the inverse do, and when there is no inverse.",
         "Read the determinant as how much area is scaled."]),
    "ml.la.systems": (
        "topic", "Systems of linear equations",
        "Ax = b: elimination by hand on a small system, np.linalg.solve on a large one, and when there is no solution or many.",
        ["ml.la.matrices-as-maps", "ml.math.algebra"], 50,
        ["Write a system of equations as Ax = b.",
         "Solve a small system by elimination, by hand and in code.",
         "Solve a large one with np.linalg.solve, and check the answer.",
         "Say, from the rank, when a system has no solution or infinitely many."]),
    "ml.la.least-squares": (
        "topic", "Projections and least squares",
        "Projecting onto a line and a plane, the normal equations, and the line fit of Checkpoint 1 found in one step.",
        ["ml.la.systems", "ml.m1.checkpoint"], 55,
        ["Project a vector onto a line and onto a plane.",
         "Write and solve the normal equations for a fit.",
         "Fit a line and a plane with np.linalg.lstsq, and check it against gradient descent.",
         "Say what least squares minimizes and why the solution is a projection."]),
    "ml.la.eigen": (
        "topic", "Eigenvalues and eigenvectors",
        "The directions a matrix only stretches, found with np.linalg.eig, and what they say about repeated transformations.",
        ["ml.la.matrices-as-maps"], 55,
        ["Say what an eigenvector and its eigenvalue are, and check a pair by multiplying.",
         "Find them with np.linalg.eig, and read complex ones as rotation.",
         "Predict what applying a matrix many times does from its eigenvalues.",
         "Diagonalize a matrix and say what that buys."]),
    "ml.la.pca": (
        "topic", "PCA: what eigenvalues mean for data",
        "Center data, form the covariance matrix, take its eigenvectors as principal components, and project to fewer dimensions.",
        ["ml.la.eigen", "ml.la.least-squares", "ml.math.probability-and-statistics"], 60,
        ["Center a dataset and compute its covariance matrix.",
         "Find the principal components as the covariance matrix's eigenvectors.",
         "Project data onto the top components and read the variance explained.",
         "Say when PCA helps and what it throws away."]),
    "ml.m3.checkpoint": (
        "checkpoint", "Checkpoint 3: fit and compress",
        "Fit a plane to points with least squares, then find the directions the same points vary most along with PCA.",
        ["ml.la.least-squares", "ml.la.eigen", "ml.la.pca"], 120,
        ["Fit a plane to points with the normal equations, and check it against np.linalg.lstsq.",
         "Reduce the same points to their top principal components and report the variance kept.",
         "Find and fix three bugs in a matrix program: a shape mismatch, a transposed multiply and an uncentered covariance.",
         "Explain why the normal equations give the least-squares fit, and what the top eigenvector of a covariance matrix means."]),
    "ml.calc.derivatives": (
        "topic", "Derivatives of the functions ML uses",
        "The derivatives of powers, exp, log, the sigmoid and ReLU, each checked numerically, and what each one's shape means for learning.",
        ["ml.math.calculus", "ml.math.exponents-and-logs", "ml.la.numpy-arrays"], 50,
        ["Differentiate powers, exp, log, the sigmoid and ReLU by rule, and check each numerically.",
         "Say why the sigmoid's derivative is small far from zero and what that does to learning.",
         "Apply a derivative to a whole array of inputs at once.",
         "Read a derivative's sign and size as the direction and speed to move."]),
    "ml.calc.partials-and-gradient": (
        "topic", "Partial derivatives and the gradient",
        "Functions of several variables, partial derivatives by holding the rest fixed, and the gradient as the vector that points uphill fastest.",
        ["ml.calc.derivatives", "ml.la.vectors"], 50,
        ["Take a partial derivative by holding the other variables fixed.",
         "Assemble the gradient as a vector, and check it against finite differences.",
         "Say why the gradient points in the direction of steepest ascent, and what its length means.",
         "Read a contour picture: the gradient is perpendicular to the contours."]),
    "ml.calc.descent-in-many-dimensions": (
        "topic", "Gradient descent in many dimensions",
        "Stepping against the gradient with a learning rate, watching the loss, and fitting a plane by descent to compare with least squares.",
        ["ml.calc.partials-and-gradient", "ml.la.least-squares"], 55,
        ["Write gradient descent for a function of several variables, with a learning rate and a stopping rule.",
         "Fit a plane by descent and compare the answer with the normal equations.",
         "Say what a learning rate too large and too small each do, and recognise each from the loss curve.",
         "Explain why descent slows near the bottom without being told to."]),
    "ml.calc.chain-rule": (
        "topic", "The chain rule",
        "Derivatives of composed functions, computed one layer at a time, which is the whole of backpropagation.",
        ["ml.calc.derivatives"], 50,
        ["Differentiate a composition of two functions by the chain rule, by hand and in code.",
         "Chain three or more functions, keeping the intermediate values.",
         "Check a chained derivative numerically.",
         "Say why the chain rule is what makes training a layered model possible."]),
    "ml.calc.loss-functions": (
        "topic", "Loss functions and their gradients",
        "Squared error, cross-entropy with the sigmoid and the softmax, why logs appear, and the gradient of each loss.",
        ["ml.calc.derivatives", "ml.math.probability-and-statistics"], 55,
        ["Compute mean squared error and cross-entropy for predictions and targets.",
         "Say why a probability model uses log loss rather than squared error.",
         "Differentiate each loss with respect to the prediction.",
         "Read a loss curve and say whether training is working."]),
    "ml.calc.backpropagation": (
        "topic", "Backpropagation",
        "A tiny network as composed functions: the forward pass, the backward pass by the chain rule, a gradient check, and the first training loop.",
        ["ml.calc.chain-rule", "ml.calc.descent-in-many-dimensions", "ml.calc.loss-functions", "ml.la.matrices-as-maps"], 60,
        ["Write a one-hidden-layer network as a forward pass of matrix products and a bend.",
         "Compute every gradient with the chain rule, layer by layer, from the loss backwards.",
         "Check the gradients against finite differences before trusting them.",
         "Train the network with gradient descent and watch the loss fall."]),
    "ml.calc.optimizers": (
        "topic", "Optimizers beyond plain gradient descent",
        "Momentum, learning-rate schedules and Adam, each in a few lines, compared on the same problem.",
        ["ml.calc.descent-in-many-dimensions", "ml.calc.backpropagation"], 50,
        ["Add momentum to gradient descent and say what it does on a long narrow valley.",
         "Decay the learning rate on a schedule, and say when that helps.",
         "Write Adam in a few lines and compare it with plain descent on the same function.",
         "Choose an optimizer and learning rate from a loss curve, and say why."]),
    "ml.m4.checkpoint": (
        "checkpoint", "Checkpoint 4: train a tiny network",
        "A two-layer network built from scratch and trained with backpropagation and an optimizer, on a small dataset.",
        ["ml.calc.backpropagation", "ml.calc.loss-functions", "ml.calc.optimizers"], 120,
        ["Build a two-layer network from scratch, train it with backpropagation and an optimizer, and report its loss and accuracy.",
         "Find and fix three bugs in a training loop: a chain-rule step out of order, an update with the wrong sign, and a shape mistake.",
         "Explain the chain rule as backpropagation, and what the learning rate trades off."]),
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


track_path = ROOT / "content" / "tracks" / "ml-foundations.yaml"
track_path.write_bytes(dump(TRACK).encode("utf-8"))
print("wrote", track_path)

for topic_id, (kind, title, summary, prereqs, minutes, objectives) in OUTLINES.items():
    folder = TOPICS / topic_id
    path = folder / "topic.yaml"
    if path.exists():
        existing = path.read_bytes().decode("utf-8")
        if "status: planned" not in existing:
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
