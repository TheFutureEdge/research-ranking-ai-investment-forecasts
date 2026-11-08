"""Network-free verification of the published frozen scoring experiments."""
from pathlib import Path
from collections import defaultdict
from statistics import mean
import csv,gzip,json,math,time
from original_scoring import scores_for_batch
from rescoring import g10,extended_score
R=Path(__file__).resolve().parents[1]
def load(name):
 p=R/'data'/name
 with gzip.open(p,'rt') if p.suffix=='.gz' else p.open() as f:return json.load(f)
def assert_close(a,b,tol=1e-7):assert abs(a-b)<tol,(a,b)
def main():
 start=time.time();orig=load('original_design.json');inp=load('original_forecast_features.json.gz');expected=load('original_rankings.json.gz');groups=defaultdict(dict)
 for r in inp:groups[r['batch']][r['subject_id']]=(r['one'],r['five'])
 orders=0
 for batch,features in groups.items():
  scores=scores_for_batch(features)
  for cid,mapping in scores.items():
   ranked=sorted(mapping,key=lambda sid:(-mapping[sid],sid));saved=expected[f'{batch}_{cid}']
   assert set(ranked)=={r['subject_id'] for r in saved}
   assert ranked[:30]==[r['subject_id'] for r in saved[:30]]
   # Runtime summation can permute B08 tail ties at about 1e-14, below every tested selection.
   assert all(mapping[a['subject_id']]>=mapping[b['subject_id']]-1e-10 for a,b in zip(saved,saved[1:]))
   for row in saved:assert_close(mapping[row['subject_id']],row['score'])
   orders+=1
 assert orders==288
 rc=load('rescoring_design.json');rin=load('rescoring_forecast_features.json.gz');rr=load('rescoring_rankings.json.gz');expected_r={(x['batch'],x['horizon'],x['lag'],x['configuration']):x for x in rr};rg=defaultdict(list)
 for x in rin:rg[x['batch'],x['horizon'],x['lag']].append(x)
 selections=0
 for (batch,horizon,lag),features in rg.items():
  eligible=[r for r in features if r['raw_return']>=3.6 and r['raw_return']-r['mad']>=-1 and g10(r['raw_return'],r['mad'],r['std'])>130]
  for c in rc['configurations']:
   scored={r['subject_id']:extended_score(c,r) for r in eligible}
   selected=sorted((sid for sid,value in scored.items() if c['kind']=='b02' or value>130),key=lambda sid:(-scored[sid],sid))[:20]
   saved=expected_r[batch,horizon,lag,c['id']]['top20'];assert selected==[x['subject_id'] for x in saved]
   for x in saved:assert_close(scored[x['subject_id']],x['score'])
   selections+=1
 assert selections==4140
 totals={};rows={}
 for prefix in ['original','rescoring']:
  vals=load(prefix+'_portfolio_results.json.gz');lookup={((r['mode']+'|') if prefix=='original' else '')+r['portfolio_id']:r for r in vals};assert len(lookup)==len(vals)
  for r in vals:
   w=sum(r[k] for k in ['stock_usd','cash_usd','receivable_usd','unresolved_usd']);assert_close(w,r['wealth_usd']);assert_close(100*(w/100000-1),r['return_pct'])
  state={};observations=0
  with gzip.open(R/'data'/f'{prefix}_portfolio_daily.csv.gz','rt') as f:
   for r in csv.DictReader(f):
    key=((r['mode']+'|') if prefix=='original' else '')+r['portfolio_id'];peak,dd,last,lastday=state.get(key,(100000.,0.,100000.,''));w=float(r['wealth_usd']);assert r['date']>=lastday;peak=max(peak,w);dd=min(dd,100*(w/peak-1));state[key]=(peak,dd,w,r['date']);observations+=1
  assert set(state)==set(lookup)
  for key,r in lookup.items():assert_close(state[key][1],r['max_drawdown_pct']);assert_close(state[key][2],r['wealth_usd'])
  totals[prefix]={'portfolios':len(vals),'daily_rows':observations};rows[prefix]=vals
 assert totals['original']['portfolios']==3456 and totals['rescoring']['portfolios']==8280
 assert sum(x['daily_rows'] for x in totals.values())==2135172
 for scope,batches in [('primary',[3,4,5]),('all',list(range(1,7)))]:
  selected=[r for r in rows['rescoring'] if r['batch'] in batches and r['horizon']=='1y' and r['configuration'] in ['RAW_G10','MIX_ORIG75']]
  pairs=defaultdict(dict)
  for r in selected:pairs[r['batch'],r['lag'],r['n']][r['configuration']]=r
  wins=sum(r['MIX_ORIG75']['return_pct']>r['RAW_G10']['return_pct']+1e-8 for r in pairs.values());assert wins== (15 if scope=='primary' else 25)
 print(json.dumps({'pass':True,'original_formula_orders':orders,'rescoring_policy_groups':selections,'portfolio_and_daily_checks':totals,'elapsed_seconds':round(time.time()-start,2)},indent=2))
if __name__=='__main__':main()
