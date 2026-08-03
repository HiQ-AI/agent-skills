# Comparability

Most wrong LCA conclusions are not arithmetic errors — they are correct numbers placed side by side on incompatible bases. Run through the following before putting two numbers next to each other.

## The five dimensions

| Dimension | Why it breaks comparability |
|---|---|
| **Functional unit / reference flow** | 1 kg of sheet, 1 m² of coated panel, and 1 m³ of concrete answer different questions. Convert explicitly, or do not compare. |
| **System model** | Cut-off and consequential answer different questions (attributional vs marginal effect). The delta between them is meaningless. |
| **System boundary** | Cradle-to-gate (A1-A3) vs cradle-to-grave. EPDs declare their modules explicitly — A1-A3 compares only with A1-A3. |
| **Geography** | Grid mix, fuel mix, technology vintage. Often the single largest driver. |
| **Database and version** | Different modelling conventions and background data. Part of any cross-database delta measures the database itself, not the product. |

State the basis with every number:

> 0.0269 kg CO₂e/kWh — BAFU 2025, DEFAULT, CH, low-voltage grid at the consumer

## Aggregate results

`aggregate_datasets` and `aggregate_indicators` return a `comparability_note`. **Read it before citing a percentile.**

- Mixed units or system models in the cohort → the distribution is an order-of-magnitude reference only, not citable as a percentile.
- `n < 8` → sample too small; give the range and the sample size instead of a percentile.
- A cohort spanning several orders of magnitude usually means mixed functional units, not genuine dispersion — narrow the predicate.

When positioning a user's own number, the cohort must share their basis. Benchmarking a Chinese mill's steel against a European cohort measures geography, not performance.

## Production routes

For route-sensitive materials, an "average" erases the decision-relevant information:

| Material | Routes that differ materially |
|---|---|
| Steel | BF-BOF (primary) vs EAF (scrap) |
| Aluminium | Primary (electrolysis, grid-dependent) vs recycled |
| 304 stainless | Mixed technology vs EAF route |
| Hydrogen | Grey (SMR), blue (with CCS), green (electrolysis) |
| Cement | Clinker factor and alternative fuels |
| Plastics | Virgin, mechanical recycling, chemical recycling |

Search and aggregate each route separately, then present them side by side under one functional unit. Explain what drives the gap (energy mix, scrap availability, allocation method for recycled content) and under what conditions the recommendation flips. A single average is the wrong deliverable for this class of question.

## EPD comparison

- `epd_peer_benchmark` counts **one vote per registration number** — multiple variants under the same registration cannot flood and skew the distribution.
- `declared_unit` is required. Comparing a per-m³ EPD against a per-tonne one is meaningless.
- `comparability_note.sufficient: false` (n < 5) → order-of-magnitude reference only.
- Grid mix, allocation method, and EF version differences all widen the distribution — falling outside a 1.5× fence is a prompt to check the basis first, not grounds to declare the EPD faulty.

## Proxy data

When no exact dataset exists, using a proxy is acceptable **provided you label it as one**:

1. Prefer "same material family, same route, different geography" over "same geography, different material".
2. State the substitution and the direction of the error explicitly (e.g. "European data used for Chinese production; the Chinese grid is more carbon-intensive, so the real value is likely higher").
3. Never present a proxy value as the material's own figure.
4. **Never use a proxy to substitute for restricted data** — that is the user's purchasing decision, not yours. Show the restriction and the purchase link truthfully.
