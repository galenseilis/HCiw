# How to Contribute

Contributions from anyone are awesome! This may include opening issues, communicating ideas for new features, letting us know about use cases of the library, and code contributions. We would love to receive your pull requests. Here's a handy guide:

Fork, then clone the repo:

``` text
git clone https://github.com/galenseilis/HCiw.git
```

HCiw uses [uv](https://docs.astral.sh/uv/) with `pyproject.toml` and a committed `uv.lock`. The pinned interpreter is Python 3.12 (see `.python-version`); other versions are not currently supported. Create the development environment (runtime plus the `dev` dependency group) with:

``` text
uv sync
```

Make sure the tests pass (HCiw uses unit & doc testing):

``` text
uv run python -m unittest discover
uv run python doctests.py
```

We encourage the use of coverage, ensuring all aspects of the code are tested:

``` python
uv run coverage run --source=hciw -m unittest discover
uv run coverage report -m
```

Add tests for your change. Make your change and make the tests pass.

Please update the documentation too, and ensure doctests pass. To build the documentation:

``` text
uv run mkdocs build
uv run mkdocs serve
```

Push to your fork and submit a pull request!

Some ideas of where to begin:

- Take a look at the [open issues for the upstream Ciw project](https://github.com/CiwPython/Ciw/issues).
- The [ROADMAP.md](https://github.com/galenseilis/HCiw/blob/main/ROADMAP.md) lists HCiw-specific work, including integrating or discarding the archived code under [old/](https://github.com/galenseilis/HCiw/tree/main/old).

We look forward to your contributions!
