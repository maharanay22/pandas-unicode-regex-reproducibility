"""Separate verification of two article edge-case claims; not part of saved suites."""
from pathlib import Path
import json,re,sys,platform
import pandas as pd
import pyarrow as pa
types={'str(pyarrow)':pd.StringDtype('pyarrow',na_value=float('nan')),
       'string[pyarrow]':pd.StringDtype('pyarrow'),
       'ArrowDtype(string)':pd.ArrowDtype(pa.string())}
rows=[]
for name,dtype in types.items():
    for pattern,values in [(r'\x08',['a\bb','ab']), (r'\p{L}\w',['éé','aa'])]:
        for method in ['contains','match','fullmatch','replace','count']:
            row={'dtype':name,'pattern':pattern,'input':values,'method':method}
            try:
                if pattern==r'\x08':
                    fn=re.search if method=='contains' else getattr(re,method,None)
                    expected=[re.sub(pattern,'-',v) if method=='replace' else len(re.findall(pattern,v)) if method=='count' else fn(pattern,v) is not None for v in values]
                    row['expected_python']=expected
                s=pd.Series(values,dtype=dtype)
                result=s.str.replace(pattern,'-',regex=True) if method=='replace' else getattr(s.str,method)(pattern)
                row['actual']=result.tolist()
                if 'expected_python' in row:row['agrees_with_python']=row['actual']==row['expected_python']
            except Exception as exc:row['error']=repr(exc)
            rows.append(row)
out={'methodology':'Targeted edge-case verification, separate from the saved 600-row and 630-row datasets.',
     'python':platform.python_version(),'pandas':pd.__version__,'numpy':__import__('numpy').__version__,
     'pyarrow':pa.__version__,'rows':rows}
Path(sys.argv[1]).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True))
