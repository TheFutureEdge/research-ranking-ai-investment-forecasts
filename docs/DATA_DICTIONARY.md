# Data dictionary and scope

All monetary portfolio fields are USD; returns, drawdowns, disagreement and
annualized volatility are percentage points. Portfolio and subject identifiers
are deterministic research keys, not brokerage positions or account identifiers.

- original_design.json: all 48 scoring rules, cohort clocks and initial funding.
- original_forecast_features.json.gz: 1,505 generated forecast-feature pairs,
  with one/five-year ensemble statistics and scalar historical-volatility inputs.
- original_rankings.json.gz: complete deterministic original score orders.
- original_portfolio_results.json.gz: all 3,456 terminal synthetic portfolios.
- rescoring_design.json: all 115 frozen policies and current economic BUY screen.
- rescoring_forecast_features.json.gz: 9,024 dated derived checkpoint features;
  raw quote/target prices are excluded. `original_scored_at` records later stored
  summary availability; `forecast_generated_at` is the separate generation clock.
- rescoring_rankings.json.gz: 4,140 Top-20 selection groups under that screen.
- rescoring_portfolio_results.json.gz: all 8,280 terminal synthetic portfolios.
- *_portfolio_daily.csv.gz: 2,135,172 derived daily portfolio-wealth observations.
  The original grid has separate `mode` values `anchor` and `availability`.
- *_holding_results.csv.gz: 69,120 original and 124,200 rescoring holding
  allocations, scores, weights and attributed terminal wealth components.
  A holding gain is terminal wealth minus its original allocation.
- bridge_*.json.gz: the separate 203-stock research-reuse comparison, including
  792 fee/cost scenarios and symmetric concentration controls. Do not pool its
  USD300,000 net wallet with the USD100,000 gross experiments.
- additional_metrics.json and CSV diagnostics: new profile, median, issuer-cash,
  attribution and research-budget findings in this manuscript revision.

G10's `mad` is mean absolute deviation, not median absolute deviation. Original
score volatility retains its frozen raw-close lineage; rescoring volatility
uses dated corporate-action-adjusted returns. Cutoffs are 2 November 2026 for
original portfolios and 3 November 2026 for rescoring; the bridge retains its
own earlier endpoints. Holding windows overlap and differ in length.

The full paths are authored portfolio outputs, not downloadable market price
histories. Raw quote rows, FX series and corporate-action feeds are excluded.
The public verifier checks formula selection, every terminal accounting identity,
and daily drawdowns from these frozen outputs. Revaluing them independently
from market observations requires compatible, separately authorized inputs.

Numeric verification uses a 1e-7 absolute tolerance for floating-point outputs.
All tested original Top-30 selections reproduce exactly. Some B08 percentile
composite ties below rank 30 can permute by about 1.4e-14 across Python summation
implementations; the frozen complete order is retained as the canonical record.
This does not change any tested portfolio selection or published result.
