# Comparability

Most wrong LCA answers are not wrong numbers — they are correct numbers compared on incompatible bases. Check these before putting two values side by side.

## The five dimensions

| Dimension | Why it breaks comparison |
|---|---|
| **Functional unit / reference flow** | 1 kg of sheet vs 1 m² of coated panel vs 1 m³ of concrete are different questions. Convert explicitly or do not compare. |
| **System model** | Cut-off and consequential answer different questions (attribution vs marginal effect). A delta between them is meaningless. |
| **System boundary** | Cradle-to-gate (A1-A3) vs cradle-to-grave. EPDs declare modules explicitly — compare A1-A3 to A1-A3. |
| **Geography** | Grid mix, fuel mix, and technology vintage. Often the single largest driver. |
| **Database and version** | Different modelling conventions and background data. Cross-database deltas partly measure the databases, not the products. |

State the basis with every number:

> 0.0269 kg CO₂e/kWh — BAFU 2025, DEFAULT, CH, low-voltage grid at consumer

## Aggregation results

`aggregate_datasets` and `aggregate_indicators` return a `comparability_note`. **Read it before quoting percentiles.**

- Mixed units or system models in the cohort → the distribution is a magnitude reference only, not a percentile you can quote.
- `n < 8` → too small for percentiles. Give the range and the count.
- A cohort spanning many orders of magnitude usually means mixed functional units, not real spread. Narrow the predicate.

When positioning a user's own value, the cohort must be built on the same basis as their number. A Chinese plant's steel benchmarked against a European cohort tells them about geography, not performance.

## Production routes

For route-sensitive materials, an "average" value hides the decision:

| Material | Routes that differ materially |
|---|---|
| Steel | BF-BOF (primary) vs EAF (scrap-based) |
| Aluminium | Primary (electrolysis, grid-dependent) vs recycled |
| Stainless 304 | Mixed technology vs EAF route |
| Hydrogen | Grey (SMR) vs blue (with CCS) vs green (electrolysis) |
| Cement | Clinker factor and alternative fuels |
| Plastics | Virgin vs mechanical vs chemical recycling |

Search each named route separately, aggregate per route, and present them side by side on one functional unit. Explain what drives the gap (energy source, scrap availability, allocation of recycled content) and under which conditions the recommendation flips. A single averaged number is the wrong deliverable here.

## EPD comparison

- `epd_peer_benchmark` counts **one vote per registration number** — multiple variants under one registration cannot inflate the distribution.
- Always pass `declared_unit`. Comparing per-m³ to per-tonne EPDs produces nonsense.
- `comparability_note.sufficient: false` (n < 5) → order-of-magnitude reference only.
- Grid mix, allocation method, and EF version differences widen the spread — a value outside the 1.5× fence is a prompt to check basis first, not automatic evidence of a bad EPD.

## Proxies

When no dataset matches the actual material, a proxy is legitimate **if you say it is one**:

1. Prefer same material family, same route, different geography over same geography, different material.
2. State the substitution and its direction of error explicitly ("使用欧洲数据代替中国产地,中国电网碳强度更高,实际值可能偏高").
3. Never present a proxy as the material's own value.
4. Never substitute a proxy for a **restricted** value — that is the user's licensing decision, not yours. Show the restriction and the purchase link.
