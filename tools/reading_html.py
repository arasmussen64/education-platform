"""What a reading shown inside the app may contain (ADR-0031).

A reading's text is a copy of part of somebody else's page, kept as a small,
plain subset of HTML: paragraphs, headings, lists, code, tables, pictures,
links and formulas (MathML). Nothing that runs, nothing that styles.

Two things use this file: `import_reading.py` cleans a downloaded page down
to the subset, and `validate_content.py` refuses a committed file that holds
anything outside it. The app's reader (`web/src/components/ReadingText.tsx`)
keeps the same list and skips anything else, so there are three guards.
"""

from __future__ import annotations

from html.parser import HTMLParser

# Tags kept as they are, each with the attributes it may carry.
ALLOWED: dict[str, frozenset[str]] = {
    tag: frozenset(attrs)
    for tag, attrs in {
        # Blocks.
        "p": (),
        "h2": (),
        "h3": (),
        "h4": (),
        "h5": (),
        "ul": (),
        "ol": ("start",),
        "li": (),
        "dl": (),
        "dt": (),
        "dd": (),
        "pre": (),
        "blockquote": (),
        "hr": (),
        "figure": (),
        "figcaption": (),
        "table": (),
        "caption": (),
        "thead": (),
        "tbody": (),
        "tr": (),
        "th": ("colspan", "rowspan"),
        "td": ("colspan", "rowspan"),
        # Inline.
        "a": ("href",),
        "img": ("src", "alt"),
        "em": (),
        "strong": (),
        "i": (),
        "b": (),
        "code": (),
        "kbd": (),
        "samp": (),
        "var": (),
        "sub": (),
        "sup": (),
        "br": (),
        # Formulas: MathML, which browsers draw themselves.
        "math": ("display",),
        "mrow": (),
        "mi": ("mathvariant",),
        "mn": (),
        "mo": ("stretchy", "fence", "separator", "lspace", "rspace"),
        "mtext": (),
        "mspace": ("width",),
        "mfrac": ("linethickness",),
        "msup": (),
        "msub": (),
        "msubsup": (),
        "msqrt": (),
        "mroot": (),
        "munder": (),
        "mover": ("accent",),
        "munderover": (),
        "mtable": ("columnalign",),
        "mtr": (),
        "mtd": ("columnalign",),
        "mstyle": ("displaystyle", "scriptlevel"),
        "mpadded": (),
        "menclose": ("notation",),
    }.items()
}

# Tags with no closing tag.
VOID = frozenset({"br", "hr", "img", "mspace"})

# Attributes that hold an address: it must be a full https one.
ADDRESSES = {("a", "href"), ("img", "src")}


class _Checker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []
        self.words = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ALLOWED:
            self.problems.append(f"<{tag}> isn't allowed in a reading")
            return
        for name, value in attrs:
            if name not in ALLOWED[tag]:
                self.problems.append(
                    f'<{tag} {name}="..."> isn\'t allowed in a reading'
                )
            elif (tag, name) in ADDRESSES and not (value or "").startswith("https://"):
                self.problems.append(
                    f"<{tag} {name}> must be a full https:// address: {value!r}"
                )

    def handle_data(self, data: str) -> None:
        self.words += len(data.split())

    def handle_comment(self, data: str) -> None:
        self.problems.append("comments aren't allowed in a reading")

    def handle_decl(self, decl: str) -> None:
        self.problems.append("a reading is a fragment: no <!doctype>")


def check(html: str) -> tuple[list[str], int]:
    """The problems with a reading's HTML (none is good), and its word count."""
    checker = _Checker()
    checker.feed(html)
    checker.close()
    # Say each problem once, however often it occurs.
    return list(dict.fromkeys(checker.problems)), checker.words


# Licences that let a text be copied and shown, with what each asks for. A
# resource's `license` must start with one of these to carry a copy. "ND"
# licences (no derivatives) are left out on purpose: we show parts of pages,
# and a part may count as a changed version. So is anything "all rights
# reserved" or with no licence stated.
COPYABLE = (
    "CC BY-NC-SA",
    "CC BY-NC ",
    "CC BY-SA",
    "CC BY ",
    "CC0",
    "PSF",
    "BSD",
    "MIT",
    "Apache",
    "GPL",
    "LGPL",
    "GNU FDL",
    "Public domain",
    "US government work",
)


def copyable(license_text: str) -> bool:
    """Whether a resource's recorded licence lets its text be copied."""
    padded = license_text + " "
    return "-ND" not in license_text and any(
        padded.startswith(start) for start in COPYABLE
    )
