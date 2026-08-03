# Scenario methods: industry benchmarking and lightweight estimation

Two classes of request do not follow the main "search → look up" flow. They need a different method and produce a different deliverable.

## 1. Industry benchmarking (the user has their own number)

Triggers: "is my X kgCO₂e/kg high or low", "how do we compare to peers", "what's the industry average", "where do we sit in the industry".

The user is not asking for one dataset's value — they want **a position within a distribution**. Use `aggregate_datasets` (script: `aggregate`).

### Steps

1. **Converge the product into a comparable cohort.** Like compares only with like, so fix these dimensions first: material/product family, geography, **functional unit** (per kg? per m³? per piece?), system model (cut-off / APOS / consequential). If ambiguous, ask one or two questions — do not guess.

2. **Use a predicate, not hand-picked keys.** You want the "industry" as a population, not thirty samples:
   ```
   aggregate --source hiqlcd --category steel --target 2.5
   ```
   Use `--keys` only when the user has explicitly named a handful of datasets.

3. **Read what the response says about itself before speaking.** It carries `count`, `cohort_profile.by_source`, `comparability_note`, and `percentiles`.

4. **Downgrade when comparability fails — never force a percentile.** Confidently telling someone "you're 15% below average" on a mixed-basis cohort is worse than not answering:
   - **Mixed units** (kg / MJ / piece) → not directly comparable. Re-query with one functional unit locked, or say so.
   - **Mixed system models**, or **n < 8** → downgrade to an order-of-magnitude statement ("few comparable entries; by order of magnitude …") and give no precise percentile.
   - The user's own **system boundary** (to-gate / to-grave, transport and end-of-life included or not) may differ from the cohort — point that out proactively.

5. **Position honestly.** Give the percentile + relative percentage + cohort basis, and state the **sample size** and **which databases** it came from:

   > In the HiQLCD steel cohort (n=21614, cut_off, functional unit 1 kg) you sit around P20, about 29% below the industry median — on the low side. If your boundary includes transport or end-of-life, the comparison basis should be adjusted upward accordingly.

**For carbon, lower is better** — judge "good/bad" from the sign of `target` relative to the median; do not report every position as favourable. A product at P71 is in fact worse than the median.

### Do not

- Do not invent an "industry average" from memory; it must come from the aggregate result.
- Do not give a position without flagging mixed units or system models.
- Do not treat a handful of search hits as the industry population.
- **Do not narrow a cohort down to a single entry to read out a restricted dataset's value.** The aggregate endpoint is for distributions; single values go through `lookup` and are entitlement-gated — using aggregation to bypass that is abuse.

## 2. Lightweight estimation (no BOM yet)

Triggers: "roughly what scale is this product's footprint", "which of these material options is better on carbon, and by how much".

The user's data is incomplete but they need a meaningful direction now, not after the data is complete.

**Not this scenario**: a real BOM already exists → use the main matching flow; the user has their own number and asks how it compares → use benchmarking above.

### Inputs — ask for a few key things, don't demand a full BOM

- Product type / function
- Main materials and approximate shares (exact masses not needed)
- Where it is produced + energy source (grid geography matters a lot)
- For design-selection cases: what the candidate options are and how they differ

When the user cannot supply everything, fill in typical compositions from domain knowledge and **state explicitly that these are assumptions** — an estimate stands on transparent assumptions, not on feigned certainty.

### Method

1. **Decompose** the product into main materials + approximate mass fractions, labelled as assumptions. Composition references in [materials.md](materials.md).
2. **Typical values per material come from the database, not from memory.** Run `aggregate` on a comparable cohort for each material and take the **p25–p75 range** as that material's plausible band (a range, not a falsely precise point). Lock one functional unit and one system model. Aggregate statistics are open to all users, so free databases suffice.
3. **Combine the ranges**: total ≈ Σ(mass fractionᵢ × rangeᵢ). The result is a **range**, never a confident point value.
4. **Material-level hotspots**: identify which material dominates ("the aluminium frame is roughly 60% of the footprint"). Process-level splits (electricity vs feedstock within one material) require `hotspot` — do not infer them from a GWP total.
5. **Option comparison**: run steps 1–4 per option, then give the **delta** and the **key variable**: "Option B is about 30% lower, almost entirely from switching the frame to recycled aluminium — that is the lever worth pursuing."

### Always deliver with a boundary statement

> This is a directional estimate based on typical values from professional databases, not a certification-grade result. A defensible number requires item-by-item matching against a real BOM, or a full LCA.

This is not boilerplate disclaiming — it is the professionalism itself, and it is what separates this from "an AI made up a number".

### Do not

- Do not give typical values from training memory or web hearsay; they must come from aggregate results.
- Do not present an estimate as an exact figure; always give a range and label it directional.
- Do not mix units or system models when building the per-material ranges.
- Do not infer process-level (energy vs feedstock) hotspots from GWP-only data; that requires process modelling.

## 3. Composition proxies (composite products with no dedicated dataset)

Composite, formulated, and blended products (animal feed, coatings, composites) often have no ready-made dataset.

Using animal feed as an example:

1. Decompose from domain knowledge, labelling the fractions as assumptions: maize ~60%, soybean meal ~25%, wheat bran ~10%, premix ~5%.
2. Search and `lookup` each component.
3. Combine by weight: total ≈ Σ(fractionᵢ × valueᵢ).
4. **State the uncertainty plainly**: this is a composition proxy, the fractions are assumptions, and additives and processing energy are not included — a directional result, not a measured feed dataset.

A proxy value must never be passed off as the product's own figure. And a proxy must **never substitute for restricted data** — that is the user's purchasing decision; show the restriction and the purchase link truthfully.
