# To draft a new release

Requirements:
  + `uv` (see https://docs.astral.sh/uv/)
  + A PyPI account/token

1) Update `hciw/version.py`. This is the single source of truth; the version in `pyproject.toml` is read from it dynamically.
2) Update `CHANGES.rst`.
3) Run `uv lock` and commit the updated `uv.lock`.
4) Push to GitHub and draft new release on GitHub.
5) Build distribution with: `uv build`.
6) Push to PyPI with: `uv publish`.
