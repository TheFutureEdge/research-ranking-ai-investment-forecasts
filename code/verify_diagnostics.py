from pathlib import Path
import csv,json
from statistics import mean,median
R=Path(__file__).resolve().parents[1]
def read(name):
 with (R/'data'/name).open() as f:return list(csv.DictReader(f))
m=json.loads((R/'data/additional_metrics.json').read_text())
r=read('rescoring_retained_cells.csv')
for expected in m['cell_robustness']:
 batches=[3,4,5] if expected['cells']==18 else list(range(1,7))
 vals={}
 for c in ['RAW_G10','MIX_ORIG75']:
  sample=sorted([x for x in r if x['configuration']==c and x['horizon']=='1y' and int(x['batch']) in batches],key=lambda x:(int(x['batch']),int(x['lag']),int(x['n'])))
  vals[c]=sample
  key='raw' if c=='RAW_G10' else 'blend'
  assert len(sample)==expected['cells']
  assert abs(median(float(x['return_pct']) for x in sample)-expected[key+'_median_pct'])<1e-10
  assert abs(mean(float(x['mrna_cash_return_pct']) for x in sample)-expected['mrna_cash_'+key+'_mean_pct'])<1e-10
 assert sum(float(b['mrna_cash_return_pct'])>float(a['mrna_cash_return_pct'])+1e-8 for a,b in zip(vals['RAW_G10'],vals['MIX_ORIG75']))==expected['mrna_cash_wins']
for row in read('turnover_cells.csv'):
 assert abs(sum(float(v) for k,v in row.items() if k.startswith('contribution_'))-float(row['delta_pp']))<1e-8
print('PASS: medians, issuer-cash controls, paired cell wins and all 36 attribution identities')
