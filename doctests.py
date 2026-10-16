"""Test hook(s) for Doctests in Markdown (.md) and reStructuredText (.rst) files."""

import doctest
import os
import unittest
from pathlib import Path
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
            line for line in string.splitlines() if not line.lstrip().startswith("```")
        )
        return super().get_doctest(string, globs, name, filename, lineno)


def load_tests(
    loader: unittest.TestLoader, tests: unittest.TestSuite, ignorex: Any
) -> unittest.TestSuite:
    """Add doctests from Markdown and reStructuredText files to the suite.

    Discovers every ``.md`` and ``.rst`` file in the directory tree and adds
    its doctests to the test suite. Used by the ``unittest`` framework.

    Args:
        loader: The test loader instance used to load the tests.
        tests: The existing test suite to which doctest suites will be added.
        ignorex: Unused placeholder required by the unittest framework.

    Returns:
        The updated test suite including all discovered doctest files.

    Examples:
        When placed in a test module, unittest will automatically call
        ``load_tests`` if it exists.

        >>> import unittest
        >>> suite = unittest.TestSuite()
        >>> loader = unittest.TestLoader()
        >>> load_tests(loader, suite, None)  # doctest: +ELLIPSIS
        <unittest.suite.TestSuite tests=[...]
    """
    skip_dirs = {"__pycache__", "_build", "build", "dist", "site"}
    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if d not in skip_dirs and not d.startswith(".") and d != "old"
        ]
        for f in files:
            if f.endswith((".md", ".rst")):
                tests.addTests(
                    doctest.DocFileSuite(
                        str(Path(root) / f),
                        optionflags=doctest.ELLIPSIS,
                        parser=_FenceStrippingParser(),
                    )
                )
    return tests


if __name__ == "__main__":
    unittest.main()
