"""Frozen score definitions; no outcome data enters this module.

The original40 definitions are copied unchanged from
../2026-11-03_expanded_scoring_study/scoring.py, SHA256 recorded by freeze.py.
The eight additional mechanisms implement DECISION_PROTOCOL.md literally.
"""
from collections import defaultdict
from itertools import product
from math import isfinite,tanh

FACTORS=('V','M','A','D','H')
def configurations():
    result=[]
    for i,bits in enumerate(product((False,True),repeat=5)):
        flags=dict(zip(FACTORS,bits))
        result.append({'id':f'G{i:02d}','kind':'grid',**flags,
            'label':' '.join(k+('1' if v else '0') for k,v in flags.items())})
    refs=[('B01','Return only'),('B02','Pure forecast Sharpe'),('B03','Stored current core'),
          ('B04','Return minus MAD'),('B05','Return minus forecast std'),
          ('B06','Directional vote agreement'),('B07','Horizon conflict penalty'),
          ('B08','Percentile composite')]
    result.extend({'id':i,'kind':'reference','label':name} for i,name in refs)
    additions=[
        {'id':'L10','label':'Light Sharpe alpha0.10; no high-vol anchor','alpha':.10,'anchor_max':1.0,'consistency':False},
        {'id':'L20','label':'Light Sharpe alpha0.20; no high-vol anchor','alpha':.20,'anchor_max':1.0,'consistency':False},
        {'id':'L10C','label':'Light Sharpe alpha0.10 plus consistency','alpha':.10,'anchor_max':1.0,'consistency':True},
        {'id':'L10A','label':'Light Sharpe alpha0.10 plus soft1.25 anchor','alpha':.10,'anchor_max':1.25,'consistency':False},
        {'id':'A00','label':'No Sharpe; soft1.25 volatility anchor','alpha':0.0,'anchor_max':1.25,'consistency':False},
        {'id':'L35','label':'Sharpe alpha0.35; no high-vol anchor','alpha':.35,'anchor_max':1.0,'consistency':False},
        {'id':'E25','label':'Positive G10score with quarter-power volatility haircut','mechanism':'soft_exposure_haircut','volatility_floor':20.0,'exponent':.25},
        {'id':'HNEG','label':'G10score; negative original5Ycore gate capped10%','mechanism':'negative_five_year_gate','max_haircut':.10},
    ]
    result.extend(dict(kind='mechanism',**c) for c in additions)
    return result

def numeric(row,field):
    value=float(row[field])
    if not isfinite(value):raise ValueError(f'Nonfinite {field}')
    return value

def unpack(row):
    import json
    extra=json.loads(row['extra_metrics'] or '{}')
    deviation=extra.get('return_stdev_annualized_total_pct',row['return_stdev_pct'])
    vol=row['hist_volatility_annualized_10y_pct']
    item={'r':numeric(row,'annual_mean_return_pct_incl_divds'),
        'mad':numeric(row,'annual_return_mad_pct_incl_divds'),
        'vol':float(vol) if vol is not None else 5.0,'vol_floor_fallback':vol is None,
        'consistency':numeric(row,'direction_consistency'),
        'agreement':numeric(row,'dir_agree'),'deviation':float(deviation),
        'stored':numeric(row,'consensus_score_incl_divds')}
    if not all(isfinite(v) for v in item.values()):raise ValueError('Nonfinite source input')
    if not 0<=item['consistency']<=1 or not 0<=item['agreement']<=1:raise ValueError('Invalid agreement scale')
    if min(item['mad'],item['vol'],item['deviation'])<0:raise ValueError('Negative risk input')
    return item

def core(h,c):
    excess=h['r']-3.6
    if c['M']:
        discount=min(.35*h['mad'],.60*abs(excess))
        excess=(1 if excess>=0 else -1)*(abs(excess)-discount)
    if c['V']:
        multiplier=1+min(1,max(0,(h['vol']-30)/50))
        signal=.35*excess/max(h['vol'],5)+.65*excess/(15*multiplier)
    else:signal=excess/15
    value=1000*tanh(signal/2)
    if c['A']:value*=.85+.15*h['consistency']
    if c['D']:
        band=max(1,min(10,.5*abs(h['r'])))
        penalty=0 if h['deviation']<=band else min(1,((h['deviation']-band)/max(15-band,1))**2)*.15
        value*=1-penalty
    return value

