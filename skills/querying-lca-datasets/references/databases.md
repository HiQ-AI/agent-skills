# Databases

Snapshot as of 2026-08. Versions change over time — the authoritative basis is whatever a `lookup` returns for a given dataset, so always quote the version from the response rather than from this table.

## Free — any valid API key

| Code | Version | System model | LCIA indicators | Use it for |
|---|---|---|---|---|
| `bafu` | 2025 | DEFAULT | 334 | Swiss national inventory. Broad coverage, full LCIA, well maintained. The best free default for European-context work. |
| `elcd` | 3.2 | DEFAULT | 294 | European reference LCD. Materials, energy, transport, end-of-life. |
| `uslci` | 1.0 | DEFAULT | 34 | US unit processes — fuels, transport, forestry, metals. |
| `usda` | 1.0 | DEFAULT | 63 | US agriculture and food systems. |
| `ef` | 3.1.0 | DEFAULT | 14 | Environmental Footprint reference package (EU PEF/OEF context). |
| `worldsteel` | 2020 | DEFAULT | 14 | Global steel industry average data. The reference for steel LCI. |
| `auslci` | 1.40 | DEFAULT | 1 | Australian national inventory. GWP only. |
| `needs` | 1.0 | DEFAULT | 1 | European energy scenarios. GWP only. |
| `ozlci` | 1.0 | DEFAULT | 1 | Australasian datasets. GWP only. |
| `bioenergiedat` | 1.0 | DEFAULT | 1 | European bioenergy. GWP only. |
| `recycledplastics` | 1.0 | DEFAULT | — | Recycled plastics eco-profiles. No LCIA layer — LCI only. |

## Commercial — requires a data package entitlement

| Code | Version | System models | LCIA indicators | Use it for |
|---|---|---|---|---|
| `ecoinvent` | 3.12.0 | CUT_OFF, APOS, CONSEQUENTIAL_LONG, EN_15804 | 240 | The global reference database. Widest coverage; most published studies use it. |
| `hiqlcd` | 1.5.0 | CUT_OFF, CONSEQUENTIAL, EN_15804 | 248 | China-native inventory. Use this for Chinese production, not a European proxy. |
| `hiqlcd-al` | 2.0.0 | CUT_OFF, CONSEQUENTIAL | 359 | Aluminium value chain, China focus. |
| `calcd` | 3.0.0 | CUT_OFF | 359 | Chinese national LCD. |
| `hiq-cesi` | 1.1.0 | CUT_OFF | 359 | Electronics / electrical industry, China. |
| `carbonminds` | 2.0.2 | CUT_OFF | 231 | Chemicals and plastics, process-level detail. |
| `agrifootprint` | 7.0 | CUT_OFF | — | Agriculture and food. No LCIA layer — LCI only. |

## Choosing a database

**Geography drives the answer more than most people expect.** Grid mix alone can move a manufacturing dataset's GWP by 2–5×. Chinese production against a European dataset is a common and serious error — prefer `hiqlcd` / `calcd` / `hiq-cesi` for China, `bafu` / `elcd` / `ef` for Europe, `uslci` / `usda` for the US.

**System model must match the question.**
- `CUT_OFF` — attributional, recycled material enters burden-free. The default for product carbon footprint and EPD work.
- `APOS` — allocation at point of substitution. Ecoinvent alternative attributional model.
- `CONSEQUENTIAL` / `CONSEQUENTIAL_LONG` — marginal effects of a decision. Not interchangeable with cut-off; never mix them in one comparison.
- `EN_15804` — construction products, EN 15804 module structure (A1-A3, A4-A5, B, C, D).
- `DEFAULT` — free databases publish a single model; treat as attributional.

**LCIA coverage varies a lot.** Databases showing 1 indicator carry GWP only — `aggregate_indicators` for AP/EP/ODP will return empty there, and that is a data limitation, not a tool failure. `agrifootprint` and `recycledplastics` have no LCIA layer at all (LCI only).

## Known quirks

- **Functional-unit extremes are usually legitimate.** Some datasets are declared per unusual functional units, so raw GWP min/max across a whole database can span many orders of magnitude. Read the reference flow and unit before calling a value an outlier.
- **`aggregate_indicators` needs the right `source`.** `method_id` is not portable across databases — an Ecoinvent cohort must be aggregated with `source="ecoinvent"`, otherwise the call returns empty.
- **Version matters for keys.** A `dataset_key` encodes source + version + system model. Keys from an older catalog return in `missing_keys` after a database version bump — re-run search rather than editing the key.
- **`partial` search status.** The search returned something related but not an exact match. Read the dataset `name` before using it; a "hot rolled coil" result for a "cold rolled sheet" query is a different product.
