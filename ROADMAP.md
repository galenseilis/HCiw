# HCiw Roadmap

HCiw is now a fork of the Ciw queueing-network simulator (`hciw/` package, dist name `HCiw`). Before the fork, this project was a healthcare-oriented wrapper around Ciw, also named HCiw. That wrapper's source is archived in `old/` (its modules are under `old/src/hciw/`, tests under `old/tests/`, example under `old/examples/`, packaging in `old/pyproject.toml`). `old/` is frozen; nothing there is imported at runtime.

The archived modules below are candidates. None are committed to; each should be evaluated on its own when its feature area next changes in `hciw/`.

## Candidates to integrate

Priority depends on how valuable the feature is to healthcare simulation work.

- ~~`old/src/hciw/waitlist.py` — Warm-start a simulation with a pre-existing backlog of customers (`create_existing_customers_from_list`, `accept`, `begin_service_if_possible_accept`).~~ **Done:** integrated as `hciw/waitlist.py` with `create_existing_customers_from_list` and `accept`, reusing the current `Node.accept` / `Node.begin_service_if_possible_accept` machinery rather than duplicating node internals. Historical arrival dates are preserved (so waiting times include time before the simulation starts) while service begins at time zero, and the arrival node's counters are advanced past seeded identifiers so later arrivals are not given duplicates. Seeding registers the seeded end-of-service dates as node events (so simulated time never moves backwards), initialises each individual's routing via `Router.initialise_individual` (so `ProcessBased` routing works), and refreshes the state tracker's initial history entry so the seeded backlog is reflected in state probabilities and deadlock detection. The backlog can also be passed to `Simulation` via the `initial_individuals` argument. Covered by `tests/test_waitlist.py` and the "How to Warm-Start a Simulation" how-to guide. The archived copy under `old/` is now redundant.
- `old/src/hciw/disciplines.py` — `wait_time_over_benchmark`: a service discipline that serves the individual furthest past a per-class `benchmark` (target wait time). Natural home: `hciw/disciplines.py`. Needs a way to attach `benchmark` to customer classes and a `simulation` reference on individuals (individuals in the current `hciw` carry `simulation`; verify).
- `old/src/hciw/server_schedules.py` — `weekday_server_sched`: builds a weekday/weekend shift template (`Schedule` input). Natural home: `hciw/schedules.py` as a schedule helper.
- `old/src/hciw/results.py` — `summarize_individuals` and related result helpers (pandas). Natural home: a `hciw` results helper or an example. Depends on pandas, which is only a dev/docs dependency today.
- `old/src/hciw/nodes.py` — `SKRouter`: a node router that picks the next node from a scikit-learn model. Usable as-is against the current router API; could live in `hciw/routing/` or be kept as a separate extension.

## Candidates to discard

- `old/src/hciw/distributions.py` — `SeqPMFNaive`: a sequence-of-PMF time-dependent distribution. The current `hciw.dists` already provides time-dependent and sequential distributions, so this one is likely superseded.
- `old/tests/service_disciplines.py`, `old/tests/test_waitlist.py`, `old/tests/test_server_schedules.py` — port the relevant tests if the matching modules are integrated; otherwise discard with them. (`old/tests/test_waitlist.py` was mock-based and depended on the old node internals; it has been superseded by `tests/test_waitlist.py`.)
- `old/examples/example.py` — example driving the wrapper; superseded by the docs tutorials.
- `old/requirements*.lock`, `old/README.md`, `old/pyproject.toml` — obsolete packaging metadata, discard when the archive is pruned.

## Standing ideas (not from `old/`)

- Review upstream Ciw issues for fixes/features worth porting back.
- Give nodes optional aliases so code and outcomes can refer to them by a readable name instead of a numeric index. For example, `create_network` could accept a `node_names` (or `aliases`) argument mapping node indices to names, exposing them on the node objects and using them in records, trackers and reports. This would make networks easier to read and interpret.
- Give individuals their own discrete-event processes so their properties can change over time, independent of service and routing events. This would let individuals accumulate continuous or stepwise state, such as a severity-of-illness score that worsens while waiting, and attach time-dependent attributes that disciplines, routing and trackers can condition on.
- ~~Fix exact-arithmetic (`exact=True`) wrap-up: `Node.wrap_up_servers` adds a `Decimal` to a server's `busy_time` that is still the initial `float` `0.0` when a server is still busy at the end of the run, raising `TypeError: unsupported operand type(s) for +=: 'float' and 'decimal.Decimal'`.~~ **Done:** `Server` now derives its initial `busy_time` and `total_time` zeros from the type of its `start_date`, so exact-mode servers accumulate `Decimal` times from the outset; this also fixes the `TypeError` raised when a node sums a never-used server's times into its utilisation. Covered by `tests/test_server.py`. (Note: passing `exact=True` still sets the `Decimal` precision to `1`, breaking event scheduling; use an integer precision such as `exact=26`, as the documentation does.)
- Improve or fill gaps in the Ciw feature surface that prompted the original wrapper (e.g., warm starts, healthcare-oriented service disciplines).

