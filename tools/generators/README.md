# Generators (an archive)

This folder keeps the scripts that first wrote the Machine Learning Foundations topics, and a few helpers that were used beside them. It is an **archive**: history and reference, not tools to run. Until 2026-11-10 these files lived only in a temporary folder on the owner's PC, where one clean-up would have deleted them.

One generator is still a live tool, and it is not in this folder: `tools/outline_cloud_track.py`, which writes the cloud track's `planned` outlines from its spec ([content/README.md](../../content/README.md) says how to use it).

## The one rule

**`content/topics/` is the source of truth** (the one place that counts when two copies disagree). To change a topic, edit its files in `content/topics/` and run the checker, as [content/README.md](../../content/README.md) describes. Never re-run a script from this folder to change content: most of them would undo fixes that were made after they last ran.

Some of the scripts say "Run from the repository root" in their first lines. That was true while they were in use. It isn't an instruction any more.

## How the ML topics were produced

A **generator** is a program that writes files. Each topic in Modules 1 to 8 of the ML track (bar one, see the table) was written by its own generator, a single Python script named `gen_ml_<topic>.py`. The generators grew more careful as the track went on.

**Modules 1 to 3: a plain file writer.** The script holds the whole topic as text (the lesson, every question, every exercise with its solution, its tests and its known-wrong answers) and writes that text into the topic's files in `content/topics/`. It runs none of the topic's programs and checks nothing: the expected outputs in it were typed in, and it was the validator, afterwards, that proved them right.

**Modules 4 to 8: a writer that checks its own story.** From Module 4 on a generator works in these steps:

1. It holds the whole topic as text, as before.
2. It runs each program in real Python (CPython, the ordinary Python you install) and captures what the program prints. Expected outputs are captured this way instead of being typed in by hand.
3. It checks the topic's story with **assertions**. An assertion is a line starting with `assert` that stops the script if something isn't true. They check things like: this number in the lesson is the number the program printed; this known-wrong answer really does print something different; and, from Module 6 on, the right choice of a multiple-choice question isn't the longest one (a giveaway).
4. It writes the topic's files into `content/topics/`. A failed assertion stops the script on the spot, so a topic whose story doesn't hold is never written in full.

After that, for every module, the validator (`tools/validate_content.py`) ran every exercise, and a **cold review** followed: a reviewer who had never seen the module read it as a beginner would and listed what was wrong or unclear. The instructions those reviewers were given are in `review-briefs/`.

The fixes from those reviews are where the generators and the content parted ways. For Modules 7 and 8 the fix was made in the generator, which was then run again. For Modules 1 to 6 the fix was made straight in `content/topics/`, and the generator was never updated. A generator that no longer produces what is in the repository is called **stale** here.

## What is in this folder

| Folder                   | What it holds                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `ml/module-1` to `-8`    | The topic generators, one per topic, grouped by module. Each script's first lines name the topic it wrote.               |
| `ml/module-9-unfinished` | The generator for Module 9's first topic. It stops at a failing assertion and has never written a file (see below).      |
| `ml/outlines`            | The scripts that added each module's `planned` outlines to the track file, the topic folders and the spec. All have run. |
| `review-briefs`          | The cold-review instructions for Modules 7 and 8.                                                                        |
| `checks`                 | Small scripts that checked content or a generator while a module was being written (listed below).                       |
| `cloud-labs`             | The parts the Cloud Solutions Architect track's Module 1 lab images were assembled from, and the script that did it.     |
| `conftest.py`            | Tells pytest (the test runner) to skip this folder, because importing a generator runs it.                               |

These files are kept as they were when they last ran, so they are not formatted or linted: `pyproject.toml` excludes this folder from ruff. (The one thing git changed is invisible: it stores every line ending the same way, as this repository does for all text files.) Three files were changed on the way in, because this repository is public: the owner's folder path in the two review briefs became `<repo root>`, and `cloud-labs/assemble.sh` now takes the folder to write into from a setting called `TOPICS_DIR` instead of a path on the owner's PC.

## Which generators still matched the content on 2026-11-10

On 2026-11-10 every topic generator was run into an empty scratch folder (a throwaway folder outside the repository) and its output was compared, file by file, with `content/topics/` as it stood after pull request #198, the last change before that day's audit fixes.

