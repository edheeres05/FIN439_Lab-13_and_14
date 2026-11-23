# Locked prediction — decision effect, before the run

Ethan's exact reply on November 23, 2026, after being asked for his predicted committee decision:

```text
allocate
```

This completes the predicted decision action accompanying his unchanged allocation/return/volatility prediction in [the prior pre-run record](https://github.com/edheeres05/FIN439project2/blob/d8b642870e1769db386534b705b50323b66ed890/docs/locked-input-prediction.md). No amount or separate rationale was supplied; neither is invented here. The earlier numerical reasoning is preserved verbatim. AI explained what the action labels mean, but did not select or rewrite Ethan's answer.

## Frozen protocol

Code and data: commit `b8b271489055dde2f9521ded626bcbadfec3b51d`. Baseline: `review()`; changed: `review(cost_bps=30.)`. Only the cost parameter changes, from 10 to 30 bps per dollar bought/sold. All other parameters remain the frozen defaults described in the original record. Report the constrained portfolio weights, estimated gross/net return, volatility, cost, turnover, numerical feasibility and actual process recommendation, including any gate preventing live allocation. Preserve both expected and actual decision effects even if they differ.

No 30-bps experiment has been run by the assistant before this commit. Execute only after this record is successfully committed to GitHub.
