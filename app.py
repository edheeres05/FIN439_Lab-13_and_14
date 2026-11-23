import json
import pandas as pd
import streamlit as st
from engine import review, stresses, TICKERS, BENCH
st.set_page_config(page_title='Six-ETF Committee Review',layout='wide')
st.title('Six-ETF Committee Review')
st.caption('Built with ChatGPT/Codex assistance. Ethan Heeres owns the analysis and decision. Education, not investment advice.')
st.info('Frozen research snapshot ending September 2026. This app does not place trades. Live allocation is blocked by stale data.')
with st.sidebar:
    st.header('Scenario inputs')
    window=st.selectbox('Monthly return observations',[59,48,36])
    costs=st.number_input('Trading cost per bought/sold dollar (bps)',0.,100.,10.)
    target=st.number_input('Estimated net-return target (%)',0.,30.,6.)/100
    reserve=st.number_input('Minimum BIL (%)',0.,100.,5.)/100
    limit=st.number_input('Estimated volatility ceiling (%)',0.,50.,15.)/100
    turnover=st.number_input('Rolling annual turnover ceiling (%)',0.,100.,25.)/100
    prior=st.number_input('Turnover already used in last 12 months (%)',0.,100.,0.)/100
    drawdown=st.number_input('Current net-wealth drawdown (%)',0.,100.,0.)/100
    st.caption('Illustrative starting holdings default to the benchmark. Replace with actual pre-trade weights for another scenario.')
    current=[st.number_input(f'{ticker} pre-trade weight (%)',0.,100.,float(w*100))/100 for ticker,w in zip(TICKERS,BENCH)]
try:
    result=review(window=window,cost_bps=costs,target=target,reserve=reserve,vol_limit=limit,turnover_limit=turnover,prior_turnover=prior,drawdown=drawdown,current=current)
except ValueError as exc:
    st.error(str(exc));st.stop()
st.subheader(result['recommendation'])
st.write('Committee ask: permit an educational validation pilot; allocate 0% of live capital to this process until fresh data, prospective evidence, and the remaining validation requirements are approved.')
a,b,c=st.columns(3)
a.metric('Data through',result['price_end']);b.metric('12-month VOO signal',f"{result['signal_value']:.2%}");c.metric('Feasible grid allocations',result['feasible_grid_count'])
summary=[]
for row in result['rows']:
    summary.append({'Portfolio':row['portfolio'],'Net return estimate':f"{row['net_estimate']:.2%}",'Volatility':f"{row['volatility']:.2%}",'One-way turnover':f"{row['one_way_turnover']:.2%}",'Trading cost':f"{row['trading_cost']:.2%}",'Verdict':row['verdict'],'Failed rules':', '.join(row['failed_rules'])})
st.dataframe(pd.DataFrame(summary),hide_index=True,width='stretch')
st.dataframe(pd.DataFrame({r['portfolio']:{k:round(v*100,2) for k,v in r['weights'].items()} for r in result['rows']}),width='stretch')
if result['feasible_grid_count']==0: st.warning('No allocation satisfies all numerical constraints. Do not relax policy silently.')
st.caption('Weights in percent. All portfolios are long-only, fully invested, unleveraged ETFs. Liquidity assumes normal-market sale and settlement within five business days; this is not a stressed-market guarantee. Direct issuer cap does not apply to diversified funds; overlapping underlying holdings remain a risk.')
with st.expander('Signal, timing, and interpretation'):
    st.write('VOO trailing 12-month adjusted-price return through September 30, 2026. Input file existed on GitHub October 22, 2026 at 21:44:32 UTC. It may inform decisions after that timestamp, never earlier backtests. Negative or zero signal pauses new risk-taking. This rule is an AI-proposed research rule, not demonstrated alpha. Current positive signal does not override stale-data or risk failures.')
    st.write('Estimated return = 12 × monthly arithmetic mean. Annual covariance = 12 × monthly sample covariance. Costs charge both securities traded; estimated first-year net return = (1 − trading cost) × (1 + gross estimate) − 1. ETF expense ratios embedded in price returns are not subtracted again. Taxes excluded. Annual rebalance; monthly review; prior turnover and drawdown require an actual account ledger.')
if st.button('Run documented stress suite'):
    cases=stresses()
    st.dataframe(pd.DataFrame([{'Scenario':name,'Feasible allocations':r['feasible_grid_count'],'Decision':r['recommendation']} for name,r in cases.items()]),hide_index=True)
    st.download_button('Download stress results',json.dumps(cases,indent=2),'stress-results.json')
st.download_button('Download current review',json.dumps(result,indent=2),'review.json')
