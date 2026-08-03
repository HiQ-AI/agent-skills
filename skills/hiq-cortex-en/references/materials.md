# Material family reference

Domain knowledge for **deciding what to search for** and **spotting ambiguity**.

This file contains **no citable numbers**. It only describes what to distinguish, how to search, and when clarification is mandatory. **All values come from tool calls** — that is the entire reason this skill exists: emission factors vary with database, version, system model, route, and geography, and there is no universal number to memorise.

The ratios mentioned below (e.g. "primary vs recycled aluminium differs by 4–10×") exist to explain why routes must be separated. Do not derive numbers from them.

Search terms are given in English because process names in most databases are English. HiQLCD is bilingual, where Chinese terms often match better.

## Steel

| What the user says | Industry term | Process meaning | Search terms |
|---|---|---|---|
| Integrated / BOF steel | BF-BOF | Iron ore → blast furnace → basic oxygen furnace → crude steel | `blast furnace, basic oxygen furnace` |
| Mini-mill / EAF steel | EAF | Scrap → electric arc furnace → crude steel | `electric arc furnace, steel scrap` |
| DRI route | DRI+EAF | Natural-gas direct reduction + EAF | `direct reduced iron, electric arc furnace` |
| Green steel / hydrogen steel | H-DRI+EAF | Green-hydrogen reduction + EAF | `hydrogen-based DRI, green steel` |
| Hot-rolled coil / sheet / section | — | Crude steel → reheating → rolling | `hot rolling, steel coil/sheet/plate` |
| Cold-rolled sheet / strip | — | Hot rolling → pickling → cold rolling | `cold rolling, steel sheet` |
| Galvanized sheet (hot-dip / electro) | — | Cold-rolled sheet → zinc coating | `galvanized steel, zinc coating` |
| Rebar / reinforcing steel | — | Integrated route → hot-rolled bar | `reinforcing steel, steel rebar` |
| Stainless steel | 304 / 316 / 430 | EAF + AOD refining | `stainless steel, chromium steel 18/8` |
| Pellets / sinter | Ironmaking feed | Pelletising / sintering | `iron ore pellet / sinter` |

About 90% of Chinese steel output is the integrated (BF-BOF) route. When the user does not specify, assume BF-BOF and state the assumption.

## Aluminium

| What the user says | Process meaning | Search terms |
|---|---|---|
| Primary aluminium | Alumina → electrolysis | `primary aluminium, electrolysis` |
| Recycled / secondary aluminium | Scrap → remelting | `secondary aluminium, scrap` |
| Extrusion / profile | Extrusion forming | `aluminium extrusion, profile` |
| Sheet / coil | Rolling | `aluminium sheet, rolling` |
| Foil | Very thin rolling (6–200 μm) | `aluminium foil` |
| Die-cast aluminium | Casting alloys such as ADC12 | `aluminium die casting` |

Primary and recycled differ by 4–10×. When the user says only "aluminium", **clarification is mandatory** — or at minimum present both side by side.

## Plastics

| What the user says | Still to distinguish | Search terms |
|---|---|---|
| PE / polyethylene | HDPE / LDPE / LLDPE | `polyethylene, high/low density` |
| PP / polypropylene | — | `polypropylene, granulate` |
| PVC | Rigid (pipe) / flexible (film) | `PVC suspension / PVC emulsion` |
| PET | Bottle grade / fibre grade | `PET bottle grade / PET fibre` |
| ABS | — | `acrylonitrile butadiene styrene` |
| PC / polycarbonate | — | `polycarbonate` |
| PA / nylon | PA6 / PA66 | `polyamide 6 / polyamide 6.6` |
| Glass-fibre reinforced | Base resin + fibre fraction | `glass fibre reinforced` + base resin |
| Recycled plastic | Which resin specifically | `recycled` + specific resin |

"Plastic" alone always requires asking which resin. A specific grade (PP, ABS …) can be searched directly.

