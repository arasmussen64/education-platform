# Tools

Python tooling for the repository. It runs with uv, on the same Python minor version as Pyodide (see the root `pyproject.toml`).

| File | What it does |
|---|---|
| `validate_content.py` | Checks everything in `content/` (see [content/README.md](../content/README.md)). CI runs it on every pull request. |
| `content_model.py` | The shapes of the content files, as pydantic models. Unknown fields are errors, so typos get caught. |
| `tests/` | Proves the validator accepts good content and catches each kind of mistake, using a tiny complete topic (`content_fixture.py`). |

The validator runs code through `harness/cli.py`, in a fresh Python process per program, which is exactly what the browser runs. It never imports learner code into its own process.

```text
python -m uv run python tools/validate_content.py   check all content
python -m uv run pytest                             run the harness and tool tests
```
