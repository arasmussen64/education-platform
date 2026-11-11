"""Writes the topic ml.hw.bits-and-integers (Module 7's first topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Nothing here prints a platform-dependent size: dtypes are always named, and
sys.getsizeof is never used, because Pyodide is 32-bit. Files are written as
bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.bits-and-integers")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


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


# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''import numpy as np

print(bin(37), hex(255), int("100101", 2), int("ff", 16))
places = " + ".join(str(2 ** (7 - i)) for i, bit in enumerate(f"{37:08b}") if bit == "1")
print(f"{37:08b}", "=", places, "=", 37)

small = np.array([120, 125, 127], dtype=np.int8)
print("int8 + 5:", small + 5)
counts = np.array([250, 255], dtype=np.uint8)
print("uint8 + 1:", counts + 1)
print("Python int:", 2 ** 100)

print("the bits of -1 and -128 in int8:", f"{(-1) & 0xFF:08b}", f"{(-128) & 0xFF:08b}")
print("the same bytes read as unsigned:", np.array([-1, -128, 127], dtype=np.int8).view(np.uint8))

for dtype in ("uint8", "float32", "float64"):
    batch = np.zeros((1000, 784), dtype=dtype)
    print(f"{dtype:>7}: {batch.nbytes:,} bytes for 1,000 images of 784 pixels")

READ, WRITE, EXEC = 1, 2, 4
perms = READ | EXEC
print("perms:", perms, f"{perms:03b}", "can write:", bool(perms & WRITE), "can run:", bool(perms & EXEC))
perms |= WRITE
perms &= ~EXEC
print("after granting write and revoking run:", f"{perms:03b}")
packed = (255 << 16) | (128 << 8) | 7
print("rgb packed:", hex(packed), "green:", (packed >> 8) & 0xFF, "| 1 << 10 =", 1 << 10, "| 1024 >> 3 =", 1024 >> 3)
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0] == "0b100101 0xff 37 255" and EX[1] == "00100101 = 32 + 4 + 1 = 37", EX[:2]
assert EX[2] == "int8 + 5: [ 125 -126 -124]" and EX[3] == "uint8 + 1: [251   0]", EX[2:4]
assert EX[4] == "Python int: 1267650600228229401496703205376", EX[4]
assert EX[5] == "the bits of -1 and -128 in int8: 11111111 10000000", EX[5]
assert EX[6] == "the same bytes read as unsigned: [255 128 127]", EX[6]
assert EX[7] == "  uint8: 784,000 bytes for 1,000 images of 784 pixels", EX[7]
assert EX[8] == "float32: 3,136,000 bytes for 1,000 images of 784 pixels" and EX[9] == "float64: 6,272,000 bytes for 1,000 images of 784 pixels", EX[8:10]
assert EX[10] == "perms: 5 101 can write: False can run: True" and EX[11] == "after granting write and revoking run: 011", EX[10:12]
assert EX[12] == "rgb packed: 0xff8007 green: 128 | 1 << 10 = 1024 | 1024 >> 3 = 128", EX[12]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_BASES = '''print(bin(10), hex(10), hex(255))
print(int("1010", 2), int("ff", 16), 0b1111, 0x10)
print(f"{5:04b}", f"{255:08b}")
'''
PREDICT_BASES_OUT = out(PREDICT_BASES)
assert PREDICT_BASES_OUT == "0b1010 0xa 0xff\n10 255 15 16\n0101 11111111\n", PREDICT_BASES_OUT

PREDICT_WRAP = '''import numpy as np

a = np.array([100, 126, 127], dtype=np.int8)
print(a + 2)
b = np.array([0, 255], dtype=np.uint8)
print(b - 1)
print(100 + 27 + 1)
'''
PREDICT_WRAP_OUT = out(PREDICT_WRAP)
assert PREDICT_WRAP_OUT == "[ 102 -128 -127]\n[255 254]\n128\n", PREDICT_WRAP_OUT

REVIEW_SHIFTS = '''print(1 << 10, 1024 >> 3, 0b1010 ^ 0b0110, 0b1010 & 0b0110, 0b1010 | 0b0110)
print(37 & 1, 38 & 1, 37 >> 1)
'''
REVIEW_SHIFTS_OUT = out(REVIEW_SHIFTS)
assert REVIEW_SHIFTS_OUT == "1024 128 12 2 14\n1 0 18\n", REVIEW_SHIFTS_OUT

PARSONS_LINES = [
    "r, g, b = 255, 128, 7",
    "packed = (r << 16) | (g << 8) | b",
    "green = (packed >> 8) & 0xFF",
    "print(hex(packed), green)",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "0xff8007 128\n"
assert out("\n".join(PARSONS_LINES).replace("green = (packed >> 8) & 0xFF", "green = packed & 0xFF") + "\n") == "0xff8007 7\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def from_bits(bits):
    """The value of a string of bits, most significant first: each step doubles what came before and adds the next bit."""
    value = 0
    for bit in bits:
        value = value * 2 + int(bit)
    return value


print(from_bits("00100101"), from_bits("11111111"), from_bits("1"), from_bits("10000000"))
'''
FILL_STARTER = FILL_SOLUTION.replace("value = value * 2 + int(bit)", "value = value * ... + int(...)")
FILL_WRONG = FILL_SOLUTION.replace("value = value * 2 + int(bit)", "value = value * 10 + int(bit)")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "37 255 1 128\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def pack(r, g, b):
    """Three bytes (0 to 255) packed into one integer: red in the top byte, green in the middle, blue at the bottom."""
    return (r << 16) | (g << 8) | b


def unpack(packed):
    """The three bytes back out, as a tuple (r, g, b)."""
    return ((packed >> 16) & 0xFF, (packed >> 8) & 0xFF, packed & 0xFF)


print(hex(pack(255, 128, 7)), unpack(0xFF8007))
print(unpack(pack(0, 0, 255)), unpack(pack(16, 32, 48)))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "0xff8007 (255, 128, 7)\n(0, 0, 255) (16, 32, 48)\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("return ((packed >> 16) & 0xFF, (packed >> 8) & 0xFF, packed & 0xFF)", "return (packed >> 16, packed >> 8, packed & 0xFF)")
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''import numpy as np

DIGITS = "0123456789abcdef"


def to_base(n, base):
    """A non-negative integer as a string of digits in a base from 2 to 16."""
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(DIGITS[n % base])
        n //= base
    return "".join(reversed(digits))


def wraps_to(value, bits, signed):
    """The value a fixed-width integer of that many bits holds after storing value: it wraps around."""
    wrapped = value % (2 ** bits)
    if signed and wrapped >= 2 ** (bits - 1):
        wrapped -= 2 ** bits
    return wrapped


def array_bytes(shape, dtype):
    """How many bytes an array of that shape and dtype takes."""
    count = 1
    for size in shape:
        count *= size
    return count * np.dtype(dtype).itemsize


def smallest_uint(max_value):
    """The smallest unsigned dtype name that holds counts from 0 to max_value."""
    for name in ("uint8", "uint16", "uint32", "uint64"):
        if max_value <= np.iinfo(name).max:
            return name
    raise ValueError("too large for 64 bits")


print(to_base(37, 2), to_base(255, 16), to_base(255, 2), to_base(0, 2))
print(wraps_to(128, 8, True), wraps_to(256, 8, False), wraps_to(-1, 8, False), wraps_to(127, 8, True))
print(array_bytes((1000, 784), "float32"), array_bytes((1000, 784), "uint8"), array_bytes((60000, 28, 28), "float64"))
print(smallest_uint(200), smallest_uint(60000), smallest_uint(3_000_000_000))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "100101 ff 11111111 0\n-128 0 255 127\n3136000 784000 376320000\nuint8 uint16 uint32\n", BUILD_OUT
BUILD_CLAMPS = BUILD_SOLUTION.replace(
    "    wrapped = value % (2 ** bits)\n    if signed and wrapped >= 2 ** (bits - 1):\n        wrapped -= 2 ** bits\n    return wrapped",
    "    low, high = (-(2 ** (bits - 1)), 2 ** (bits - 1) - 1) if signed else (0, 2 ** bits - 1)\n    return max(low, min(high, value))",
)
BUILD_NOT_REVERSED = BUILD_SOLUTION.replace('    return "".join(reversed(digits))', '    return "".join(digits)')
BUILD_COUNTS_ELEMENTS = BUILD_SOLUTION.replace("    return count * np.dtype(dtype).itemsize", "    return count")
for wrong in (BUILD_CLAMPS, BUILD_NOT_REVERSED, BUILD_COUNTS_ELEMENTS):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np

pixels = np.array([3, 200, 200, 3, 3, 255, 200, 3] * 40, dtype=np.uint8)
histogram = np.zeros(256, dtype=np.int64)
np.add.at(histogram, pixels, 1)
print("counts of 3 and 200:", int(histogram[3]), int(histogram[200]))

FLAG_VALID, FLAG_EDGE, FLAG_DARK = 1, 2, 4
flags = np.where(pixels < 10, FLAG_VALID | FLAG_DARK, FLAG_VALID)
dark = sum(1 for f in flags if (f & FLAG_DARK) != 0)
print("dark pixels:", dark)
'''
BUG_INT8 = ("histogram = np.zeros(256, dtype=np.int64)", "histogram = np.zeros(256, dtype=np.int8)")
BUG_PRECEDENCE = ("if (f & FLAG_DARK) != 0)", "if (f & FLAG_DARK) == 1)")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_INT8).replace(*BUG_PRECEDENCE)
DEBUG_STILL_INT8 = DEBUG_SOLUTION.replace(*BUG_INT8)
DEBUG_STILL_PRECEDENCE = DEBUG_SOLUTION.replace(*BUG_PRECEDENCE)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT == "counts of 3 and 200: 160 120\ndark pixels: 160\n", DEBUG_OUT
assert STARTER_OUT == "counts of 3 and 200: -96 120\ndark pixels: 0\n", STARTER_OUT
assert out(DEBUG_STILL_INT8) != DEBUG_OUT and out(DEBUG_STILL_PRECEDENCE) != DEBUG_OUT

REVIEW_CODE_SOLUTION = '''def to_binary(n, width):
    """A non-negative integer as exactly width bits, most significant first, without bin() or format()."""
    bits = []
    for position in range(width - 1, -1, -1):
        bits.append("1" if (n >> position) & 1 else "0")
    return "".join(bits)


print(to_binary(37, 8), to_binary(5, 4), to_binary(0, 3), to_binary(255, 8))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "00100101 0101 000 11111111\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.bits-and-integers
kind: topic
status: ready
title: "Bits, bytes and integers"
summary: "How a computer stores a whole number: binary and hexadecimal, bytes, fixed-width integers that wrap around, Python's integers that don't, and the bit operations that masks and flags are made of."
prerequisites: [ml.m6.checkpoint]
packages: [numpy]
estimated_minutes: 45
rev: 1
objectives:
  - "Convert between binary, decimal and hexadecimal, and read a byte."
  - "Explain what a fixed-width integer is, why an int8 wraps from 127 to -128, and why a Python int doesn't."
  - "Say how many bytes a NumPy array of a given dtype and shape takes, and choose a dtype for a column of counts."
  - "Use and, or, shift and masks to pack and read flags."
# Linked, never copied or embedded: NumPy's documentation is under the NumPy
# licence (BSD-3-Clause); the Python documentation is under the PSF licence;
# Wikipedia is CC BY-SA 4.0.
resources:
  - title: "NumPy user guide: Data types (the table of integer and float types, and the section on overflow errors)"
    url: https://numpy.org/doc/stable/user/basics.types.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
  - title: "The Python documentation: Bitwise Operations on Integer Types (and, or, xor, shifts and inversion)"
    url: https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "Wikipedia: Two's complement (the introduction and the Theory section)"
    url: https://en.wikipedia.org/wiki/Two%27s_complement
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-what-a-byte-holds
  - predict-three-bases
  - mcq-why-127
  - predict-a-wrap
  - mcq-python-int-against-numpy-int
  - mcq-which-dtype-for-counts
  - parsons-pack-a-colour
  - mcq-testing-a-flag
  - fill-place-values
  - write-pack-and-unpack
prove:
  build: build-a-bit-toolkit
  debug: debug-a-counter-that-went-negative
  explain:
    prompt: |
      A teammate's pipeline counts events per user in an int8 column and reports negative counts for the busiest users; another asks why a dataset of 60,000 grey images of 28 by 28 pixels is 47 megabytes on disk and 376 megabytes once loaded; a third wrote `if (flags & 4) == 1:` and can't see why the branch never runs, even for dark pixels. In your own words: how a byte stores a number and how binary and hexadecimal relate to it; what a fixed-width integer is, why int8 wraps from 127 to -128 (what the top bit means), and why a Python int never does; how to size an array from its dtype and shape and choose a dtype for a column; and what the bit operations do, including why that `if` is wrong.
    rubric:
      - id: bases
        required: true
        description: "A byte is eight bits with place values 128 down to 1, 256 patterns; binary writes the bits, hexadecimal writes one digit per four bits so two digits per byte (0xFF is 255); int(s, 2), bin, hex and format convert."
      - id: fixed-width
        required: true
        description: "A fixed-width integer has a set number of bits: int8 has 256 patterns, interpreted as -128 to 127 in two's complement, where the top bit counts as -128; 127 + 1 produces the pattern 10000000, which is -128, so the count wraps. Python's int grows as needed and never wraps; NumPy arrays wrap silently, so counts need a wider dtype such as int64."
      - id: sizing
        required: true
        description: "Bytes are itemsize times elements: 60,000 by 28 by 28 is 47,040,000 elements, 47 MB as uint8 and 376 MB as float64 (8 bytes each); choose the smallest dtype whose range holds the column (counts to 60,000 fit uint16) and compute sums in a wider one."
      - id: bits
        required: true
        description: "& keeps bits set in both, | sets, ^ flips, ~ inverts, << and >> move bits (multiply or divide by two per step); a mask like 4 picks bit 2 and keeps it in its place, so `flags & 4` is 4 when the flag is set and never 1: test it against 0 or use its truthiness (Python, unlike C, binds & tighter than ==)."
    model_answer: |
      A byte is eight bits, each a 0 or a 1, and reading them as place values 128, 64, 32, 16, 8, 4, 2 and 1 gives a number from 0 to 255, two hundred and fifty-six patterns in all. Binary just writes the bits out; hexadecimal writes one digit for every four bits, so a byte is exactly two hex digits and 0xFF is 11111111, which is 255. Python converts with int(s, 2), bin, hex and format. A fixed-width integer is a number stored in a set number of bits, so it has a set number of patterns: an int8 has 256. Signed types read them in two's complement, where the top bit counts as minus 128 instead of plus 128, so 01111111 is 127 and 10000000 is minus 128. Adding 1 to 127 produces the pattern 10000000, and that is minus 128: the count didn't go wrong gradually, it wrapped round, which is exactly what the busy users' negative counts are. Python's own int has no fixed width; it grows to hold whatever you compute, so 2 to the 100 is fine, and it never wraps. NumPy arrays do wrap, silently, so a column of counts needs a dtype with room, int64 or an unsigned type if counts can't be negative. Sizing an array is multiplication: the number of elements times the bytes per element, which the dtype fixes. Sixty thousand images of 28 by 28 pixels is 47,040,000 elements; as uint8, one byte each, that is 47 megabytes, which is the file; loaded as float64, eight bytes each, it is 376 megabytes. Choosing a dtype means choosing the smallest whose range holds the column, uint16 for counts up to 65,535, say, and doing sums in a wider type so they don't wrap. The bit operations work on the patterns directly: and keeps the bits set in both operands, or sets a bit, xor flips one, not inverts all of them, and the shifts move the whole pattern left or right, which multiplies or divides by two per position. A mask such as 4 is the pattern with only bit 2 set, so flags & 4 is nonzero exactly when that flag is on. The teammate's if is wrong because the mask keeps the bit where it was: flags & 4 is 4 when the flag is set and 0 when it isn't, never 1, so comparing with 1 is always false. Compare with 0, or just write if flags & 4, since any nonzero value counts as true. Python, unlike C, binds & tighter than ==, so the parentheses are for the reader, not the parser.
review_pool:
  - review-predict-shifts
  - review-mcq-a-byte-in-hex
  - review-mcq-eight-megabytes
  - review-to-binary
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: bases
    description: "Convert between binary, decimal and hexadecimal, and read a byte"
  - id: fixed-width
    description: "Say what a fixed-width integer is, why it wraps, and why a Python int doesn't"
  - id: sizing
    description: "Size an array from its dtype and shape, and choose a dtype for a column"
  - id: bits
    description: "Use and, or, xor, shifts and masks to pack and read flags"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Every number a model touches is stored in a fixed handful of **bits**, and the handful decides what can go wrong: a counter that turns negative, a dataset that is eight times bigger in memory than on disk, a flag test that never fires. This topic is the whole number's half of that story: how a **byte** holds a value, why a **fixed-width integer** wraps around, why Python's own `int` doesn't, how to size an array before you load it, and the bit operations that masks and flags are made of. The next topic does the same for fractions.

The main resource is **NumPy's user guide page on data types**: the table of integer and float types with their ranges, and the short section on overflow; about 15 minutes. The Python documentation's section on bitwise operations is the reference for `&`, `|`, `^`, `~` and the shifts, and Wikipedia's _Two's complement_ explains the top bit. Watch for:

- **The ranges**: int8 is -128 to 127, uint8 is 0 to 255, and so on up to 64 bits.
- **Overflow**: what NumPy does when a result doesn't fit.
- **The top bit** counts as negative in a signed type.

</Intro>

<Resource index={0} />

<Recap>

- **Bits and bytes.** A **bit** is a 0 or a 1; a **byte** is eight of them, with place values 128, 64, 32, 16, 8, 4, 2, 1, so it holds 0 to 255, 256 patterns. **Binary** writes the bits (`0b100101` is 37: 32 + 4 + 1); **hexadecimal** writes one digit per four bits, so a byte is two hex digits and `0xFF` is 255. `bin`, `hex`, `int(text, 2)` and `f"{n:08b}"` convert.
- **Fixed-width integers.** A NumPy `int8` has 8 bits, so 256 patterns, read in **two's complement**: the top bit counts as -128, so `01111111` is 127, `10000000` is -128 and `11111111` is -1. Arithmetic that leaves the range **wraps**: on int8, 127 + 1 is -128, and on uint8 (0 to 255), 255 + 1 is 0. The worked example's `[120, 125, 127] + 5` comes out `[125, -126, -124]`. NumPy arrays wrap **silently**; NumPy scalars warn; storing an out-of-range number into an array raises. Python's own `int` has no fixed width and grows as needed (`2 ** 100` is fine), at the cost of speed. The default integer dtype of a NumPy array depends on the platform (64-bit CPython uses int64; the browser's Python is 32-bit), so name a dtype whenever it matters.
- **Sizing an array** is multiplication: elements times bytes per element (`np.dtype(name).itemsize`; `array.nbytes` for a real array). A thousand images of 784 pixels is 784,000 bytes as uint8, 3,136,000 as float32 and 6,272,000 as float64. Choose the smallest dtype whose **range** holds the column (counts to 65,535 fit uint16; a byte holds a pixel), and do sums in a wider type (`dtype=np.int64`) so they don't wrap.
- **Bit operations** work on the patterns: `&` keeps the bits set in both (`0b1010 & 0b0110` is `0b0010`), `|` sets (`0b1110`), `^` flips where they differ (`0b1100`), `~` inverts every bit, `<<` and `>>` move the pattern left or right, which multiplies or divides by two per step (`1 << 10` is 1024, `1024 >> 3` is 128). `n & 1` tests the lowest bit (odd or even). A **mask** is a pattern with the bits you care about set: with `READ, WRITE, EXEC = 1, 2, 4`, `perms & WRITE` is nonzero when writing is allowed, `perms |= WRITE` grants it, `perms &= ~EXEC` revokes running. Packing three bytes into one int is shifts and ors, unpacking is shifts and masks: `(packed >> 8) & 0xFF` is the middle byte.
- **A mask keeps the bit in place:** `flags & 4` is 4 when the flag is set and 0 when it isn't, never 1, so test it against 0 (`(flags & 4) != 0`) or use its truthiness (`if flags & 4:`), never `== 1` or `== True`. Python, unlike C, binds `&` tighter than `==`, so `flags & 4 == 0` means `(flags & 4) == 0`; the parentheses are for the reader.
- **In machine learning** (names you'll meet later): an image dataset is uint8 on disk and becomes float64, NumPy's default float, the moment you divide by 255: eight times the memory (converting to float32 first makes it four); a token counter in int32 wraps at about 2.1 billion; **quantization** stores weights as int8 to cut memory and bandwidth, which is this topic applied to a model; and attention masks are arrays of 0s and 1s doing the job of a bitmask.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-three-bases.yaml",
    f'''id: predict-three-bases
type: predict_output
rev: 1
prompt: |
  The same numbers in binary, decimal and hexadecimal. What does the program print?
code: |
{block(PREDICT_BASES)}expected_output: |
{block(PREDICT_BASES_OUT)}explanation: |
  `bin` and `hex` return strings with `0b` and `0x` prefixes; ten is `1010` in binary and `a` in hex, 255 is `ff`. `int(text, base)` reads them back, and literals written with `0b` and `0x` are just numbers (`0b1111` is 15, `0x10` is 16). The format `04b` pads to four bits, `08b` to a byte.
skills: [bases]
''',
)

mcq(
    "mcq-why-127",
    "An `int8` holds -128 to 127 and a `uint8` holds 0 to 255. Why those numbers?",
    [
        "Because the hardware adds in groups of seven bits and keeps the eighth as a carry, so seven bits is all a byte can count with",
        "Because the sign takes one bit and the remaining seven count to 127; the negatives go one further because zero is counted twice",
        "Because 8 bits make 256 patterns: unsigned reads them as 0 to 255; signed gives half to negatives, the top bit counting -128",
        "Because NumPy reserves the pattern 10000000 as a missing-value marker, which costs one positive number",
    ],
    2,
    "Eight bits give 2 to the 8, 256, patterns, and both types use all of them. Unsigned reads the pattern as a plain place-value number, 0 to 255. Two's complement reads the top bit as -128 instead of +128, so the patterns run from -128 (10000000) through -1 (11111111) and 0 to 127: one more negative than positive because zero takes one of the non-negative patterns. Nothing is reserved and primes have nothing to do with it.",
    ["fixed-width"],
)

write(
    "recall/predict-a-wrap.yaml",
    f'''id: predict-a-wrap
type: predict_output
rev: 1
prompt: |
  An int8 array plus 2, a uint8 array minus 1, and the same sum in plain Python. What does the program print?
code: |
{block(PREDICT_WRAP)}expected_output: |
{block(PREDICT_WRAP_OUT)}explanation: |
  Arrays keep their dtype: 126 + 2 is 128, which an int8 can't hold, so the pattern wraps to -128, and 127 + 2 to -127; 0 - 1 on a uint8 wraps to 255. NumPy does this silently for arrays. Python's own integers have no width, so 100 + 27 + 1 is simply 128.
skills: [fixed-width]
''',
)

mcq(
    "mcq-python-int-against-numpy-int",
    "`2 ** 64` works in plain Python but a NumPy `int64` array can't hold it. What is the difference between the two kinds of integer?",
    [
        "Python's int is stored as a float behind the scenes, so it can hold anything up to about 10 to the 308 before it overflows to infinity",
        "There is no difference; NumPy raises only because it checks for overflow and Python doesn't",
        "NumPy integers are 32-bit on every platform, and Python integers are 64-bit",
        "A Python int grows to the bits the value needs; a NumPy integer has a fixed width set by its dtype, which keeps arrays compact",
    ],
    3,
    "A Python int is an object that allocates more digits as the number grows, so it never wraps and 2 to the 64, or to the 1000, is fine; each operation pays for that flexibility. A NumPy array stores every element in the same fixed number of bytes, which is why a million of them take a predictable amount of memory and can be processed in compiled loops, and why a result that doesn't fit wraps or raises. Widths follow the dtype; the default integer dtype depends on the platform.",
    ["fixed-width"],
)

mcq(
    "mcq-which-dtype-for-counts",
    "A column holds the number of events per user, between 0 and about 50,000. Which dtype should it have, and why not the others?",
    [
        "`int8`, the smallest, so the column takes the least memory",
        "`float32`, because counts may need to be averaged later and a float column saves the conversion when the time comes to compute means",
        "`uint16`: 0 to 65,535 in two bytes; int8 wraps at 127, and float32 costs four bytes and can't hold every count past 16,777,216",
        "`int64`, always, since memory is cheap and nothing else is safe",
    ],
    2,
    "The right dtype is the smallest whose range holds the column: counts are non-negative and stay under 65,535, so uint16 fits in two bytes. int8 would wrap at 127, which is the negative-count bug. float32 would spend twice the memory and loses exactness above 16,777,216. int64 is safe but four times the size of uint16; it is the right choice for the sums, not the stored column.",
    ["sizing"],
)

write(
    "recall/parsons-pack-a-colour.yaml",
    "id: parsons-pack-a-colour\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to pack a red, green and blue byte into one integer, read the green byte back out, and print `0xff8007 128`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("green = packed & 0xFF")
    + "\nexplanation: |\n"
    + block("Red is shifted up 16 bits, green 8, blue none, and the three are combined with `|`: `0xff8007`. To read green back, shift the packed value down 8 bits so green sits in the bottom byte, then mask with `0xFF` to drop red above it. The decoy masks without shifting and gets blue, 7.")
    + "skills: [bits]\n",
)

mcq(
    "mcq-testing-a-flag",
    "`FLAG_DARK = 4`. A loop with `if (flags & FLAG_DARK) == 1:` never takes the branch, even for pixels where the flag is on. Why?",
    [
        "Because `==` binds tighter than `&` in Python, so the test is really `flags & (FLAG_DARK == 1)`, which is always 0",
        "Because the mask keeps the bit in place: `flags & 4` is 4 when set, never 1; test against 0 or use truthiness",
        "Because `&` on NumPy values returns an array rather than a plain number, and an array is never equal to 1",
        "Because `&` on a NumPy uint8 gives a Python bool, so the test should compare with `True` instead of 1",
    ],
    1,
    "`flags & 4` keeps only bit 2, in its own place, so the result is 4 when the flag is on and 0 when it is off; it is never 1, and the branch never runs. Compare with 0, or write `if flags & FLAG_DARK:`, since any nonzero value is true. The precedence story is C's, not Python's: Python binds `&` tighter than `==`, so even without parentheses the test would have been `(flags & 4) == 1`. `&` on NumPy integers gives an integer of the same dtype, not a bool, and a scalar for scalars; and 4 is a power of two, which is exactly what makes it usable as a flag.",
    ["bits"],
)

write(
    "recall/review-predict-shifts.yaml",
    f'''id: review-predict-shifts
type: predict_output
rev: 1
prompt: |
  Shifts and the three bitwise combinations on small numbers. What does the program print?
code: |
{block(REVIEW_SHIFTS)}expected_output: |
{block(REVIEW_SHIFTS_OUT)}explanation: |
  Shifting left by 10 multiplies by 2 to the 10, so 1 becomes 1024; shifting 1024 right by 3 divides by 8, 128. `1010 ^ 0110` keeps the bits that differ, `1100`, which is 12; `&` keeps the bits in both, `0010`, 2; `|` keeps the bits in either, `1110`, 14. `n & 1` is the lowest bit, 1 for odd 37 and 0 for even 38, and `37 >> 1` is 37 halved and rounded down, 18.
skills: [bits]
''',
)

mcq(
    "review-mcq-a-byte-in-hex",
    "Why are bytes so often written in hexadecimal, and what is `0x7F`?",
    [
        "Because one hex digit is exactly four bits, so a byte is two digits; `0x7F` is 0111 1111, 127",
        "Because hex is what the hardware uses; `0x7F` is 79",
        "Because hex numbers are smaller than decimal ones; `0x7F` is 7 times 16 minus 1, which is 111, the largest byte",
        "Because Python can only print bytes in hex; `0x7F` is 7 and 15, written together as 715",
    ],
    0,
    "Sixteen is 2 to the 4, so each hex digit stands for exactly four bits and the boundaries line up: a byte is two digits, a 32-bit word eight. `0x7F` is 7 sixteens plus 15, which is 127, the largest int8, and its bits are 0111 1111, the top bit clear. The hardware doesn't use hex; people do, because the binary is easier to see through it. Hex digits aren't smaller numbers, just a shorter spelling of the same ones; `0x7F` is one number, not 7 and 15 side by side; and Python prints bytes in hex by default but can print them in any base.",
    ["bases"],
)

mcq(
    "review-mcq-eight-megabytes",
    "A million measurements are loaded as a float64 array. Roughly how much memory, and what would halve it?",
    [
        "About 1 megabyte, since a million values is a million bytes; nothing halves it short of dropping values",
        "About 64 megabytes, 64 bytes each; float32 halves it",
        "About 8 megabytes, 8 bytes each; float32 halves it, keeping about 7 significant digits instead of 16",
        "It depends on the values; small numbers take fewer bytes",
    ],
    2,
    "Memory is elements times bytes per element, and float64 is eight bytes whatever the value: a million of them is 8,000,000 bytes. float32 is four bytes, so half, and keeps about seven significant digits where float64 keeps about sixteen, which the next topic, Floating point, measures. A fixed-width type takes the same room for every value; that is what fixed width means.",
    ["sizing"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-what-a-byte-holds/exercise.yaml",
    f'''id: example-what-a-byte-holds
stage: worked_example
rev: 1
title: "What a byte holds"
prompt: |
  Numbers in three bases, integers that wrap and one that doesn't, the bits of a negative number, the size of an image batch in three dtypes, and flags packed into an integer. Press **Run**, then read how each part works.
steps:
  - label: "Three ways to write 37 and 255"
    lines: "{ln('print(bin(37)')}-{ln('"=", places')}"
    note: "`bin` and `hex` turn a number into text with a `0b` or `0x` prefix, and `int(text, base)` reads it back. The second line shows what the bits mean: in `00100101` the 1s sit under the place values 32, 4 and 1."
  - label: "Fixed width wraps; Python's int doesn't"
    lines: "{ln('small = np.array')}-{ln('Python int:')}"
    note: "An int8 holds -128 to 127, so 125 + 5 and 127 + 5 don't fit: the patterns wrap round to -126 and -124, silently. A uint8 holds 0 to 255, so 255 + 1 is 0. Python's own `int` has no width: `2 ** 100` is a 31-digit number and nothing wraps."
  - label: "What the bits of a negative number look like"
    lines: "{ln('the bits of -1')}-{ln('read as unsigned')}"
    note: "In two's complement the top bit of an int8 counts as -128, so -1 is all eight bits set and -128 is the top bit alone. Reading the same bytes as unsigned (`view(np.uint8)`, which reinterprets without converting) gives 255, 128 and 127: the patterns didn't change, only the rule for reading them."
  - label: "Sizing a batch of images"
    lines: "{ln('for dtype in')}-{ln('bytes for 1,000 images')}"
    note: "A thousand images of 784 pixels is 784,000 elements; the dtype says how many bytes each one takes: one as uint8 (a pixel's 0 to 255), four as float32, eight as float64. `nbytes` is the array's own count. Dividing pixels by 255 gives float64, NumPy's default float, eight times the memory; converting to float32 first makes it four."
  - label: "Flags in an integer"
    lines: "{ln('READ, WRITE, EXEC')}-{ln('after granting write')}"
    note: "Three flags, one bit each. `|` combines them into `101`, 5; `& WRITE` tests the middle bit and finds it off; `|= WRITE` turns it on and `&= ~EXEC` turns the top bit off, leaving `011`. Permissions, options and feature switches are stored this way."
  - label: "Packing and unpacking bytes"
    lines: "{ln('packed = (255 << 16)')}-{ln('rgb packed:')}"
    note: "Three bytes shifted into place and combined make one integer, `0xff8007`; shifting it back down by 8 and masking with `0xFF` recovers the middle byte, 128. A left shift by 10 multiplies by 1024; a right shift by 3 divides by 8."
''',
)
write("exercises/example-what-a-byte-holds/solution.py", EXAMPLE)
write(
    "exercises/example-what-a-byte-holds/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the bases, the wraps, the negative bits, the three sizes and the flag arithmetic."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-place-values/exercise.yaml",
    f'''id: fill-place-values
stage: fill_in
rev: 1
title: "Place values"
prompt: |
  `from_bits(bits)` should turn a string of bits, most significant first, into its value by walking the string once: at each bit, double what came before and add the bit. Replace each `...` so the program prints the values of four bit strings:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Each place to the left is worth twice as much, so the running value doubles for every new bit."
  - "`int(bit)` turns the character `\\"1\\"` or `\\"0\\"` into 1 or 0."
skills: [bases]
''',
)
write("exercises/fill-place-values/starter.py", FILL_STARTER)
write("exercises/fill-place-values/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-place-values/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 37 255 1 128."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_against_int():
    """Agrees with int(bits, 2) for every value from 0 to 1023, written in 10 bits."""
    from_bits = function("from_bits")
    assert all(from_bits(format(n, "010b")) == n for n in range(1024))
''',
)
write("exercises/fill-place-values/wrong/decimal-places.py", FILL_WRONG)
write(
    "exercises/fill-place-values/wrong/typed-in.py",
    "def from_bits(bits):\n    return 37\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-pack-and-unpack/exercise.yaml",
    f'''id: write-pack-and-unpack
stage: write
rev: 1
title: "Pack and unpack a colour"
prompt: |
  Write `pack(r, g, b)`, which packs three bytes (each 0 to 255) into one integer with red in the top byte, green in the middle and blue at the bottom, and `unpack(packed)`, which returns the three bytes as a tuple `(r, g, b)`. Then print:

  ```python
  print(hex(pack(255, 128, 7)), unpack(0xFF8007))
  print(unpack(pack(0, 0, 255)), unpack(pack(16, 32, 48)))
  ```

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Shift red up by 16 bits and green by 8, then combine with `|`."
  - "To read a byte back, shift it down to the bottom and mask with `0xFF`; without the mask the bytes above it come along."
skills: [bits]
''',
)
write("exercises/write-pack-and-unpack/starter.py", "")
write("exercises/write-pack-and-unpack/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-pack-and-unpack/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the packed colour and the three unpacked tuples."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_round_trips():
    """Every byte survives a pack and unpack, including 255 in every position and 0 everywhere."""
    pack = function("pack")
    unpack = function("unpack")
    for r, g, b in ((0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (1, 2, 3), (200, 100, 50)):
        assert unpack(pack(r, g, b)) == (r, g, b)
    assert pack(255, 255, 255) == 0xFFFFFF
''',
)
write("exercises/write-pack-and-unpack/wrong/no-mask.py", WRITE_WRONG)
write(
    "exercises/write-pack-and-unpack/wrong/typed-in.py",
    "def pack(r, g, b):\n    return 0xFF8007\n\n\ndef unpack(packed):\n    return (255, 128, 7)\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-bit-toolkit/exercise.yaml",
    f'''id: build-a-bit-toolkit
stage: build
rev: 1
title: "A bit toolkit"
prompt: |
  Starting from a blank editor, write four functions:

  - `to_base(n, base)`: a non-negative integer as a string of digits in a base from 2 to 16, using the digits `0123456789abcdef`, with no leading zeros (`to_base(0, base)` is `"0"`); without `bin`, `hex` or `format`.
  - `wraps_to(value, bits, signed)`: the value a fixed-width integer of `bits` bits ends up holding after `value` is stored in it, by wrapping: for an unsigned type the remainder on division by `2 ** bits`, and for a signed type the same remainder shifted down by `2 ** bits` when it reaches the top half.
  - `array_bytes(shape, dtype)`: the bytes an array of that shape (a tuple) and dtype (a name such as `"float32"`) takes; `np.dtype(name).itemsize` is the bytes per element.
  - `smallest_uint(max_value)`: the name of the smallest of `uint8`, `uint16`, `uint32`, `uint64` that holds counts from 0 to `max_value` (`np.iinfo(name).max` is each one's largest value); raise `ValueError` beyond 64 bits.

  Then print:

  ```python
  print(to_base(37, 2), to_base(255, 16), to_base(255, 2), to_base(0, 2))
  print(wraps_to(128, 8, True), wraps_to(256, 8, False), wraps_to(-1, 8, False), wraps_to(127, 8, True))
  print(array_bytes((1000, 784), "float32"), array_bytes((1000, 784), "uint8"), array_bytes((60000, 28, 28), "float64"))
  print(smallest_uint(200), smallest_uint(60000), smallest_uint(3_000_000_000))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare `to_base` with Python's own conversions, `wraps_to` with what NumPy really stores, `array_bytes` with real arrays' `nbytes`, and `smallest_uint` at the boundaries.
skills: [bases, fixed-width, sizing]
''',
)
write("exercises/build-a-bit-toolkit/starter.py", "")
write("exercises/build-a-bit-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-bit-toolkit/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_to_base_against_python():
    """Agrees with bin, oct and hex for 0 to 999, and writes 0 as a single digit."""
    to_base = function("to_base")
    for n in range(1000):
        assert to_base(n, 2) == format(n, "b") and to_base(n, 8) == format(n, "o") and to_base(n, 16) == format(n, "x")
    assert to_base(0, 16) == "0"


def test_wraps_to_against_numpy():
    """Agrees with what NumPy stores for every value from -300 to 300 in int8, uint8 and int16."""
    wraps_to = function("wraps_to")
    for value in range(-300, 301):
        assert wraps_to(value, 8, True) == int(np.array([value]).astype(np.int8)[0])
        assert wraps_to(value, 8, False) == int(np.array([value]).astype(np.uint8)[0])
        assert wraps_to(value, 16, True) == int(np.array([value]).astype(np.int16)[0])
    assert wraps_to(70000, 16, False) == 4464


def test_array_bytes_against_nbytes():
    """Matches nbytes for small arrays of five dtypes, and an empty shape is one element."""
    array_bytes = function("array_bytes")
    for dtype in ("uint8", "int16", "int32", "float32", "float64"):
        for shape in ((7,), (3, 4), (2, 3, 4)):
            assert array_bytes(shape, dtype) == np.zeros(shape, dtype=dtype).nbytes
    assert array_bytes((), "float64") == 8


def test_smallest_uint_boundaries():
    """255 fits uint8 and 256 needs uint16; 65,535 fits uint16 and 65,536 needs uint32; beyond uint64 raises."""
    smallest_uint = function("smallest_uint")
    assert (smallest_uint(255), smallest_uint(256), smallest_uint(65535), smallest_uint(65536)) == ("uint8", "uint16", "uint16", "uint32")
    assert smallest_uint(2**64 - 1) == "uint64"
    try:
        smallest_uint(2**64)
    except ValueError:
        pass
    else:
        raise AssertionError("2**64 doesn't fit any unsigned dtype")
''',
)
write("exercises/build-a-bit-toolkit/wrong/clamps-instead-of-wrapping.py", BUILD_CLAMPS)
write("exercises/build-a-bit-toolkit/wrong/digits-not-reversed.py", BUILD_NOT_REVERSED)
write("exercises/build-a-bit-toolkit/wrong/counts-elements-not-bytes.py", BUILD_COUNTS_ELEMENTS)
write(
    "exercises/build-a-bit-toolkit/wrong/typed-in.py",
    "def to_base(n, base):\n    return '100101'\n\n\ndef wraps_to(value, bits, signed):\n    return -128\n\n\ndef array_bytes(shape, dtype):\n    return 3136000\n\n\ndef smallest_uint(max_value):\n    return 'uint8'\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-counter-that-went-negative/exercise.yaml",
    f'''id: debug-a-counter-that-went-negative
stage: debug
rev: 1
title: "A counter that went negative"
prompt: |
  The program counts how often each pixel value appears in 320 pixels, then counts the pixels whose `FLAG_DARK` bit is set. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the count for value 3 is -96, because the histogram is an **int8** array, which holds at most 127; the 160 increments wrapped round. Counts need room: `int64`. Fix that, and the dark-pixel count is 0, because the test compares the masked value with 1: `f & FLAG_DARK` keeps the bit in its own place, so it is 4 when the flag is set, never 1. Test it against 0, `(f & FLAG_DARK) != 0`, or just `if f & FLAG_DARK`.
skills: [fixed-width, bits]
''',
)
write("exercises/debug-a-counter-that-went-negative/starter.py", DEBUG_STARTER)
write("exercises/debug-a-counter-that-went-negative/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-counter-that-went-negative/test_exercise.py",
    f'''from checks import run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints 160 and 120 for the two counts, and 160 dark pixels."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"
''',
)
write("exercises/debug-a-counter-that-went-negative/wrong/still-int8.py", DEBUG_STILL_INT8)
write("exercises/debug-a-counter-that-went-negative/wrong/still-compares-with-one.py", DEBUG_STILL_PRECEDENCE)
write(
    "exercises/debug-a-counter-that-went-negative/wrong/typed-in.py",
    "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()).replace("print('counts of 3 and 200: 160 120')", "print('counts of 3 and 200: 160 121')"),
)

write(
    "exercises/review-to-binary/exercise.yaml",
    f'''id: review-to-binary
stage: review_code
rev: 1
title: "To binary, from memory"
prompt: |
  Write `to_binary(n, width)`, a non-negative integer as exactly `width` bits, most significant first, without `bin` or `format`: for each position from `width - 1` down to 0, shift `n` right by that many places and look at the lowest bit. Print it for 37 in 8 bits, 5 in 4, 0 in 3 and 255 in 8:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [bits, bases]
''',
)
write("exercises/review-to-binary/starter.py", "")
write("exercises/review-to-binary/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-to-binary/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the four bit strings."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_against_format():
    """Agrees with format(n, '010b') for 0 to 1023."""
    to_binary = function("to_binary")
    assert all(to_binary(n, 10) == format(n, "010b") for n in range(1024))
''',
)
write(
    "exercises/review-to-binary/wrong/least-significant-first.py",
    REVIEW_CODE_SOLUTION.replace("for position in range(width - 1, -1, -1):", "for position in range(width):"),
)
write(
    "exercises/review-to-binary/wrong/typed-in.py",
    "def to_binary(n, width):\n    return '00100101'\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.bits-and-integers written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
