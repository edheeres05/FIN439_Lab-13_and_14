ChatGPT/Codex (GPT-6) assisted with implementation, validation, and drafting; Ethan Heeres owns the analysis and decision, subject to his final review of this draft.
Education, not investment advice.

# Project 2 — Six-ETF Investment Management

**WORK IN PROGRESS:** runnable draft; locked AI-off record and final presentation evidence are not complete. Current recommendation: reject live allocation, permit educational validation only. Live process allocation range: 0%. Snapshot prices end September 2026; the app visibly fails the freshness gate.

## Run on Windows

Download this branch's ZIP, extract it, and open the folder containing app.py in VS Code. In its terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python -m streamlit run app.py
```

Python 3.12 tested. On macOS/Linux use python3 to create the environment and `.venv/bin/python` for subsequent commands. No API keys or internet data downloads are required at runtime. Stop with Ctrl+C. If imports fail, confirm the terminal is in the folder containing engine.py. Dependency installation needs internet access.

The sidebar edits scenario assumptions and actual pre-trade holdings; weights must total 100%. Default holdings are the illustrative benchmark, not a statement about any real account. Tables show numerical results, individual failed rules, and all allocation weights. Download the review JSON. The stress button runs the documented suite, but do not use it or change trading costs until the required human prediction has been committed.

Approved policy: five years, no planned withdrawals; minimum volatility subject to 6% estimated annual net return, volatility ≤15%, BIL ≥5%, rolling one-way turnover ≤25%; 15% drawdown pause. Annual rebalance, monthly review. Benchmark 50% VOO / 40% BND / 10% BIL. Long-only, no leverage. Liquidity assumes normal-market ETF sale/settlement within five business days; stressed liquidity is not guaranteed. No individual stocks; underlying ETF overlap remains.

Read [decision memo](docs/decision-memo.md), [validation](docs/validation-and-ai-use.md), [signal card](docs/signal-data-card.md) and [visible executed output](outputs/baseline.json). The constrained solution is a 5-percentage-point grid minimum, not a continuous optimum. All means are historical estimates, not guaranteed returns. No signal efficacy, untouched holdout or independent cold run of this build is claimed.

Do not submit as finished until the pending validation and real videos/transcripts are complete. Older Lab13 files in the repository are historical context; this README describes the revised ETF project.
