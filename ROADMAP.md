# HCiw Roadmap

HCiw is now a fork of the Ciw queueing-network simulator (`hciw/` package, dist name `HCiw`). Before the fork, this project was a healthcare-oriented wrapper around Ciw, also named HCiw. That wrapper's source is archived in `old/` (its modules are under `old/src/hciw/`, tests under `old/tests/`, example under `old/examples/`, packaging in `old/pyproject.toml`). `old/` is frozen; nothing there is imported at runtime.

The archived modules below are candidates. None are committed to; each should be evaluated on its own when its feature area next changes in `hciw/`.

## Candidates to integrate

Priority depends on how valuable the feature is to healthcare simulation work.

- `old/src/hciw/waitlist.py` — Warm-start a simulation with a pre-existing backlog of customers (`create_existing_customers_from_list`, `accept`, `begin_service_if_possible_accept`). High value for healthcare workloads that start from an existing waitlist. Natural home: a warm-start/initial-conditions facility in `hciw`. Note the code manipulates `hciw.Node` internals, so it must be re-checked against the current `hciw/` node implementation after the restructure.
- `old/src/hciw/disciplines.py` — `wait_time_over_benchmark`: a service discipline that serves the individual furthest past a per-class `benchmark` (target wait time). Natural home: `hciw/disciplines.py`. Needs a way to attach `benchmark` to customer classes and a `simulation` reference on individuals (individuals in the current `hciw` carry `simulation`; verify).
- `old/src/hciw/server_schedules.py` — `weekday_server_sched`: builds a weekday/weekend shift template (`Schedule` input). Natural home: `hciw/schedules.py` as a schedule helper.
- `old/src/hciw/results.py` — `summarize_individuals` and related result helpers (pandas). Natural home: a `hciw` results helper or an example. Depends on pandas, which is only a dev/docs dependency today.
- `old/src/hciw/nodes.py` — `SKRouter`: a node router that picks the next node from a scikit-learn model. Usable as-is against the current router API; could live in `hciw/routing/` or be kept as a separate extension.

## Candidates to discard

- `old/src/hciw/distributions.py` — `SeqPMFNaive`: a sequence-of-PMF time-dependent distribution. The current `hciw.dists` already provides time-dependent and sequential distributions, so this one is likely superseded.
- `old/tests/service_disciplines.py`, `old/tests/test_waitlist.py`, `old/tests/test_server_schedules.py` — port the relevant tests if the matching modules are integrated; otherwise discard with them.
- `old/examples/example.py` — example driving the wrapper; superseded by the docs tutorials.
- `old/requirements*.lock`, `old/README.md`, `old/pyproject.toml` — obsolete packaging metadata, discard when the archive is pruned.

## Standing ideas (not from `old/`)

- Review upstream Ciw issues for fixes/features worth porting back.
- Improve or fill gaps in the Ciw feature surface that prompted the original wrapper (e.g., warm starts, healthcare-oriented service disciplines).

## Python and platform support

- Update Python support to the latest LTS version(s). The project currently targets 3.12 only (`requires-python = ">=3.12,<3.13"`, `.python-version = 3.12.3`); broaden the supported range to current LTS lines and drop end-of-life ones as they age. Validate the full `unittest` suite and the `.md`/`.rst` doctests on every supported version, since version-specific breakage is real (e.g. the `TypeError: cannot pickle 'itertools.cycle' object` failure on 3.14 from deep-copying distributions in `Simulation.find_arrival_dists`).

## Documentation and branding

