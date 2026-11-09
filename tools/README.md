# Tools

Python tooling for the repository. It runs with uv, on the same Python minor version as Pyodide (see the root `pyproject.toml`).

| File | What it does |
|---|---|
| `validate_content.py` | Checks everything in `content/` (see [content/README.md](../content/README.md)). CI runs it on every pull request. |
| `content_model.py` | The shapes of the content files, as pydantic models. Unknown fields are errors, so typos get caught. |
| `outline_cloud_track.py` | Reads the Cloud Solutions Architect spec and writes its track and `planned` topic outlines into `content/`. It never overwrites a topic that's being written. |
| `tests/` | Proves the validator accepts good content and catches each kind of mistake, using a tiny complete topic (`content_fixture.py`), and that the outline generator writes content the validator accepts. |

The validator runs code through `harness/cli.py`, in a fresh Python process per program, which is exactly what the browser runs. It never imports learner code into its own process.

```text
python -m uv run python tools/validate_content.py      check all content
python -m uv run python tools/outline_cloud_track.py   refresh the cloud track's outlines from its spec
python -m uv run pytest                                run the harness and tool tests
```
