# Team 4 dashboard implementation and validation

Working validation note — final-file checks are being completed. This is not the comprehensive analytical report.

## Scope and architecture
One Power BI report contains six visible pages: Portfolio; Financial; Demand & Service; Capacity; Priorities; Model Evidence. Three hidden pages provide business-unit drill-through, allocation-record drill-through and KPI definitions. All visuals are native. No publication or upload was performed.

The two official briefs require at least five visualization types, working KPIs, navigation, slicers, drill-through, comparisons and professional presentation. They do not prescribe five dashboard pages. The final submission comprises exactly three files: PBIX, presentation PPTX and comprehensive analytical-report PDF. The dashboard export PDF does not replace that report. Deadlines remain TBA in the supplied briefs.

## Suggested team ownership
| Member | Primary ownership | Review responsibility |
|---|---|---|
| Ahmed Mostafa Helmy | Asset reliability, downtime, maintenance and equipment constraints | Capacity-page evidence and operational feasibility |
| Sherif Samy Karoub | Financial definitions, investment allocation and report integration | Reconciliation and submission coordination; no EBITDA or cash-flow claims without new data |
| Ahmed Mahmoud Elsayed Gohar | Initiative profitability and digital-product interpretation | Financial top-five logic and management implications |
| Abdelrahman Mohamed Mahmoud Ataalla | Demand, inventory, forecast error and regression experiment | Temporal validation, service denominators and leakage review |
| Mostafa Badr El-Din Abdo Ghonim | Workforce capacity, safety and allocation constraints | Scenario interpretation and action-queue validation |

Each owner should review their domain against the CSV and co-author the relevant presentation/report evidence. Shared sign-off covers definitions, filter behavior and reproducibility.

## Independent data review
Master CSV: 5,000 observations, 60 fields, no missing cells or duplicate Record_ID values. Dates span 5 January 2024 to 25 December 2026 across 60 distinct observation dates. Populations are 2,004 (2024), 2,000 (2025), 996 (2026). These are synthetic irregular observations, not a complete regular time series or YTD extract. There are 240 resource IDs and 45 initiatives. Resource category is one-to-one with business unit; a redundant category slicer was removed.

All six workbook sheets were inspected. Its raw Dataset contains 5,000 rows and 60 columns. Its Executive KPIs use several unweighted means; dashboard ratio-of-sums metrics are intentionally distinguished. Publication claims are reference context rather than measured project outcomes. No EBITDA, cash-flow, expiry-date or causal-effect fields support such claims.

## Reconciliation and definitions
| Metric | Definition | Full-population result |
|---|---|---:|
| Allocated budget | Sum allocated USD | 2,515,646,929.3566 |
| Spend | Sum actual spending USD | 2,505,324,105.7410 |
| Revenue | Sum revenue USD | 3,050,089,873.3096 |
| Operating profit | Sum supplied operating profit; revenue less direct and operating costs within source rounding | 1,447,046,441.8957 |
| Budget execution | Spend / allocated budget | 99.5897% |
| Operating margin | Profit / revenue | 47.4427% |
| Weighted expected ROI | (Expected return - investment) / investment | 22.1537% |
| Workforce utilization | Allocated / available hours | 81.7913% |
| Equipment utilization | Allocated / available hours | 79.0928% |
| Order completion | Completed / (completed + delayed) | 91.5327% |
| Attention records | Supplied Review + Reallocate | 293 (282 + 11) |
| Attention budget | Budget associated with attention records; not savings | 150,080,206.9772 |
| Baseline capacity gap | Sum MAX(0, service demand - capacity), per record | 118,341.3837 |

Demand WAPE = sum absolute supplied forecast errors / actual demand. Bias = (sum forecast - actual) / actual. Shortage rate = stockout units / demand. Inventory is a mean observation, not a current stock balance. Revenue, demand and downtime per record normalize observation counts, not changing portfolio composition. Expected ROI is not realized return. DIVIDE produces blank for zero denominators.