- ~~Give the documentation a style distinct from Ciw's.~~ **Done:** the docs were migrated from Sphinx/rST to MkDocs with the Material theme (`mkdocs.yml`, `docs/javascripts/mathjax.js`), and `docs/_static/style.css` is now a small Material override rather than Ciw's Sphinx styling.
- Replace the logo and favicon with HCiw-specific artwork. A placeholder is in place (`docs/_static/hciw-logo.svg`, `hciw-favicon.svg`, wired to `theme.logo`/`theme.favicon` in `mkdocs.yml`), but final artwork should be designed or commissioned. The Ciw-derived assets (`logo.png`, `logo.svg`, `logo.pdf`, `logo_small.png`, `favicon.ico`) remain in `docs/_static/` unused and can be deleted once the final assets land.
- (Context) The docs are already published to GitHub Pages via `.github/workflows/docs.yml` at https://galenseilis.github.io/HCiw/.
- Structure the documentation around **Diátaxis** (https://diataxis.fr/), which separates four modes: tutorials (learning-oriented), how-to guides (task-oriented), reference (information-oriented), and explanation (understanding-oriented). The existing tree already maps closely to this and should keep doing so: `docs/Tutorial/` (tutorials), `docs/Guides/` (how-to guides), `docs/Reference/` (reference), and `docs/Background/` (explanation). Keep each page in a single mode and split any page that blends a how-to with explanation as it is touched.
- Keep the quadrants pure and site project meta outside them: citation, contributing, change log, and authors live in `docs/Project/`, not `docs/Reference/`, and installation is a how-to under `docs/Guides/`. `docs/Reference/` then holds only API-shaped reference (parameters, results, distributions, routers, state trackers) plus the glossary.
- Generate the API reference from docstrings with MkDocs + [mkdocstrings](https://mkdocstrings.github.io/) (`docs/Reference/api.md`), and keep all public modules, classes, functions, and methods documented with **Google-style** docstrings so they render.

## Code and documentation style

- Adopt Google's Python style for code and docstrings, following the `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html>`_.
- Convert docstrings to `Google style <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ section headings (`Args:`, `Returns:`, `Raises:`, `Yields:`, `Attributes:`, `Examples:`, `Note:`, `Todo:`) rather than the current NumPy/Sphinx-style `Parameters`/`Returns` blocks. The `hciw/` sources are largely NumPy-style today; migrate opportunistically as files are touched, and prefer Google style for all new code.
- ~~Adopt the `Ruff formatter <https://docs.astral.sh/ruff/formatter/>`_ and the `Ruff linter <https://docs.astral.sh/ruff/linter/>`_~~ **Done:** Ruff is authoritative, configured under `[tool.ruff]` in `pyproject.toml` with the `E`, `F`, `W`, `I`, `UP`, `B`, `S`, `SIM`, and `RUF` rule families at 88 columns; `uv run ruff check` and `uv run ruff format --check` are clean. Enabling the `D` docstring rules remains outstanding.
- When enabling the `D` (pydocstyle) rules, select the `google` convention (`[tool.ruff.lint.pydocstyle] convention = "google"`); choose an opt-out for individual rules only where they conflict with the style guide rather than with preference.
- Google-style docstrings render through mkdocstrings (`docstring_style: google` in `mkdocs.yml`), so no separate docstring-conversion extension is required.
- Line length: the Ruff formatter's default of **88 columns** is now authoritative; `.pylintrc` (`max-line-length=240`) has been retired. This overrides the Google guide's 80-column recommendation for this project.
- **Tie-break policy (decided):** when neither the Google style guide nor PEP 8 decides a formatting/linting conflict, **Ruff defaults win**. Do not fight the formatter. Where a case genuinely matters, add a targeted suppression (`# noqa` / `per-file-ignores`) with a short, specific justification (e.g. a code comment or a note in this file). Record any lasting exception below.

### Ruff exceptions

- `S101` (`assert`) is ignored globally: `assert` is used throughout `hciw/` for internal invariants and for type narrowing, and is stripped under `-O`.

## Conventions

- Do not edit files under `old/`. When a candidate is pulled into `hciw/`, move it into the live tree and delete it from `old/`, keeping the fork attribution in `AUTHORS.md`.
- Keep the roadmap honest about origins: when integrating, credit the original Ciw code it is based on.
