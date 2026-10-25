"""Independent reviewer harness: pandas Arrow-string regex vs Python re oracle.
Not the author's script (not supplied). Fixtures chosen by the reviewer.
Usage: python harness.py out.json
"""
import json, re, sys, platform, traceback
import numpy as np, pandas as pd, pyarrow as pa

ASCII_CTRL = ["a\vb", "a\x1cb", "a\x1fb", "plain ascii"]
FIXTURES = [
    # (id, pattern, values, replacement)
    ("article_example", r"[^\w\s]", ["café crème!", "Müller-Lüdenscheidt", "東京 2024"], ""),
    ("w_plus", r"\w+", ["café", "naïve", "Ωμέγα", "Москва", "abc"], "X"),
    ("W", r"\W", ["café!", "東京", "a-b"], "_"),
    ("d_arabic", r"\d+", ["٣٤٥", "१२३", "abc123"], "#"),
    ("D", r"\D", ["٣a", "12"], "_"),
    ("s_unicode", r"\s", ["a b", "a　b", "a b"], "_"),
    ("S_unicode", r"\S+", ["a b", "x y"], "Z"),
    ("b_japanese", r"\b東", ["東京", "x東", " 東"], "!"),
    ("B", r"\Bé", ["café", "é"], "E"),
    ("nested_alt", r"(?:x|(\w))+", ["éé", "xx"], "-"),
    ("lookahead_in_repeat", r"(?:a(?=é))+", ["aé", "ab"], "-"),
    ("backref", r"(\w)\1", ["éé", "aa", "ab"], "-"),
    ("escaped_literal_w", r"\\w", ["\\w é", "w"], "-"),
    ("backspace_class", r"[\b]", ["a\bb", "ab"], "-"),
    ("ctrl_s_ascii_only", r"\s", ASCII_CTRL, "_"),
    ("ctrl_S_ascii_only", r"\S+", ASCII_CTRL, "_"),
    ("ctrl_s_mixed", r"\s", ASCII_CTRL + ["é"], "_"),
    ("decomposed", r"^\w+$", ["café", "café"], "-"),
    ("zero_width_b_replace", r"\b", ["ab cd", "é x"], "|"),
    ("ascii_only_w", r"\w+", ["abc", "a_b", "x y"], "-"),
    ("case_insens_inline", r"(?i)é", ["É", "é"], "-"),
]
METHODS = ["contains", "match", "fullmatch", "count", "replace"]


def dtypes():
    return {
        "object": object,
        "string[pyarrow]": pd.StringDtype("pyarrow"),
        "str(pyarrow)": pd.StringDtype("pyarrow", na_value=np.nan),
        "string[python]": pd.StringDtype("python"),
        "ArrowDtype(string)": pd.ArrowDtype(pa.string()),
        "ArrowDtype(large_string)": pd.ArrowDtype(pa.large_string()),
    }


def oracle(method, pat, v, repl):
    if method == "contains": return re.search(pat, v) is not None
    if method == "match": return re.match(pat, v) is not None
    if method == "fullmatch": return re.fullmatch(pat, v) is not None
    if method == "count": return len(re.findall(pat, v))
    if method == "replace": return re.sub(pat, repl, v)


def call(s, method, pat, repl):
    a = s.str
    if method == "replace": return a.replace(pat, repl, regex=True)
    return getattr(a, method)(pat)


def norm(x):
    if x is None or x is pd.NA: return "<NA>"
    if isinstance(x, float) and np.isnan(x): return "<NaN>"
    if isinstance(x, (np.bool_,)): return bool(x)
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.floating,)): return float(x)
    return x


def run():
    rows = []
    for dname, dt in dtypes().items():
        for fid, pat, vals, repl in FIXTURES:
            s = pd.Series(vals, dtype=dt)
            for m in METHODS:
                row = dict(fixture=fid, dtype=dname, method=m, pattern=pat,
                           series_dtype=str(s.dtype),
                           storage=getattr(s.dtype, "storage", None),
                           array_cls=type(s.array).__name__)
                exp = [oracle(m, pat, v, repl) for v in vals]
                try:
                    out = call(s, m, pat, repl)
                    got = [norm(x) for x in out.tolist()]
                    row["result_dtype"] = str(out.dtype)
                    row["got"] = got; row["expected"] = exp
                    row["status"] = "PASS" if got == exp else "MISMATCH"
                except Exception as e:
                    row["status"] = "EXCEPTION"; row["error"] = f"{type(e).__name__}: {str(e)[:160]}"
                    row["expected"] = exp
                rows.append(row)
    # missing / empty contracts
    miss = []
    for dname, dt in dtypes().items():
        for label, vals in [("with_null", ["café", None]), ("all_null", [None, None]), ("empty", [])]:
            s = pd.Series(vals, dtype=dt)
            for m in METHODS:
                r = dict(dtype=dname, case=label, method=m)
                try:
                    out = call(s, m, r"\w+", "X")
                    r["got"] = [norm(x) if not isinstance(x, str) else x for x in out.tolist()]
                    r["result_dtype"] = str(out.dtype); r["len"] = len(out)
                except Exception as e:
                    r["error"] = f"{type(e).__name__}: {str(e)[:160]}"
                miss.append(r)
    env = dict(python=platform.python_version(), pandas=pd.__version__, pyarrow=pa.__version__,
               numpy=np.__version__, platform=platform.platform(),
               default_string_storage=pd.get_option("mode.string_storage"),
               infer_string=str(pd.Series(["a"]).dtype))
    return dict(env=env, rows=rows, missing=miss)


if __name__ == "__main__":
    res = run()
    json.dump(res, open(sys.argv[1], "w"), ensure_ascii=False, indent=1, default=str)
    from collections import Counter
    print(res["env"])
    print(Counter((r["dtype"], r["status"]) for r in res["rows"]))
