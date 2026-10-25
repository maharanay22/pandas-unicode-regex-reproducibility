# Test environment details

| Dataset | Python | pandas | NumPy | PyArrow | Platform |
|---|---|---|---|---|---|
| pandas_300_results.json | 3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)] | 3.0.0 | 2.5.4 | 23.0.1 | Windows-11-10.0.26200-SP0 |
| pandas_310_results.json | 3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)] | 3.1.0 | 2.5.4 | 23.0.1 | Windows-11-10.0.26200-SP0 |
| reviewer_300_results.json | 3.12.13 | 3.0.0 | 2.5.4 | 23.0.1 | Linux-6.18.44-fc-v153-x86_64-with-glibc2.39 |
| reviewer_310_results.json | 3.12.13 | 3.1.0 | 2.5.4 | 23.0.1 | Linux-6.18.44-fc-v153-x86_64-with-glibc2.39 |

The dependency file pins shared numerical and Arrow packages. Select pandas 3.0.0 or 3.1.0 explicitly using the README commands. Original input arrays and backend selections are retained in the original dataset; the supplementary harness constructs each dtype explicitly and records its array class. Absolute local paths were removed only from the public metadata copies.
