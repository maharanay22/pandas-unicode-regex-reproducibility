# Regression comparison results

The original and supplementary datasets use different fixtures, dtypes, Python patch versions and platforms. They are reported separately.

| Dataset file | Rows | Status counts |
|---|---:|---|
| pandas_300_results.json | 600 | {'PASS': 304, 'FAIL': 226, 'ERROR': 70} |
| pandas_310_results.json | 600 | {'PASS': 570, 'FAIL': 20, 'ERROR': 10} |
| reviewer_300_results.json | 630 | {'PASS': 348, 'MISMATCH': 232, 'EXCEPTION': 50} |
| reviewer_310_results.json | 630 | {'PASS': 462, 'EXCEPTION': 40, 'MISMATCH': 128} |

## Supplementary results by dtype

| dtype | 3.0.0 PASS | 3.0.0 MISMATCH | 3.0.0 EXCEPTION | 3.1.0 PASS | 3.1.0 MISMATCH | 3.1.0 EXCEPTION |
|---|---:|---:|---:|---:|---:|---:|
| object | 105 | 0 | 0 | 105 | 0 | 0 |
| string[pyarrow] | 37 | 58 | 10 | 94 | 6 | 5 |
| str(pyarrow) | 37 | 58 | 10 | 94 | 6 | 5 |
| string[python] | 105 | 0 | 0 | 105 | 0 | 0 |
| ArrowDtype(string) | 32 | 58 | 15 | 32 | 58 | 15 |
| ArrowDtype(large_string) | 32 | 58 | 15 | 32 | 58 | 15 |

## Interpretation

The original 3.1.0 remainder consists of 20 whitespace mismatch rows and 10 backspace-class exception rows on the two Arrow-backed StringDtype representations. The supplementary experiment also includes ArrowDtype, whose ArrowExtensionArray implementation remains outside the corrected StringDtype fallback. See every row in the corresponding JSON; exceptions have not been discarded or counted as passes.

The original missing-value assertions are distinct from regex comparisons. Supplementary missing/empty outputs are observational probes with no complete assertion oracle. Neither is an independent statistical sample.

## Reproduction commands

Exact portable commands and pinned dependencies are in the README and requirements.txt. Original absolute execution paths are intentionally withheld from public records. Run each script into a new output file and compare fixture/dtype/method statuses with the saved dataset of the same methodology.

## Integrity

Original/public hashes and metadata redaction counts are in results/PROVENANCE.json. The saved numerical results are not benchmark measurements. No claim is made that these experiments reran the complete pandas upstream test suite.
