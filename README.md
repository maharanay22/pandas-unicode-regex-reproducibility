# pandas Unicode regex reproducibility

Reproduction evidence for **When pandas Thinks Café Isn’t a Word: Fixing Unicode Regex Behavior in pandas 3.1.0**, by Maha Rana Yadavalli, and [pandas PR #70773](https://github.com/pandas-dev/pandas/pull/70773).

## Research problem and scope

Python re treats shorthand classes such as \w, \d and \s as Unicode-aware for string patterns, while RE2 uses ASCII shorthand definitions. pandas 3.0 made Arrow storage the default for inferred strings when PyArrow is available, exposing different text-cleaning results. The merged correction uses a selective Python fallback for PyArrow-backed StringDtype/ArrowStringArray. ArrowDtype strings use ArrowExtensionArray and are outside those corrected method call sites.

## Separate experiments

The datasets must not be pooled into a single success percentage. Rows are method/fixture/dtype combinations, not independent statistical observations. Python-backed controls use the same engine as the oracle.

| Dataset | pandas | Comparison rows | PASS | Mismatch | Exception |
|---|---|---:|---:|---:|---:|
| Original expanded suite | 3.0.0 | 600 | 304 | 226 | 70 |
| Original expanded suite | 3.1.0 | 600 | 570 | 20 | 10 |
| Supplementary differential harness | 3.0.0 | 630 | 348 | 232 | 50 |
| Supplementary differential harness | 3.1.0 | 630 | 462 | 128 | 40 |

The original suite crosses 40 fixtures, five methods and three dtype representations. It also asserts missing-value contracts separately and identifies empty-array execution-only cases. Its baseline partition contains the retained 345 comparisons.

The supplementary harness crosses 21 independently selected fixtures, five methods and six dtype representations. Its additional 90 missing/empty probe outputs are recorded separately from the 630 comparison rows; they are not 90 additional Unicode successes or a fully asserted missing-contract suite.

Original execution: Python 3.12.14, Windows, pandas 3.0.0/3.1.0, NumPy 2.5.4, PyArrow 23.0.1. Supplementary execution: Python 3.12.13, Linux, the same pandas/NumPy/PyArrow versions. Full environment strings remain in the JSON.

## Dtypes and methods

Both suites cover contains, match, fullmatch, replace and count. The original suite tests object, nullable string and str with explicit Arrow storage. The supplementary suite additionally distinguishes string[python], ArrowDtype(pa.string()) and ArrowDtype(pa.large_string()). Recorded array classes and storage make backend selection observable.

## Reproduce without overwriting saved records

Use Python 3.12. The examples below use Windows PowerShell; on Linux use the environment's bin/python executable.

```powershell
py -3.12 -m venv .venv-300
.\.venv-300\Scripts\python -m pip install -r requirements.txt pandas==3.0.0
.\.venv-300\Scripts\python -X utf8 tests/pandas_unicode_regression_tests.py --output fresh_300.json
.\.venv-300\Scripts\python -X utf8 tests/independent_review_harness.py fresh_reviewer_300.json

py -3.12 -m venv .venv-310
.\.venv-310\Scripts\python -m pip install -r requirements.txt pandas==3.1.0
.\.venv-310\Scripts\python -X utf8 tests/pandas_unicode_regression_tests.py --output fresh_310.json
.\.venv-310\Scripts\python -X utf8 tests/independent_review_harness.py fresh_reviewer_310.json
```

The original script exits 1 when it records a mismatch or exception; this is expected for these limitation probes. The supplementary harness prints counts and writes JSON; inspect its statuses rather than relying on process exit alone. The UTF-8 switch makes non-Latin output portable. Matching the exact Python patch release and platform provides the closest replication of each saved experiment.

## Known limitations

- Python and RE2 disagree on vertical tab and U+001C–U+001F in ASCII whitespace shorthand and its complement. All-ASCII arrays can remain on Arrow; mixed arrays may trigger Python fallback.
- RE2 rejects Python's backspace-class spelling r"[\b]". The detector sees a literal backspace rather than a boundary assertion.
- ArrowExtensionArray paths retain discrepancies outside this StringDtype correction.
- Backend-specific syntax, flags, normalization and batch composition require separate testing. These fixtures do not certify all regex syntax or every Unicode code point.
- No performance benchmark is supplied. Count improvements are not speed measurements and cannot all be attributed to one PR across an entire release.

## Record integrity and privacy

The author retains the original full execution files privately. The public original-suite JSON copies replace absolute local execution paths with <LOCAL_PATH>, including paths inside tracebacks. Test inputs, expected/actual values, result dtypes, storage, statuses, exception messages, counts, versions and timestamps are unchanged. Supplementary JSON files are byte-for-byte copies because they contain no personal execution paths. See results/PROVENANCE.json for original/public SHA-256 hashes and redaction counts. Do not describe the public path-redacted copies as byte-identical originals.

## License and upstream software

The reproduction code is offered under the MIT License. pandas, PyArrow, RE2 and Python retain their respective upstream licenses. This repository contains focused reproduction scripts, not a copy of the pandas project or its full test suite.

## Separate edge-case follow-up

A separate 30-row follow-up tests backspace spelling `r"\x08"` and mixed RE2-property/shorthand syntax `r"\p{L}\w"` on three dtype representations and all five methods. It used Python 3.12.14, pandas 3.1.0, NumPy 2.5.4 and PyArrow 23.0.1. These checks are not included in the saved 600-row or 630-row totals. See tests/edge_case_checks.py and results/edge_case_checks_310.json. The mixed pattern is not Python-valid, so it has no Python-re result oracle; the file records its observed backend behavior.
