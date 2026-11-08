# Ranking AI Investment Forecasts

**Original Scoring, Dynamic Rescoring, and the Trade-Off Between Return-Focused
and Risk-Adjusted Strategies**

Russlan Ramdowar, Future Edge Group FZE / iPulse AI. Version 1.0.0, 8 November 2026.
Author: russlan@ipulseai.com. ORCID: https://orcid.org/0009-0004-9311-6957 .

Deep multi-agent research changes slowly; stock prices move every day. This
paper separates how a forecast is ranked when it is created from how that
ranking should change between research runs. It also separates return-focused
ranking from explicit normalization for historical price volatility.

## Paper and supporting archive

- Paper: [PDF](paper/Ranking_AI_Investment_Forecasts.pdf)
- Source: [LaTeX](paper/main.tex), [Markdown](paper/Ranking_AI_Investment_Forecasts.md)
- Zenodo: [10.5281/zenodo.24051542](https://doi.org/10.5281/zenodo.24051542) (version 1.0.0).
- arXiv: submitted under cs.MA on 8 November 2026; public identifier will be added after announcement.

This is a new ranking paper. Its companion research-budget paper is
[arXiv:2611.04348](https://arxiv.org/abs/2611.04348), with the exact bridge artifacts
at [Zenodo v2.1.0](https://doi.org/10.5281/zenodo.23941195).

## What the experiments find

The original-scoring grid compares 48 fixed formulas across six cohorts and
3,456 portfolios. A separate grid compares 115 rescoring policies across
8,280 portfolios. G10 supports a return-focused ranking, while B02 provides a
separate volatility-adjusted objective. For one-year eligible BUY selections,
a 75% fixed-original/25% current G10 blend wins 15 of 18 primary cells, averaging
19.54% versus 12.80% for raw updated G10. Retaining early risers is its leading
observed mechanism. Concentration controls expose a weaker all-cohort result:
with Moderna's sleeve held as cash the blend wins 17 of 36 cells. The paper
retains raw G10 for five-year rescoring on matched-cell consistency.

The separate 203-stock bridge measures reuse improvement under the companion's
own net costs and clocks. It is not pooled with the two main experiments.

## Reproduce the published calculations

Python 3.9+ and its standard library suffice:

```sh
python3 code/verify_release.py
python3 code/verify_diagnostics.py
```

The verifier rebuilds all 48 original score orders and all 115 checkpoint-policy
selection groups, verifies 11,736 terminal portfolios and their daily drawdowns,
and checks the reported medians, Moderna controls and attribution sums. The
first command reads about 2.1 million derived daily rows and can take a minute.
Compile `paper/main.tex` with a standard LaTeX installation for the manuscript.

[Data dictionary](docs/DATA_DICTIONARY.md) defines fields, units and clocks.
The public archive includes generated forecast features and derived simulation
outputs. Licensed raw quote histories, FX rows and market-action feeds remain
outside the public release. The manuscript retains the approved commercial
interest and AI-assistance disclosures and one consolidated limitations section.

## Licenses

Original paper, figures, generated forecast summaries and authored research
outputs: **CC BY 4.0**. Focused research/reproduction code: **MIT**.
See LICENSE-DATA-AND-PAPER and LICENSE-CODE. Third-party rights remain unchanged.