## Chemicals

| What the user says | Ambiguity | Key distinction |
|---|---|---|
| Caustic soda / NaOH | Co-produced with chlorine; allocation dominates | Membrane / diaphragm process; allocation basis |
| Ethanol | Petrochemical vs fermentation routes differ 2–3× | Synthetic / bio-based |
| Hydrogen | Grey / blue / green differ 5–10× | Steam reforming / electrolysis |
| Ammonia | Natural-gas route vs green ammonia differ 3–5× | Conventional / green |
| "Additive", "auxiliary" | Could be anything | Must ask for the chemical name or CAS number |

## Energy

| What the user says | Search terms | Key variable |
|---|---|---|
| Electricity / grid power | `electricity, grid mix` | **Geography** |
| Green power | `electricity, wind/solar/hydro` | Which renewable specifically |
| Steam | `steam, [pressure], from [fuel]` | Pressure level + fuel |
| Natural gas (combustion) | `natural gas, burned in` | Direct combustion |
| Natural gas (feedstock) | `natural gas, at plant` | Upstream extraction |
| Diesel (combustion) | `diesel, burned in` | Direct combustion |

## Transport

| What the user says | Must distinguish | Search terms |
|---|---|---|
| Transport / logistics | Mode must be specified | — ask first — |
| Sea freight | Container / bulk | `container ship / bulk carrier` |
| Road freight | Vehicle tonnage | `lorry, 16-32t / 3.5-7.5t` |
| Rail | Electric / diesel | `freight train, electric/diesel` |
| Air freight | Belly hold / freighter | `air freight, long-haul` |

## Geographic sensitivity

| Sensitivity | Materials | Handling |
|---|---|---|
| Very high | Electricity, primary aluminium | **Geography must be clarified** |
| High | Steel, cement | Clarification recommended |
| Medium | Glass, paper | Optional |
| Low | Commodity plastics, basic chemicals | Skip; GLO is fine |

Common geographies to offer: China CN · global average GLO · Europe RER · no preference

## Common unit mismatches

| Unit the user expects | Database unit | Conversion needs |
|---|---|---|
| Per metre (pipe) | Per kg | Linear density kg/m |
| Per square metre (sheet) | Per kg | Areal density = thickness × density |
| Per piece | Per kg | Unit mass |
| Per kWh (battery) | Per kg | Energy density kWh/kg |
| Per tkm | Per kg·km | 1 tkm = 1000 kg·km |
| Per litre (liquid) | Per kg | Density |

Search in the database's native unit (usually per kg), then tell the user which conversion factor they need.

## Product decomposition reference

When the user gives a product name, work out its composition before deciding what to search.

- **Drainage pipe** — PVC body 90–95% + calcium carbonate filler 3–5% + stabilisers 2–3%. Ecoinvent has complete PVC pipe extrusion datasets that can be used directly.
- **Cable** — copper conductor + XLPE/PVC insulation + steel armour + PVC sheath; search all four separately.
- **Corrugated box** — linerboard 55–65% + fluting medium 35–45%. Ecoinvent has aggregated corrugated board datasets.
- **Animal feed** — roughly maize 60% + soybean meal 25% + wheat bran 10% + premix 5%. Usually no dedicated dataset exists; build a composition proxy from the ingredients.
- **Lithium battery pack** — cathode (NMC / LFP) + graphite anode + electrolyte + copper and aluminium foil + housing. Confirm the cell chemistry first.
- **PV module** — glass 65–70% + wafer + EVA + aluminium frame. Ecoinvent has module-level aggregated datasets.
- **LED bulb** — aluminium heat sink + PC diffuser + PCB driver + LED chip; search per component.
- **Cotton T-shirt** — cotton fibre 85–92% + polyester sewing thread + dyeing and finishing chemicals. Wet processing accounts for 30–50% of the footprint.

When unsure how a product decomposes, look it up before assuming.
