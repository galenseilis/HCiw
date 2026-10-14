# AGENTS.md

## Repo identity
- HCiw is a fork of the **Ciw** queueing-network simulator (upstream package `Ciw`, version `3.2.7` in `hciw/version.py`). Development and maintenance of Ciw upstream has slowed, so HCiw takes over the Ciw codebase as its starting point.
- Active code is the flat `hciw/` package at repo root, packaged via `pyproject.toml` (setuptools backend, dist name `HCiw`, requires Python `>=3.12,<3.13`). `uv.lock` is committed. Public API is assembled in `hciw/__init__.py`: `hciw.create_network` (in `import_params.py`), `hciw.Simulation`, `hciw.auxiliary` (incl. `hciw.seed`), `hciw.dists`, `hciw.disciplines`, `hciw.schedules.Schedule`, `hciw.routing`, `hciw.trackers`, `hciw.deadlock`.
- Structure differs from upstream Ciw 3.2.7: node logic is split across `arrival_node.py`, `exit_node.py`, `exactnode.py`, `processor_sharing.py`, `server.py`, with `routing/`, `trackers/`, `deadlock/` subpackages. `Simulation(network, exact=prec)` swaps in Decimal-precision `ExactNode`/`ExactArrivalNode`.
- `old/` archives the previous healthcare-oriented `hciw` package built on top of Ciw (rye/hatchling `pyproject.toml`, obsolete) — do not edit `old/`. Its modules are triaged in `ROADMAP.md` (some to integrate, some to discard).
- This project predates the fork as a healthcare wrapper also named HCiw; that context is in `ROADMAP.md` and the README.

## Python version (critical)
- Must use **Python 3.12** (`.python-version` = 3.12.3, mirrored by `requires-python = ">=3.12,<3.13"` in `pyproject.toml`); `python` is not on PATH, and the default `python3` is 3.14.
- On 3.14 the suite fails: `TypeError: cannot pickle 'itertools.cycle' object` (deep-copying distributions in `Simulation.find_arrival_dists`). Use `uv`, which respects `.python-version`.
- Note: an upstream `Ciw 3.2.7` is installed in the user site-packages, so `import ciw` from outside this repo resolves to upstream, not this code. Always `import hciw` here.

## Test commands
- Environment: `uv sync` creates `.venv` with the project (editable) plus the `dev` dependency group (hypothesis, coverage, pandas, mkdocs, mkdocs-material, mkdocstrings). The venv lives at repo root and is gitignored.
- Unit tests (365 tests): `uv run python -m unittest discover`
- Doctests: `uv run python doctests.py` — runs every `>>>` block in all project `.md` and `.rst` files (README.rst, CHANGES.md, docs/...). Separate from `unittest discover`. `doctests.py` strips Markdown code-fence lines and prunes `.venv`, `site/`, hidden dirs, and `old/`; editing any `.md`/`.rst` can break doctests, so run this after doc changes.
- Coverage: `uv run coverage run --source=hciw -m unittest discover && uv run coverage report -m`
- Docs build: `uv run mkdocs build` (add `--strict` to fail on warnings; output in `site/`).
- Release procedure: see `new_release_checklist.md` (bump `hciw/version.py` — the single source of truth, read dynamically by `pyproject.toml` — then `uv lock`, update `CHANGES.md`, `uv build`, `uv publish`).

## Conventions
- Max line length 240 (`.pylintrc`). Roadmap plan: move to the Ruff formatter at 88 columns and retire `.pylintrc`; once Ruff is configured, that becomes authoritative.
- Adopt Google's Python style (Google Python Style Guide) for code and docstrings; existing `hciw/` docstrings are mostly NumPy/Sphinx style, so prefer Google style for new code and migrate touched files. See the style section in `ROADMAP.md`.
- `hciw/dists/.hypothesis/` is generated hypothesis state and gitignored — never commit it.
- Keep the fork attribution honest in prose and citations: upstream Ciw, its authors, the MIT licence (see `LICENSE.txt`), and the published Ciw paper title must be referred to correctly ("Ciw", not "HCiw"). Don't remove Ciw's copyright notice.
- Git history tracks the pre-refactor `hciw` tree; the current `hciw/`, restructured `tests/`, and `docs/` are uncommitted/untracked — the tree is mid-migration.