## Models

Add a directory of named models (`hciw/models/`) that users can instantiate directly and, where applicable, fit to data. Each model declares its parameters: the user may fix any subset of them, and the remaining parameters are the ones estimated when fitting. A parameter that has been fixed by the user is never treated as a fitted parameter, so a single model object supports both fully-specified simulation and calibration from observed data.

- Begin with the classic queueing systems (e.g. M/M/1, M/M/c, M/G/1, M/G/c, and finite-capacity, priority and multi-class variants), each exposing its arrival process, service distribution, number of servers and capacity as parameters.
- Include the hybrid DES+SD model described in the [DES+SD hybrid guide](docs/Guides/System/behaviour/hybrid.md) (Palmer and Tian, [GP21]), which couples the discrete-event simulation to a system-dynamics component.
- Add other less-typical models that are essentially queueing or adjacent to it, such as queueing networks, retrial and vacation queues, fluid and diffusion approximations, and healthcare flow models (e.g. emergency-department or bed-occupancy models).
- Keep the simulation-side models free of new runtime dependencies; the fitting machinery may rely on a numerical/statistics stack (e.g. SciPy), which is acceptable to add as a dependency for that purpose.

## Performance benchmarks

Add a benchmark suite and track performance over the project's lifetime, so that regressions are caught deliberately rather than discovered by users. The aim is the capability, not a specific tool; the choice should follow from what fits the project's `uv`-based, `unittest`-based toolchain and its MkDocs/GitHub Pages publishing.

