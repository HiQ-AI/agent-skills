# Databases

Snapshot as of 2026-08. Versions change — the authoritative basis is what `lookup` returns for the specific dataset. Cite the version from the response, not from this table.

## Free — available with any valid API key

| Code | Version | System model | LCIA indicators | Use for |
|---|---|---|---|---|
| `bafu` | 2025 | DEFAULT | 334 | Swiss national inventory. Broad coverage, complete LCIA, well maintained. The best free default in a European context. |
| `elcd` | 3.2 | DEFAULT | 294 | European Reference Life Cycle Database. Materials, energy, transport, end-of-life. |
| `uslci` | 1.0 | DEFAULT | 34 | US unit processes — fuels, transport, forestry, metals. |
| `usda` | 1.0 | DEFAULT | 63 | US agriculture and food systems. |
| `ef` | 3.1.0 | DEFAULT | 14 | Environmental Footprint reference package (EU PEF/OEF context). |
| `worldsteel` | 2020 | DEFAULT | 14 | Global steel industry averages. The reference source for steel LCI. |
| `auslci` | 1.40 | DEFAULT | 1 | Australian national inventory. GWP only. |
| `needs` | 1.0 | DEFAULT | 1 | European energy scenarios. GWP only. |
| `ozlci` | 1.0 | DEFAULT | 1 | Australia/New Zealand datasets. GWP only. |
| `bioenergiedat` | 1.0 | DEFAULT | 1 | European biomass energy. GWP only. |
| `recycledplastics` | 1.0 | DEFAULT | — | Recycled-plastics eco-profiles. No LCIA layer, LCI only. |

## Commercial — requires the corresponding data-package entitlement

| Code | Version | System model | LCIA indicators | Use for |
|---|---|---|---|---|
| `ecoinvent` | 3.12.0 | CUT_OFF, APOS, CONSEQUENTIAL_LONG, EN_15804 | 240 | The global reference database. Widest coverage; most published studies use it. |
| `hiqlcd` | 1.5.0 | CUT_OFF, CONSEQUENTIAL, EN_15804 | 248 | China-specific inventory. Use this for Chinese production — do not substitute European data. |
| `hiqlcd-al` | 2.0.0 | CUT_OFF, CONSEQUENTIAL | 359 | Aluminium value chain, primarily China. |
| `calcd` | 3.0.0 | CUT_OFF | 359 | Chinese Life Cycle Database. |
| `hiq-cesi` | 1.1.0 | CUT_OFF | 359 | Electronics and appliances, China. |
| `carbonminds` | 2.0.2 | CUT_OFF | 231 | Chemicals and plastics at process-level granularity. |
| `agrifootprint` | 7.0 | CUT_OFF | — | Agriculture and food. No LCIA layer, LCI only. |

## Choosing a database

**Geography affects results more than most people expect.** Grid mix alone can move the GWP of a manufacturing dataset by a factor of 2–5. Using a European dataset to represent Chinese production is a common and serious error — prefer `hiqlcd` / `calcd` / `hiq-cesi` for China, `bafu` / `elcd` / `ef` for Europe, `uslci` / `usda` for the US.

**The system model must match the question.**

- `CUT_OFF` — attributional; recycled material carries no upstream burden. The default choice for product carbon footprints and EPDs.
- `APOS` — allocation at the point of substitution. Ecoinvent's alternative attributional model.
- `CONSEQUENTIAL` / `CONSEQUENTIAL_LONG` — marginal effects of a decision. Not interchangeable with cut-off; never mix the two in one comparison.
- `EN_15804` — construction products, structured by EN 15804 modules (A1-A3, A4-A5, B, C, D).
- `DEFAULT` — free databases publish a single model; treat it as attributional.

**LCIA coverage varies widely.** Databases with an indicator count of 1 carry GWP only; running `aggregate_indicators` for AP/EP/ODP against them returns empty — that is a data-side limitation, not a tool failure. `agrifootprint` and `recycledplastics` have no LCIA layer at all (LCI only).

## Known pitfalls

- **Extreme values from functional units are usually legitimate.** Some datasets are declared in unusual functional units, so whole-database GWP min/max can span several orders of magnitude. Read the reference flow and unit before judging a value as an outlier.
- **`aggregate_indicators` needs the right `source`.** `method_id` is not portable across databases — an Ecoinvent cohort must be aggregated with `source="ecoinvent"` or the result is empty.
- **Versions affect keys.** `dataset_key` encodes source + version + system model. After a database version bump, keys from an older catalogue show up in `missing_keys` — search again, do not hand-edit keys.
- **Search status `partial`.** Means related but inexact matches. Read the dataset `name` before use: a search for "cold-rolled sheet" returning "hot-rolled coil" is a different product.
