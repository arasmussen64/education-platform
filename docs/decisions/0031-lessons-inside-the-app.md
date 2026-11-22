# ADR-0031: Lessons inside the app: play the video, show the reading, or write our own

- **Status:** Accepted (the owner set the order on 2026-11-21: "Embed videos when possible. Show the outside pages text in the app. And if we can't do either of those then" our own text). The details below were chosen while building; say the word to change any.
- **Date:** 2026-11-21

## Context

A lesson has our own introduction, one main resource from somebody else, and our recap ([ADR-0004](0004-content-model.md)). In the Python track the main resource is a video that plays in the page. Everywhere else it was mostly a link: of 135 ready topics, 87 sent the learner to a reading on another site and 17 to a video on another site. Leaving the app in the middle of a lesson is where a sitting ends, and the owner asked for the lesson to come to the learner instead.

ADR-0004 says: "Record every external resource's license. Never copy text from sources that don't allow it." Until now every reading was linked, whatever its licence, so the second half of that rule was never used. Many of the readings do allow copying: Creative Commons licences, the Python documentation's licence, US government pages. Others don't: "all rights reserved" pages, and "no derivatives" licences.

## Decision

For each resource, in this order:

1. **A video plays in the page** when YouTube allows it. A video is recorded by its YouTube address and marked `use: embed` after YouTube's oEmbed address confirms embedding is on. YouTube's own player shows it; nothing is copied. Videos beyond the main one play under "More resources".
2. **A reading's own words are shown in the page** when its licence allows copying. The topic keeps a copy of the part the lesson assigns, and the lesson shows it in a box of its own with its credit.
3. **Otherwise the lesson's own text has to carry the topic,** and the outside page stays a link for going deeper. That is writing work, topic by topic, and comes last.

### Which licences allow a copy

`tools/reading_html.py` holds the list (`COPYABLE`), and the validator refuses a copy under anything else:

- Creative Commons BY, BY-SA, BY-NC and BY-NC-SA, and CC0;
- the Python Software Foundation licence, BSD, MIT and Apache licences;
- the GPL, LGPL and GNU Free Documentation License;
- US government works and other public-domain text.

Left out on purpose: any "no derivatives" licence (we show parts of pages, and a part may count as a changed version), anything "all rights reserved", and anything with no licence stated.

### What a copy is

- **A file in the topic's folder,** `readings/<name>.html`, made by `tools/import_reading.py`: it downloads the page, keeps the sections asked for, and cleans them down to a small subset of HTML (paragraphs, headings, lists, code, tables, pictures, links, formulas). The words stay the source's, in order. Nothing of ours is mixed in, and our lesson text stays outside the box.
- **Recorded on the resource** in `topic.yaml` under `text:`: the file, who it is by, the address of the licence, the day it was copied, and what was changed. A source's own required words (OpenStax's "Access for free at ...") go in `notice`. The app shows all of it under the text, with a link to the original.
- **Pictures are not copied.** They load from the source's own site, on a light ground so a diagram drawn for a white page still reads in dark mode.
- **Formulas are MathML,** which browsers draw themselves, so no formula library is needed. One old tag browsers no longer draw (`<mfenced>`, a pair of brackets) is rewritten as ordinary brackets by the importer, and the change is stated.

### Three guards against a copied page doing harm

A copied page is somebody else's HTML, so it is never trusted:

1. the importer keeps only the allowed tags and attributes;
2. the content validator, in CI, refuses a committed file with anything else in it;
3. the app never hands the text to the browser as HTML: it rebuilds each allowed tag as an element with only its allowed attributes (`web/src/content/readingHtml.tsx`). Links must be full `https://` addresses and open beside the lesson.

### Step 3 in practice: a lesson that stands on its own text (added 2026-11-22)

When neither a video nor a copy can carry a topic, the lesson's own text must. The test is the topic's own items: for every objective, quick question, exercise, lab check and line of the explain rubric, some sentence of the lesson's own text prepares the learner for it. Whatever only an outside page taught is the gap, and it is written into the lesson in our own words, never copied or closely paraphrased, with facts checked against primary sources.

Then every linked page of the topic gets `optional: true` in `topic.yaml`. The app shows the main one under "Go deeper (optional)", the lesson's "Read now" paragraph becomes a short note of what each page adds, and `estimated_minutes` drops by the reading time it used to count and rises by the new text at 130 words a minute.

### What does not change

The time a topic takes already counted the reading. What counts as learned, the questions, and the lesson's own text are untouched. A copy is downloaded only when it is shown: the main reading with the last part of the lesson, a further one when the learner opens it.

## Alternatives considered

- **Showing the other site inside a frame.** Most sites forbid it (their servers tell browsers not to), and those that allow it bring their menus, banners and cookie prompts with them.
- **Fetching the page when the learner opens the lesson.** It needs a service of ours in the middle, the page can change or vanish under a lesson written around it, and nothing could be checked beforehand.
- **Converting pages to Markdown.** Tables, formulas and figures don't survive it well, and it invites small rewordings. Plain HTML keeps the source's words and structure as they are.
- **Rewriting every reading in our own words now.** It is the fallback, not the first choice: the owner's order puts it last, and a good source's own explanation, credited, is worth more than a hurried paraphrase.
- **Copying under "no derivatives" licences in full.** Possible in principle for a whole, unchanged chapter, but our lessons assign parts of chapters, and the safe reading is to link those.

## Consequences

- **Non-commercial licences now matter.** Much of the copied text (OpenStax, Runestone, DigitalOcean, MIT's Missing Semester) is "NC": free to share, not for commercial use. The app is free, so this is fine today. If it ever charges money or carries advertising, those copies must come out first, back to links. Each is marked by its licence in `topic.yaml`, so they can be found with one search.
- **"Share alike" licences** (Wikipedia, MDN, the NC-SA books) ask that changed versions carry the same licence. A copy here is the source's text with parts left out, shown under its own licence in its own box, and our lesson around it is a separate work.
- **The repository now holds other people's text.** It is public, so this is redistribution, which these licences allow with credit. Every copy's credit lives beside it in `topic.yaml`.
- **A copy can go stale.** The source may be corrected after the day in `retrieved`. Re-running the importer refreshes it, and the diff shows what changed.
- **Not every topic can have a video or a copy.** About 15 main readings are link-only (AWS documentation, Brendan Gregg, Beej's guides, Julia Evans and others). Those wait for step 3.
- **Pictures depend on the source's site staying up.** If one moves, the picture is missing and the text still reads; the alt text stays.