- **Recommended primary tool: [airspeed velocity](https://asv.readthedocs.io/en/latest/index.html) (`asv`).** It is standalone (benchmarks are plain Python classes, so the project need not adopt `pytest`), now has first-class `uv` support (`asv.plugins.uv`), tracks runtime and memory across git commits and releases, and publishes an interactive HTML dashboard that fits the existing GitHub Pages workflow. It is the de facto standard in scientific Python (astropy, numpy, scipy), which is close in spirit to HCiw.
- **Benchmark content:** seed the RNG for stability, then micro-benchmark distribution sampling and `Individual`/`Node` operations, and measure end-to-end simulation throughput (individuals and events per second) on representative networks, parametrised over network size. Unlike micro-benchmarks, these are unavoidably long-running, which is the main reason to track them per release rather than per commit.
- **Where to run it:** `asv` wants stable hardware, so run the suite on a schedule on a dedicated or self-hosted runner and publish results alongside the docs. It is a poor fit for noisy pull-request runners.
- **Per-PR regression checks (optional, complementary):** for fast feedback on pull requests, consider [CodSpeed](https://codspeed.io/) (free for open source, calibrates for noisy shared runners, has a GitHub Action, but adds `pytest`/`pytest-codspeed`) or a lightweight `pytest-benchmark`/`pyperf` comparison with a generous threshold (5–10%) to avoid false positives from CI variance.

## Testing

Keep the existing focused, example-based unit tests (including the paired specific/`_h` Hypothesis cases) — they are valuable and should stay — but lean on [Hypothesis](https://hypothesis.readthedocs.io/) much more, using broad generated inputs rather than only hand-picked ones. `hypothesis` is already a dev dependency, so this is about how the tests are written, not new tooling.

- Build a shared library of reusable Hypothesis strategies ("schemas") for the domain — distributions, `ServiceCentre`/`CustomerClass`/`Network` objects, `Individual`s, and small `Simulation`s — in a shared test module (e.g. `tests/strategies.py`) instead of bespoke inline `@given` arguments repeated per test. Use `hypothesis.strategies.composite`, `builds`, and (for annotated types) `from_type`.
- Prioritise strategy builders that generate valid, internally consistent networks (routing rows that sum to one, matching class names, sensible server and capacity counts) so tests can focus on behaviour instead of building fixtures.
- Move from round-tripping constructor arguments towards genuine properties and invariants, for example: seeded runs are reproducible; simulated time never moves backwards; individuals are conserved (arrivals minus exits equals the number in the system); records and state-tracker histories are well formed and consistent; routing probabilities and sampled values stay within their supports.
- Keep the generated-example database (`.hypothesis/`) gitignored, and use `@settings`/Hypothesis profiles to keep the default run fast in CI while allowing longer, higher-`max_examples` runs locally or on a schedule.
- Add [mutmut](https://mutmut.readthedocs.io/) mutation testing as an ancillary quality check, run periodically rather than on every pull request (it is slow). It alters the source (integer literals, `<` to `<=`, `break` to `continue`, and so on) and reports the mutants the tests fail to catch, pointing at behaviour that is under-tested so that mutation bugs can be found and covered preemptively. Add targeted tests for the meaningful survivors, but do not treat every survivor as a defect: some mutations are equivalent or simply not worth testing, so use the score as guidance rather than a hard gate. Configure `[tool.mutmut]` with `source_paths = ["hciw"]` and the `tests/` selection, and use `# pragma: no mutate` (or the type-checker filter) to suppress intentional noise. Note that mutmut 3+ drives `pytest`, so this would require `pytest` as a test runner even though the suite is written with `unittest`; it also needs POSIX fork support (fine on Linux, WSL on Windows).

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
- ~~Adopt the `Ruff formatter <https://docs.astral.sh/ruff/formatter/>`_ and the `Ruff linter <https://docs.astral.sh/ruff/linter/>`_~~ **Done:** Ruff is authoritative, configured under `[tool.ruff]` in `pyproject.toml` at 88 columns; `uv run ruff check` and `uv run ruff format --check` are clean. The linter enables **every** stable rule (`select = ["ALL"]`), including `D` (pydocstyle), and excludes only the rules that contradict another rule, the formatter, or a deliberate project convention. Every exclusion is documented in `pyproject.toml` and mirrored below.
- `D` uses the `google` convention (`[tool.ruff.lint.pydocstyle] convention = "google"`); individual `D` rules are opted out only where they conflict with the style guide rather than with preference.

### Ruff exceptions

Beyond the formatter-conflict rules (`COM812`, `COM819`, `ISC001`, `Q000`–`Q003`, which the formatter owns), the global `ignore` list is:

- `S101` (`assert`) — `assert` is used throughout `hciw/` for internal invariants and for type narrowing, and is stripped under `-O`.
- `PT009`, `PT027` — the suite is written with `unittest`; the pytest-style equivalents of its idioms are intentionally unused.
- `ANN001`, `ANN201`, `ANN202`, `ANN204`, `ANN401` — a full type-annotation layer is a separate, large effort, and Google Style treats annotations as optional (deferred; see above).
- `ARG001`, `ARG002` — unused parameters are overwhelmingly base-class/interface signatures (the `_sample(self, t, ind)` distribution interface, routing hooks, etc.); re-annotating them would desynchronise the documented interface.
- `TRY003`, `EM101`, `EM102` — opinionated exception-message rules; Google Style and PEP 8 are silent on this and the codebase favours inline messages.
- `SLF001` — access to underscore-prefixed members is intentional within the library and in tests that exercise private helpers.
- `CPY001` — attribution is centralised in `LICENSE.txt` and `AUTHORS.md` rather than in per-file copyright headers.
- `FBT001`, `FBT002` — boolean positional parameters (`completed=False`, `exact=False`, `progress_bar=False`, ...) are part of the Ciw-derived public API; making them keyword-only would break source compatibility with Ciw.

Per-file exceptions are used where a rule conflicts with a file's deliberate conventions:

- `hciw/disciplines.py`: `N802` — `FIFO`/`SIRO`/`LIFO` are the public service-discipline names (queueing acronyms).
- `tests/**`: `D`, `FBT`, `N803`, `N805`, `N806`, `PLR0915`, `PLR2004`, `PTH` — the test suite is self-describing, uses the tutorial `N`/`Q` notation, and bundles many example-based assertions per test.
- Google-style docstrings render through mkdocstrings (`docstring_style: google` in `mkdocs.yml`), so no separate docstring-conversion extension is required.
- Line length: the Ruff formatter's default of **88 columns** is now authoritative; `.pylintrc` (`max-line-length=240`) has been retired. This overrides the Google guide's 80-column recommendation for this project.
- **Tie-break policy (decided):** when neither the Google style guide nor PEP 8 decides a formatting/linting conflict, **Ruff defaults win**. Do not fight the formatter. Where a case genuinely matters, add a targeted suppression (`# noqa` / `per-file-ignores`) with a short, specific justification (e.g. a code comment or a note in this file). Record any lasting exception above, under "Ruff exceptions".

## Conventions

- Do not edit files under `old/`. When a candidate is pulled into `hciw/`, move it into the live tree and delete it from `old/`, keeping the fork attribution in `AUTHORS.md`.
- Keep the roadmap honest about origins: when integrating, credit the original Ciw code it is based on.
