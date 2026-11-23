"""Educational allocation review. Decimals throughout; no historical strategy backtest."""
from pathlib import Path
from functools import lru_cache
import hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
TICKERS=['VOO','QQQ','SOXX','SCHD','BIL','BND']
BENCH=np.array([.5,0,0,0,.1,.4])
HASH='4db0e28aa81cf8642a5ff756777cf844eb300cffec669e170bbc6e9e8285010a'
AVAILABLE=pd.Timestamp('2026-10-22T21:44:32Z')


def load_prices():
    raw=(ROOT/'data/prices.csv').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=HASH:
        raise ValueError('Frozen price snapshot checksum mismatch. Stop and review provenance.')
    p=pd.read_csv(ROOT/'data/prices.csv',index_col=0,parse_dates=True)
    if list(p.columns)!=TICKERS or not p.index.is_unique or not p.index.is_monotonic_increasing:
        raise ValueError('Invalid price columns or date order.')
    if not np.isfinite(p.values).all() or (p.values<=0).any():
        raise ValueError('Missing, nonfinite, or nonpositive price.')
    if not (np.diff(p.index.to_period('M').astype(int))==1).all():
        raise ValueError('Missing or duplicate month.')
    return p


@lru_cache(None)
def grid():
    def parts(left,n):
        if n==1: yield (left,)
        else:
            for i in range(left+1):
                for rest in parts(left-i,n-1): yield (i,)+rest
    return np.array(list(parts(20,6)),dtype=float)/20


def estimates(window=59, haircut=0.):
    p=load_prices()
    r=p.pct_change(fill_method=None).iloc[1:]
    if window not in (36,48,59): raise ValueError('Window must be 36, 48 or 59 returns.')
    r=r.tail(window)
    mu=r.mean().values*12
    mu[:4]-=haircut
    cov=r.cov().values*12
    return mu,cov


def metrics(weights,mu,cov,current,cost_bps):
    w=np.atleast_2d(weights)
    gross=w@mu
    turnover=np.abs(w-current).sum(axis=1)/2
    # Every asset is a security: both buys and sells are charged.
    cost=np.abs(w-current).sum(axis=1)*cost_bps/10000
    net=(1-cost)*(1+gross)-1
    vol=np.sqrt(np.maximum(np.einsum('ij,jk,ik->i',w,cov,w),0))
    return gross,net,vol,turnover,cost


def review(window=59,cost_bps=10.,target=.06,reserve=.05,vol_limit=.15,
           turnover_limit=.25,haircut=0.,current=None,prior_turnover=0.,drawdown=0.,
           decision_date='2026-11-23',signal=True):
    current=BENCH.copy() if current is None else np.asarray(current,float)
    values=[cost_bps,target,reserve,vol_limit,turnover_limit,haircut,prior_turnover,drawdown]
    if not np.isfinite(values).all() or not (0<=cost_bps<=100 and 0<=reserve<=1 and 0<=vol_limit<=1 and 0<=turnover_limit<=1 and 0<=prior_turnover<=1 and 0<=drawdown<=1):
        raise ValueError('Invalid policy input.')
    if current.shape!=(6,) or not np.isfinite(current).all() or (current<0).any() or not np.isclose(current.sum(),1):
        raise ValueError('Pre-trade weights must be six nonnegative values totaling 100%.')
    asof=pd.Timestamp(decision_date,tz='UTC')
    if asof<=AVAILABLE: raise ValueError('Snapshot was not yet available. No historical backfill allowed.')
    mu,cov=estimates(window,haircut)
    p=load_prices()
    momentum=float(p['VOO'].iloc[-1]/p['VOO'].iloc[-13]-1)
    # Single explicit signal: negative 12-month VOO total-return proxy pauses new risk.
    stopped=drawdown>=.15 or (signal and momentum<=0)
    stale=(asof.tz_localize(None)-p.index[-1]).days>45
    w=grid(); gross,net,vol,turn,cost=metrics(w,mu,cov,current,cost_bps)
    feasible=(net>=target-1e-12)&(w[:,4]>=reserve-1e-12)&(vol<=vol_limit+1e-12)&(turn+prior_turnover<=turnover_limit+1e-12)
    chosen=None
    if feasible.any():
        ix=np.flatnonzero(feasible); chosen=w[ix[np.argmin(vol[ix])]]
    inv=1/np.sqrt(np.diag(cov));inv/=inv.sum()
    portfolios={'Equal weight':np.ones(6)/6,'Inverse volatility':inv,'Benchmark':BENCH}
    if chosen is not None: portfolios['Constrained']=chosen
    rows=[]
    for name,weights in portfolios.items():
        g,n,v,t,c=[float(a[0]) for a in metrics(weights,mu,cov,current,cost_bps)]
        failed=[]
        for label,ok in [('6% net-return target' if target==.06 else 'Net-return target',n>=target-1e-12),('Reserve',weights[4]>=reserve-1e-12),('Volatility',v<=vol_limit+1e-12),('Rolling turnover',t+prior_turnover<=turnover_limit+1e-12)]:
            if not ok: failed.append(label)
        if stopped: failed.append('Signal/drawdown pause')
        if stale: failed.append('Stale data')
        rows.append(dict(portfolio=name,weights=dict(zip(TICKERS,map(float,weights))),gross_estimate=g,net_estimate=n,volatility=v,one_way_turnover=t,rolling_turnover=t+prior_turnover,trading_cost=c,verdict='FAIL' if failed else 'PASS',failed_rules=failed))
    return dict(as_of=decision_date,price_end='2026-09-30',snapshot_available=AVAILABLE.isoformat(),window=window,cost_bps=cost_bps,target=target,reserve=reserve,vol_limit=vol_limit,turnover_limit=turnover_limit,prior_turnover=prior_turnover,drawdown=drawdown,current_weights=dict(zip(TICKERS,map(float,current))),signal_value=momentum,signal_active=signal,stale=stale,paused=stopped,feasible_grid_count=int(feasible.sum()),rows=rows,recommendation='REJECT live allocation; educational pilot only' if stale or stopped or chosen is None else 'PILOT for validation only; no live allocation authorized')


def stresses():
    # The separate locked 30-bps experiment must not run before the human prediction is committed.
    cases={'Base':{},'Equity mean estimates minus 2 percentage points':{'haircut':.02},'36-return window':{'window':36},'48-return window':{'window':48},'50-bps trading costs':{'cost_bps':50},'10% BIL reserve':{'reserve':.1},'10% turnover limit':{'turnover_limit':.1},'5% volatility ceiling':{'vol_limit':.05},'15% drawdown reached':{'drawdown':.15}}
    return {name:review(**kwargs) for name,kwargs in cases.items()}
