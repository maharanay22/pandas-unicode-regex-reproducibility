"""Python 3.12 pandas/RE2 semantic probes, expanded from the retained smoke test.

Run: python pandas_unicode_regression_tests.py --output pandas_310_results.json
Exit 0: all rows agree; 1: at least one measured mismatch/exception; 2: setup error.
Each row is one fixture x dtype x method, not one individual string assertion.
Missing values use pandas' dtype contract, since re has no missing-value contract.
This script is standalone, performs no network access and makes no timing claims.
"""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import platform
import re
import sys
import traceback
import warnings
from pathlib import Path

BASELINE_CASES = [
    ('latin', ['café', 'naïve', 'Müller', 'abc'], r'\w+'),
    ('scripts', ['東京', 'Ελλάδα', 'Москва', 'مرحبا', 'abc'], r'\w+'),
    ('digits', ['١٢٣', '１２３', '123', 'abc'], r'\d+'),
    ('space_unicode', ['\u00a0', '\u2003', ' ', 'x'], r'\s+'),
    ('space_ascii_limit', ['\v', '\x1c', '\x1d', '\x1e', '\x1f', ' '], r'\s'),
    ('space_mixed_array', ['\v', '\x1c', '\u00a0', ' '], r'\s'),
    ('boundaries', ['café', '東京', 'é', 'abc'], r'\b\w+\b'),
    ('boundary_only', ['café', '東京', 'é', 'abc'], r'\b'),
    ('boundary_japanese', ['東京', 'café'], r'\b東'),
    ('negated_class', ['café crème!', 'Müller-Lüdenscheidt', '東京 2024'], r'[^\w\s]'),
    ('negated_word', ['café!', '東京!', 'abc!'], r'\W+'),
    ('negated_digit', ['١٢٣', '１２３', 'abc'], r'\D+'),
    ('negated_space', ['\u00a0', '\u2003', 'abc'], r'\S+'),
    ('nonboundary', ['café', '東京', 'abc'], r'\B'),
    ('nested', ['café', '東京', '١٢٣', 'abc'], r'(?:(?:\w+)|(?:\d{2,}))+'),
    ('repeated_lookaround', ['ab', 'aa', 'café'], r'(?:a(?=b))+'),
    ('repeated_backref', ['aa', 'aaaa', '東京'], r'(?:(a)\1)+'),
    ('literal_escape', [r'\w', 'café', 'abc'], r'\\w'),
    ('ascii_control', ['abc', '123', 'a b', ''], r'\w+'),
    ('normalization', ['é', 'e\u0301', '東京'], r'\w+'),
    ('empty', [], r'\w+'),
    ('nulls', [None, None], r'\w+'),
    ('mixed_nulls', ['café', None, '東京'], r'\w+'),
]
ADDED_CASES = [
    ('word_class', ['café-東京', 'Müller', 'abc-1'], r'[\w-]+'),
    ('alternation', ['X', '١٢٣', '１２', 'café'], r'(?:X|\d+)'),
    ('lazy_repeat', ['café', '東京', 'abc'], r'(?:\w+?)+'),
    ('possessive_repeat', ['café', '東京', 'abc'], r'\w++'),
    ('atomic_group', ['café', '東京', 'abc'], r'(?>\w+)'),
    ('repeated_negative_lookahead', ['ac', 'ab', 'café'], r'(?:a(?!b))+'),
    ('repeated_lookbehind', ['ab', 'bb', 'café'], r'(?:(?<=a)b)+'),
    ('ascii_space_complement', ['\v', '\x1c', '\x1d', '\x1e', '\x1f', ' '], r'\S'),
    ('emoji', ['🧪', 'café🧪', '東京_', 'abc'], r'\w+'),
    ('combining_strip', ['é', 'e\u0301', '東京'], r'[^\w]'),
    ('literal_unicode', ['é', '東京', 'café', 'abc'], r'é|東'),
    ('escaped_class_literals', [r'\w', r'\d', r'\s', r'\b', 'é'], r'\\[wdsb]'),
    ('backspace_class', ['\b', 'b', 'é'], r'[\b]'),
    ('all_null_empty_pattern', [None, None], r''),
    ('mixed_empty', ['', None, 'café'], r'\w*'),
    ('decimal_categories', ['١', '²', 'Ⅻ', '1', ''], r'\d'),
    ('word_categories', ['²', 'Ⅻ', '١', '_', ''], r'\w'),
]
METHODS = ['contains', 'match', 'fullmatch', 'replace', 'count']
DTYPES = ['object', 'string', 'str']

def oracle(value, method, pattern):
    if value is None:
        return None
    if method == 'replace':
        return re.sub(pattern, '', value)
    if method == 'count':
        return len(re.findall(pattern, value))
    fn = re.search if method == 'contains' else getattr(re, method)
    return fn(pattern, value) is not None

