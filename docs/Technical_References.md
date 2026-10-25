# Technical references

- [Original pandas issue 70770](https://github.com/pandas-dev/pandas/issues/70770)
- [Merged PR 70773](https://github.com/pandas-dev/pandas/pull/70773)
- [Pinned merge source](https://github.com/pandas-dev/pandas/blob/bcd184af891a5231717259d9b77634fc9d071cad/pandas/core/arrays/_arrow_string_mixins.py)
- [StringDtype method call sites](https://github.com/pandas-dev/pandas/blob/bcd184af891a5231717259d9b77634fc9d071cad/pandas/core/arrays/string_arrow.py)
- [pandas 3.1.0 release notes](https://pandas.pydata.org/pandas-docs/version/3.1.0/whatsnew/v3.1.0.html)
- [String dtype migration](https://pandas.pydata.org/docs/user_guide/migration-3-strings.html)
- [Python 3.12 re](https://docs.python.org/3.12/library/re.html)
- [RE2 syntax](https://github.com/google/re2/wiki/Syntax)
- [Whitespace issue 70991](https://github.com/pandas-dev/pandas/issues/70991)
- [Separate proposed whitespace PR 71025](https://github.com/pandas-dev/pandas/pull/71025)
- [Separate Unicode-escape PR 71383](https://github.com/pandas-dev/pandas/pull/71383)
- [Separate end-anchor PR 71387](https://github.com/pandas-dev/pandas/pull/71387)

PR 70773 changed the Python fallback selection in ArrowStringArray/StringDtype call sites; it does not establish equivalent behavior in ArrowExtensionArray/ArrowDtype. Reviewer comments document shared traversal and the strengthened Japanese boundary fixture. Other regex repairs in the release must be attributed separately. The scripts and datasets here are release-package comparisons, not the merged PR's full test suite.