def percentiles(values):
    indexed=defaultdict(list)
    for key,value in values.items():indexed[value].append(key)
    total=len(values);used=0;result={}
    for value in sorted(indexed):
        keys=indexed[value]
        average_index=used+(len(keys)-1)/2
        pct=100*average_index/max(1,total-1)
        result.update({k:pct for k in keys});used+=len(keys)
    return result

def mechanism_score(one,five,configuration):
    """The eight preregistered mechanisms, each based on G10's MAD/dispersion."""
    base_flags={'V':False,'M':True,'A':False,'D':True,'H':False}
    identity=configuration['id']
    if identity=='E25':
        base=core(one,base_flags)
        return base/(max(one['vol'],20)/20)**.25 if base>0 else base
    if identity=='HNEG':
        base=core(one,base_flags)
        # Literal protocol: multiply signed G10score; no positive5Y uplift.
        factor=1-.10*max(0,min(1,-five['stored']/1000))
        return base*factor
    excess=one['r']-3.6
    discount=min(.35*one['mad'],.60*abs(excess))
    excess=(1 if excess>=0 else -1)*(abs(excess)-discount)
    alpha=configuration['alpha']
    anchor=1+(configuration['anchor_max']-1)*max(0,min(1,(one['vol']-30)/50))
    signal=alpha*excess/max(one['vol'],5)+(1-alpha)*excess/(15*anchor)
    score=1000*tanh(signal/2)
    if configuration['consistency']:
        score*=.85+.15*one['consistency']
    band=max(1,min(10,.5*abs(one['r'])))
    penalty=0 if one['deviation']<=band else min(1,((one['deviation']-band)/max(15-band,1))**2)*.15
    return score*(1-penalty)

def scores_for_batch(pairs):
    output={c['id']:{} for c in configurations()}
    percentile_fields={name:{} for name in ('return','sharpe','negative_mad','agreement','five')}
    for subject,(one,five) in pairs.items():
        for c in configurations():
            if c['kind']=='grid':
                a=core(one,c)
                output[c['id']][subject]=.8*a+.2*core(five,c) if c['H'] else a
            elif c['kind']=='mechanism':
                output[c['id']][subject]=mechanism_score(one,five,c)
        sharpe=(one['r']-3.6)/max(one['vol'],5)
        refs={'B01':one['r'],'B02':sharpe,'B03':one['stored'],
            'B04':one['r']-one['mad'],'B05':one['r']-one['deviation'],
            'B06':(one['r']-3.6)*(.5+.5*one['agreement']),
            'B07':one['stored']-.25*abs(one['stored']-five['stored'])}
        for k,value in refs.items():output[k][subject]=value
        for k,value in {'return':one['r'],'sharpe':sharpe,'negative_mad':-one['mad'],
                        'agreement':one['agreement'],'five':five['stored']}.items():
            percentile_fields[k][subject]=value
    p={k:percentiles(v) for k,v in percentile_fields.items()}
    for subject in pairs:
        output['B08'][subject]=sum(weight*p[k][subject] for k,weight in (
            ('return',.45),('sharpe',.20),('negative_mad',.15),('agreement',.10),('five',.10)))
    return output

def weights(n,method):
    if method=='equal':return [1/n]*n
    if method=='linear':return [2*(n-i)/(n*(n+1)) for i in range(n)]
    raise ValueError(method)

def explicit_primary_historical_volatility(configuration):
    """Eligible explicit1Y volatility treatments for the balancing comparison.

    HNEG uses a stored5Y core for a direction gate, not an explicit1Y
    volatility adjustment. This helper does not misclassify it as one.
    """
    if configuration['kind']=='grid':return configuration['V']
    return configuration['id'] in {'B02','B03','B07','B08','L10','L20','L10C','L10A','A00','L35','E25'}