def counts(rows):
    return {status:sum(row['status']==status for row in rows)
            for status in ['PASS','FAIL','ERROR']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    out=Path(args.output)
    report={'schema_version':2,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'argv':sys.argv,'python':sys.version,'executable':sys.executable,
            'platform':platform.platform(),'machine':platform.machine(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'suite':{'baseline_fixtures':len(BASELINE_CASES),'added_fixtures':len(ADDED_CASES),
                     'methods':METHODS,'dtypes':DTYPES,'expected_rows':(len(BASELINE_CASES)+len(ADDED_CASES))*len(METHODS)*len(DTYPES)},
            'rows':[]}
    try:
        if sys.version_info[:2]!=(3,12):
            raise RuntimeError('This verification run requires Python 3.12')
        import pandas as pd
        import pyarrow as pa
        report.update(pandas=pd.__version__,pyarrow=pa.__version__,
                      numpy=importlib.metadata.version('numpy'),
                      packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions()})
    except Exception as exc:
        report.update(setup_error=repr(exc),traceback=traceback.format_exc())
        out.write_text(json.dumps(report,indent=2),encoding='utf-8')
        return 2

    def normal(value):
        if pd.isna(value): return None
        return value.item() if hasattr(value,'item') else value

    with pd.option_context('mode.string_storage','pyarrow'):
        for dtype in DTYPES:
            for partition,cases in [('baseline',BASELINE_CASES),('added',ADDED_CASES)]:
                for case,values,pattern in cases:
                    for method in METHODS:
                        row={'id':f'{case}/{dtype}/{method}','partition':partition,
                             'case':case,'dtype':dtype,'method':method,'pattern':pattern,
                             'input':values,'expected':[oracle(v,method,pattern) for v in values],
                             'checks':[],'replacement':'' if method=='replace' else None}
                        try:
                            series=pd.Series(values,dtype=dtype)
                            row.update(actual_dtype=str(series.dtype),
                                       storage=getattr(series.dtype,'storage',None) or 'python-object',
                                       array_type=type(series.array).__module__+'.'+type(series.array).__name__)
                            if dtype!='object' and getattr(series.dtype,'storage',None)!='pyarrow':
                                raise RuntimeError('Expected pyarrow storage was not selected')
                            if hasattr(series.array,'_needs_python_regex'):
                                row['fallback_predicate']=bool(series.array._needs_python_regex(pattern))
                                row['fallback_predicate_note']='Source predicate prediction, not an execution trace; other fallback conditions may apply.'
                            positional=[pattern,''] if method=='replace' else [pattern]
                            kwargs={'regex':True} if method=='replace' else {}
                            with warnings.catch_warnings(record=True) as caught:
                                warnings.simplefilter('always')
                                result=getattr(series.str,method)(*positional,**kwargs)
                            raw=result.tolist()
                            row.update(actual=[normal(v) for v in raw],
                                       actual_raw=[{'repr':repr(v),'type':type(v).__module__+'.'+type(v).__name__} for v in raw],
                                       result_dtype=str(result.dtype),
                                       warnings=[{'category':w.category.__name__,'message':str(w.message)} for w in caught])
                            if len(raw)!=len(values):
                                raise AssertionError('Result length differs from input length')
                            for i,(value,actual,expected) in enumerate(zip(values,raw,row['expected'])):
                                if value is None:
                                    default_false=dtype=='str' and method in ['contains','match','fullmatch']
                                    passed=(normal(actual) is False) if default_false else bool(pd.isna(actual))
                                    row['checks'].append({'index':i,'input':None,'kind':'missing_contract',
                                        'python_re_applicable':False,
                                        'expected_contract':'False' if default_false else 'missing',
                                        'actual':normal(actual),'passed':passed,
                                        'classification':'intentional dtype missing-value handling' if passed else 'missing contract mismatch'})
                                else:
                                    row['checks'].append({'index':i,'input':value,'kind':'python_re',
                                        'expected':expected,'actual':normal(actual),
                                        'passed':normal(actual)==expected})
                            row['status']='PASS' if all(c['passed'] for c in row['checks']) else 'FAIL'
                            row['empty_array_execution_only']=not values
                        except Exception as exc:
                            row.update(status='ERROR',error_type=type(exc).__name__,error=str(exc),
                                       error_repr=repr(exc),traceback=traceback.format_exc())
                        report['rows'].append(row)
    report['summary']=counts(report['rows'])
    report['partition_summary']={p:counts([r for r in report['rows'] if r['partition']==p]) for p in ['baseline','added']}
    checks=[c for r in report['rows'] for c in r['checks']]
    report['value_assertions']={kind:{'passed':sum(c['passed'] for c in checks if c['kind']==kind),
                                    'failed':sum(not c['passed'] for c in checks if c['kind']==kind)}
                                for kind in ['python_re','missing_contract']}
    report['empty_execution_rows']=sum(r.get('empty_array_execution_only',False) for r in report['rows'])
    report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert len(report['rows'])==report['suite']['expected_rows']
    assert len({r['id'] for r in report['rows']})==len(report['rows'])
    out.write_text(json.dumps(report,ensure_ascii=True,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['pandas','pyarrow','summary','partition_summary','value_assertions']}))
    return int(any(r['status']!='PASS' for r in report['rows']))

if __name__=='__main__':
    raise SystemExit(main())