| Folder                   | Module                            | Generators | Result on 2026-11-10                                                                                  |
| ------------------------ | --------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
| `ml/module-1`            | 1. Math refresher                 | 7          | **Stale.** All 7 differ from the content (19 files of 311).                                           |
| `ml/module-2`            | 2. Intermediate Python            | 8          | **Stale.** 7 of 8 differ (16 files of 356).                                                           |
| `ml/module-3`            | 3. Linear algebra                 | 8          | **Stale.** 6 of 8 differ (11 files of 364).                                                           |
| `ml/module-4`            | 4. Calculus                       | 8          | **Stale.** All 8 differ (53 files of 372).                                                            |
| `ml/module-5`            | 5. Probability and statistics     | 8          | **Stale.** All 8 differ (64 files of 373).                                                            |
| `ml/module-6`            | 6. Data structures and algorithms | 8          | **Stale.** All 8 differ (46 files of 395).                                                            |
| `ml/module-7`            | 7. How computers and GPUs work    | 8          | **Matched.** All 420 files identical.                                                                 |
| `ml/module-8`            | 8. Neural networks from scratch   | 8          | **Matched.** All 441 files the generators write are identical. Three more files are only in the repo. |
| `ml/module-9-unfinished` | 9. Transformers                   | 1          | Stops at an assertion before writing anything.                                                        |

Notes on the table:

- Module 1 has seven generators for eight topics. `ml.math.vectors-and-matrices` was written by hand and never had one.
- In the stale modules the differences are the review fixes: clearer wording in lessons and explanations, reordered multiple-choice answers, corrected numbers, corrected resource titles, and doubled apostrophes removed. Re-running a stale generator would put the old text back. One Module 5 topic alone, `ml.prob.bayes`, would lose changes in 9 files.
- Three generators in the stale modules happened to match (`ml.m2.checkpoint`, `ml.la.matrices-as-maps`, `ml.la.systems`). That is luck, not a promise. Treat the whole of Modules 1 to 6 as stale.
- The three extra Module 8 files are `wrong/dense-backward-not-transposed.py` in `ml.m8.checkpoint`'s build exercise and its two fresh versions. A review fix renamed that known-wrong answer to `dw-from-the-first-row-only.py` in the generator. A generator only writes files, it never deletes one, so the file with the old name stayed behind.
- "Matched" describes that one moment. The audit fixes that arrived together with this archive were made in `content/topics/` and may have touched Modules 7 and 8 too. **Assume that no generator matches the content today**, and check before you believe otherwise.

## Looking at what a generator would write, without touching the content

A generator writes to `content/topics/<topic>` _relative to the folder it is run from_. Run from the repository root, it overwrites the real topic. Run from an empty folder somewhere else, it builds a harmless copy there, which you can compare with the real one. A **diff** is a listing of the lines that differ between two files or folders.

1. Make an empty scratch folder outside the repository and go into it. On Windows keep its path short, such as `C:\tmp\regen`: Windows refuses paths over 260 characters, and the longest topic file's path is already 129 characters counted from the repository root.
2. Run the generator from there. `--project` tells uv where the repository is, so the script gets the project's Python and NumPy while the files land in the scratch folder. Put the full path of the repository folder where it says `<repo root>`, and keep the quotes, because that path may have a space in it:

   ```text
   python -m uv run --project "<repo root>" python "<repo root>/tools/generators/ml/module-7/gen_ml_hw_bits.py"
   ```

   It prints the outputs it captured and ends with `ml.hw.bits-and-integers written: 48 files`. If an assertion fails it stops with an `AssertionError` and writes nothing after that point.

3. Go back to the repository root and compare the two folders:

   ```text
   git diff --no-index --stat content/topics/ml.hw.bits-and-integers C:/tmp/regen/content/topics/ml.hw.bits-and-integers
   ```

   No output means the two are identical. Leave out `--stat` to see the lines. A line starting with `-` is what the repository has now and would lose; a line starting with `+` is what the generator would write instead.

4. Delete the scratch folder.

If a diff shows something you want, copy that change into `content/topics/` by hand and run the checker. Don't copy the generated folder over the real one.

## The unfinished Module 9 generator

`ml/module-9-unfinished/gen_ml_tf_tokens.py` is the work in progress for `ml.tf.tokens-and-embeddings`, the first Transformers topic, which is still a `planned` outline in the content. Its worked example and its write, build and debug exercises run and pass their own assertions. It then stops at line 572:

```text
assert REVIEW_CODE_OUT == "[6, 1, 4] gain  in\n", REVIEW_CODE_OUT
AssertionError: [6, 1, 4] gain  no
```

The program is right and the expected text typed into the assertion is wrong. The characters of `"no pain no gain"`, sorted, are a space, then `a g i n o p`, numbered 0 to 6, so `decode([0, 4, 5], chars)` is a space, `n`, `o`. Everything after line 572 (the topic file, the lesson, the recall items and every file being written) has never run, so expect more assertions to fail once this one is corrected. The folder's own `README.md` says the same in short.

Module 9 is to be written when the ML track is picked up again. Whether to finish this script or write the topic by hand is open; either way the result that counts is the folder in `content/topics/`.

## The outline scripts

`ml/outlines/` holds six scripts. `gen_ml_outlines.py` created the track file and the `planned` outlines for Modules 1 to 4; the others added Modules 5 to 9, one module each, to the track file, to `content/topics/` and to the spec ([docs/specs/ml-foundations.md](../../docs/specs/ml-foundations.md)). They have done their job, and two of the things they do make them unsafe to run again:

