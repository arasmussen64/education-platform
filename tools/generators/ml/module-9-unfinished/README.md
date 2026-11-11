# Unfinished: the generator for `ml.tf.tokens-and-embeddings`

`gen_ml_tf_tokens.py` was being written on 2026-11-10 for the first topic of Module 9 (Transformers). It has never written a file: the topic in `content/topics/` is still a `planned` outline.

## Where it stops

Run into a scratch folder (see [the archive's README](../../README.md#looking-at-what-a-generator-would-write-without-touching-the-content)), it prints the outputs of the worked example and of the write, build and debug exercises, all of which pass their own checks, and then stops at line 572:

```text
    assert REVIEW_CODE_OUT == "[6, 1, 4] gain  in\n", REVIEW_CODE_OUT
AssertionError: [6, 1, 4] gain  no
```

An assertion is a line that stops the script when something it expects isn't true. Here the script expected the review exercise's solution to print `[6, 1, 4] gain  in`, and the solution printed `[6, 1, 4] gain  no`.

## Why

The program is right; the expected text in the assertion was typed wrong. The exercise builds its vocabulary from `"no pain no gain"`. Sorted, its characters are a space, `a`, `g`, `i`, `n`, `o`, `p`, numbered 0 to 6. The last thing printed is `decode([0, 4, 5], chars)`: character 0 is the space, 4 is `n`, 5 is `o`. So the line ends with a space and `no`, not `in`.

## What is left

- Correct the expected text on line 572.
- Everything below that line has never run: the known-wrong version of that exercise, `topic.yaml`, the lesson, the recall items, and the writing of every file. Expect more assertions to stop the script before it finishes.
- When it does finish, the topic it writes still has to pass `tools/validate_content.py` and be read once as a learner before it is marked `ready`.

From then on the topic's folder in `content/topics/` is what counts, like every other topic's, and this script becomes history.
