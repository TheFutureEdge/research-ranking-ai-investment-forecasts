"""Rescoring arithmetic extracted unchanged from the frozen author experiment."""

from math import tanh

def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)))
    return t*t*(3-2*t)

def g10(r,mad,std):
    excess=r-3.6
    adjusted=(1 if excess>=0 else -1)*(abs(excess)-min(.35*mad,.6*abs(excess)))
    band=max(1,min(10,.5*abs(r)))
    penalty=.15*min(1,(max(0,std-band)/max(15-band,1))**2)
    return 1000*tanh(adjusted/30)*(1-penalty)

def shock_weight(config,shock,threshold,horizon):
    if config['kind']=='legacy':
        cap=.5 if horizon=='1y' else .2
        start,full,direction=12,25,'both'
    elif config['kind']=='shock':
        cap,start,full,direction=(config[k] for k in ('cap','absolute_start','absolute_full','direction'))
    else:return 0.
    if direction=='down' and shock>=0:return 0.
    if direction=='up' and shock<=0:return 0.
    if abs(shock)<start:return 0.
    return cap*max(smooth(.75,1.5,abs(shock)/threshold),smooth(start,full,abs(shock)))

def score(config,item):
    if config['kind']=='original':return item['original_g10']
    if config['kind']=='b02':return 1000*tanh(((item['raw_return']-3.6)/max(item['vol'],5))/2)
    w=shock_weight(config,item['shock_pct'],item['threshold_pct'],item['horizon'])
    r=3.6+(1-w)*(item['raw_return']-3.6)
    if config['kind']!='legacy':return g10(r,item['mad'],item['std'])
    excess=r-3.6
    adjusted=(1 if excess>=0 else -1)*(abs(excess)-min(.35*item['mad'],.6*abs(excess)))
    vol=max(item['vol'],5)
    anchor=1+min(1,max(0,(vol-30)/50))
    signal=.35*adjusted/vol+.65*adjusted/(15*anchor)
    band=max(1,min(10,.5*abs(r)))
    penalty=.15*min(1,(max(0,item['std']-band)/max(15-band,1))**2)
    return 1000*tanh(signal/2)*(.85+.15*item['consistency'])*(1-penalty)

def extended_score(config,item):
    if config['kind']=='score_shock':
        trigger=dict(config,kind='shock')
        w=shock_weight(trigger,item['shock_pct'],item['threshold_pct'],item['horizon'])
        return score({'kind':'raw'},item)*(1-w)
    if config['kind']=='continuity':
        w=config['original_weight']
        return w*item['original_g10']+(1-w)*score({'kind':'raw'},item)
    return score(config,item)