- `gen_ml_outlines.py` writes the whole track file from its own list, which stops at Module 4. Run from the repository root today, it would drop Modules 5 to 9 from the track.
- Every one of them skips a topic that has been written, but overwrites an outline that is still `planned` (Module 9's, today) with its own copy, losing any edit made since.

To change an outline, edit its `topic.yaml`. To change the track, edit `content/tracks/ml-foundations.yaml`.

## The cloud lab parts

Most labs in Module 1 of the Cloud Solutions Architect track run in a container that boots like a small server. A lab's `Dockerfile` (the recipe Docker builds that container from) was not typed out once per lab. `cloud-labs/assemble.sh` glued each one together from a shared beginning (`services/Dockerfile.head`), a part shared by one topic's labs (`<topic>/tail-common`, where there is one) and a part of the lab's own (`<topic>/tail-<lab>`). It also copied the small files a topic's labs share, such as fake services and boot scripts, into each lab's folder. There is one folder per topic. The shell and scripting topics have none, because the script never assembled their labs.

On 2026-11-10 the script reproduced 294 of the 295 files it writes. The one that differs is `csa.linux.triage/exercises/fill-triage-report/Dockerfile`, where a later fix (a stand-in `vmstat` with fixed numbers) was made straight in the content. So the same rule holds here: the files in `content/topics/` count, a change to a lab is made there, and this script is not to be run against the real content as it stands.

One day a change may be needed in the lines every one of these labs shares (a new package for all of them, say), and editing some seventy files by hand invites mistakes. That would be the moment to make this script a real tool again: bring `triage/tail-fill` in line with the committed `Dockerfile`, check that the scratch comparison below shows no difference at all, move the script and its parts out of this archive, and give it a test. Until someone decides that, it stays an archive.

To see what it would write, give it a scratch copy to write into. From the repository root, in Git Bash:

```text
mkdir -p C:/tmp/regen
cp -r content/topics C:/tmp/regen/topics
TOPICS_DIR=C:/tmp/regen/topics bash tools/generators/cloud-labs/assemble.sh
git diff --no-index --stat content/topics C:/tmp/regen/topics
```

Without `TOPICS_DIR` the script stops and says so. The passwords, keys and tokens in these files (`FakeKeyForTheLabOnly`, `ASIAFAKEFORTHELAB0001` and the like) are invented for the labs and open nothing.

## The checks

Run from the repository root with `python -m uv run python tools/generators/checks/<name>`. The one exception is `check_resources.sh`, a shell script: run it in Git Bash with `bash tools/generators/checks/check_resources.sh`. They read the content and never edit it. Several have one module's topic names written into them, so read a script before trusting its output for another module.

| Script                                                                               | What it does                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate_one.py <topic id>...`                                                      | The validator's checks for the named topics only, in seconds instead of minutes. It leaves out the two checks that aren't per topic (choices named by position, and the placement test's questions), so the full validator must still pass. |
| `check_mcq_lengths.py <generator.py>`                                                | Lists the multiple-choice questions in a generator whose right answer is the longest choice.                                                                                                                                                |
| `check_recall.py .`                                                                  | Module 8: runs every predict-the-output item and compares the output; flags right answers that are the longest choice.                                                                                                                      |
| `mcq_check.py content/topics <topic id>...`                                          | The same for any topics you name, and it also runs each Parsons item's lines.                                                                                                                                                               |
| `mcq_tally.py`, `audit_items.py`, `revA_check.py`                                    | Tallies for Modules 5, 6 and 8: answer positions, choice lengths, skill ids that don't exist, doubled apostrophes, unpaired backticks.                                                                                                      |
| `yaml_apostrophes.py content/topics`                                                 | Module 5: finds a doubled apostrophe (`''`), which shows up as two characters on the page.                                                                                                                                                  |
| `check_resources.sh`                                                                 | Module 8: downloads each of the module's 19 linked resource pages and prints its title and section names, to compare with what `topic.yaml` says. It needs the internet.                                                                    |
| `complexity_checks.py`, `hashing_checks.py`, `sorting_checks.py`, `stacks_checks.py` | The sums behind numbers quoted in four Module 6 topics.                                                                                                                                                                                     |
| `count_trees.py`, `count_checkpoint.py`                                              | Count the comparisons a solution makes, to set the limits in two Module 6 exercises' tests. Give them solution files to count.                                                                                                              |

## What was left behind

The temporary folder held about 630 entries; 237 files came here. Left out on purpose: run logs, drafts of commit messages and pull-request texts, one-off scripts that patched a file once (their results are already in the repository), backup copies, throwaway experiments, and every downloaded web page or video transcript, which are other people's work and are only ever linked from a topic's resources, never copied.