## What-if calculation
Demand changes by -10%, 0%, +10% or +20%; capacity remains fixed. Shortfalls are computed at record level before aggregation, so spare capacity on one record cannot cancel another record's gap. Supplied scores/statuses remain unchanged. This is sensitivity analysis, not an allocation optimizer.

| Demand change | Capacity gap, units | Coverage |
|---|---:|---:|
| -10% | 20,813.2100 | 99.2993% |
| 0% | 118,341.3837 | 96.4145% |
| +10% | 311,224.9103 | 91.4277% |
| +20% | 590,812.4981 | 85.0828% |

Unused workforce/equipment hours cannot automatically transfer across dates, locations, skills or assets. Review maintenance, safety, timing and approvals before any transfer.

## Executed AI experiment
Code: train_demand.py; outputs: model_results.json, model_parameters.json and Heldout_Predictions.csv. NumPy ridge regression predicts Demand_Units from business unit, region, initiative and scheduled-month sine/cosine. Planning-time availability is assumed, not recorded. Outcomes, supplied forecasts, finance/resource quantities, scores and IDs are excluded. Categories are learned only from the training window; unknown categories map to zero indicators.

Train on 2024 (2,004); tune penalty 1/10/100/1000 on 2025 (2,000) MAE; select 1; refit 2024–25; evaluate once on 2026 (996). Baseline is the training-window business-unit mean with global fallback. This tests future observations of known portfolio entities, not unseen-entity generalization.

| Held-out metric | Ridge | Historical unit baseline |
|---|---:|---:|
| MAE, units | 113.9617 | 113.4178 |
| RMSE, units | 145.2911 | 144.3367 |
| WAPE | 18.2736% | 18.1864% |

No overall improvement was demonstrated. Retain the baseline for this experiment. Filters on Model Evidence inspect held-out errors and do not retrain. Rare supplied Reallocate labels (11) were not used for classification. Synthetic results do not establish production usefulness or causation.

## Actual Desktop checks so far
- Enhanced project loaded with all 5,000 observations and refreshed successfully from the master CSV and held-out predictions.
- Portfolio cards displayed profit 1.45bn, budget execution 99.6%, weighted expected ROI 22.2%, delayed orders 8.5%, attention budget 150.08m and 293 exceptions.
- Right-click Digital Products -> Business Unit Detail opened 1,000 records with inherited Business_Unit filter; yearly counts 334/500/166.
- Right-click T4-01708 -> Allocation Record Detail opened that exact record/date (15 April 2026), Digital Products, Initiative-43; displayed approximately 224.8K budget, 242.8K spend, -18.0K remaining and 38.3% expected ROI.
- Financial top-five filter rendered five initiative rows after layout refinement.
- Service scenario summary rendered all five scenarios and their record populations.
- Final saved PBIX reopen, reset/navigation controls, scenario selections, cross-filtering and native PDF checks: pending; do not treat these as passed yet.

## Refresh and reproducibility
The report imports data, so a saved PBIX should open with embedded data. Refresh requires the original CSV and working/enhancement/Heldout_Predictions.csv at their recorded local paths. If moved, use Transform data > Data source settings > Change Source, or edit the two File.Contents paths in Power Query. No credentials or cloud service are needed for these local sources.

To reproduce evidence, run audit.py, train_demand.py and validate_sources.py with Python (NumPy, openpyxl, pypdf). To regenerate the editable report, run build_enhanced.py followed by final_refine.py, open Dashboard.pbip in Power BI Desktop, refresh and save as PBIX. Close the project before external edits. Do not run the legacy working/build_report.py directly.

## AI assistance
Codex assisted with audit code, regression code, DAX, report layout and documentation. The team remains responsible for final interpretations and submission. The PDF export is visual dashboard evidence, not the complete capstone analytical report.
