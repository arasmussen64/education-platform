"""The reading importer (ADR-0031): what it keeps of a page, and what it
turns the rest into. No test here downloads anything."""

# The sample page has long lines, as real pages do.
# ruff: noqa: E501

import reading_html
from import_reading import extract

PAGE = "https://example.com/book/chapter.html"

HTML = """
<html><body>
<nav>Menu</nav>
<main>
  <h1>Chapter 1</h1>
  <section id="one">
    <h2>First<a class="headerlink" href="#one">¶</a></h2>
    <p class="lead" style="color:red">Kept <span class="x">words</span>,
       a <a href="other.html#part">link</a> and a <a href="mailto:a@b.c">mail</a>.</p>
    <div class="highlight"><pre><span class="kn">from</span><span class="w"> </span><span class="nn">fractions</span><span class="w"> </span><span class="kn">import</span><span class="w"> </span><span class="n">Fraction</span>
</pre></div>
    <script>steal()</script>
    <button type="button"><img src="/img/a.png" alt="A chart"></button>
    <!-- a note -->
  </section>
  <section id="two">
    <h2>Second</h2>
    <p>Value: <math><semantics><mrow><msup><mfenced><mrow><mn>1</mn><mo>+</mo><mi>r</mi></mrow></mfenced><mi>n</mi></msup></mrow><annotation encoding="x">(1+r)^n</annotation></semantics></math></p>
  </section>
  <section id="three"><h2>Third</h2><p>Left out.</p></section>
</main>
<footer>Footer</footer>
</body></html>
"""


def test_the_cleaned_page_is_a_valid_reading() -> None:
    html = extract(HTML, PAGE)
    assert reading_html.check(html)[0] == []
    assert "Menu" not in html and "Footer" not in html
    assert "steal" not in html and "a note" not in html and "¶" not in html


def test_code_keeps_the_spaces_between_its_words() -> None:
    # Each space of coloured code sits in a tag of its own: dropping "empty"
    # tags once turned this line into "fromfractionsimport Fraction".
    html = extract(HTML, PAGE)
    assert "<pre><code>from fractions import Fraction</code></pre>" in html


def test_addresses_become_full_ones_and_others_lose_their_link() -> None:
    html = extract(HTML, PAGE)
    assert '<a href="https://example.com/book/other.html#part">link</a>' in html
    assert "mailto" not in html and "a mail." in html
    assert '<img alt="A chart" src="https://example.com/img/a.png"/>' in html
    assert "<p>Kept words," in html


def test_brackets_in_a_formula_are_written_out() -> None:
    # Browsers no longer draw <mfenced>: (1 + r) would show as 1 + r.
    html = extract(HTML, PAGE)
    assert "mfenced" not in html and "annotation" not in html
    assert (
        "<msup><mrow><mo>(</mo><mrow><mn>1</mn><mo>+</mo><mi>r</mi></mrow>"
        "<mo>)</mo></mrow><mi>n</mi></msup>"
    ) in html


def test_only_the_part_asked_for_is_kept() -> None:
    html = extract(HTML, PAGE, start_at="#two", stop_at="Third")
    assert "<h2>Second</h2>" in html
    assert "First" not in html and "Left out" not in html and "Chapter" not in html
    by_heading = extract(HTML, PAGE, start_at="First", stop_at="#two")
    assert "Kept" in by_heading and "Second" not in by_heading
