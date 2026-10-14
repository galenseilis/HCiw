"""Test hook(s) for Doctests in Markdown (.md) and reStructuredText (.rst) files."""

import doctest
import os
import unittest
import sys
from typing import Any


class _FenceStrippingParser(doctest.DocTestParser):
    """DocTestParser that ignores Markdown fenced code-block markers.

    Doctest examples live inside fenced blocks (```` ``` ````) in the Markdown
    documentation. The fence lines are not valid doctest input or expected
    output, so they are removed before parsing.
    """

    def get_doctest(
        self,
        string: str,
        globs: dict,
        name: str,
        filename: str | None,
        lineno: int | None,
    ) -> doctest.DocTest:
        string = "\n".join(
            line for line in string.splitlines()
            if not line.lstrip().startswith("```")
        )
        return super().get_doctest(string, globs, name, filename, lineno)


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, ignorex: Any) -> unittest.TestSuite:
    """
    Discover and add all Markdown (.md) and reStructuredText (.rst) doctest files within the current directory tree to the test suite.

    Parameters
    ----------
    loader : unittest.TestLoader
        The test loader instance used to load the tests.
    tests : unittest.TestSuite
        The existing test suite to which doctest suites will be added.
    ignorex : Any
        A placeholder parameter (typically unused) required by the unittest framework.

    Returns
    -------
    unittest.TestSuite
        The updated test suite including all discovered .md and .rst doctest files.

    Notes
    -----
    This function is used by the unittest framework to discover and include additional doctests
    in the test suite during test discovery.

    Examples
    --------
    When placed in a test module, unittest will automatically call `load_tests` if it exists.

    >>> import unittest
    >>> suite = unittest.TestSuite()
    >>> loader = unittest.TestLoader()
    >>> load_tests(loader, suite, None)  # doctest: +ELLIPSIS
    <unittest.suite.TestSuite tests=[...]
    """
    skip_dirs = {"__pycache__", "_build", "build", "dist", "site"}
    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d for d in dirs
            if d not in skip_dirs and not d.startswith(".") and d != "old"
        ]
        for f in files:
            if f.endswith((".md", ".rst")):
                tests.addTests(
                    doctest.DocFileSuite(
                        os.path.join(root, f),
                        optionflags=doctest.ELLIPSIS,
                        parser=_FenceStrippingParser(),
                    )
                )
    return tests


if __name__ == "__main__":
    if sys.version_info >= (3, 6):
        unittest.main()

