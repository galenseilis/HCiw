# Installing HCiw

HCiw requires Python 3.12 and is managed with [uv](https://docs.astral.sh/uv/). The project is not yet published to PyPI, so install it from source:

``` text
$ git clone https://github.com/galenseilis/HCiw.git
$ cd HCiw
$ uv sync
```

This creates a virtual environment with HCiw installed in editable mode, together with the dependencies needed for testing and building the documentation. Activate it, or prefix commands with `uv run`:

``` python
$ uv run python -c "import hciw; print(hciw.__version__)"
```

You can also install without uv using any PEP 517 frontend:

``` text
$ pip install .
```

Installation requires Python 3.12.
