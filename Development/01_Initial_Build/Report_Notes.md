# Team 4 report notes

The report uses the supplied synthetic enterprise dataset: 5,000 allocation observations, 60 fields, 2024–2026. All visuals are native Power BI visuals. No custom visual package is included.

## Pages

1. Executive: portfolio KPIs, unit profitability, trends, budget execution and operating scorecard.
2. Financial: revenue, margin, spending, investment return, product economics and LTV/CAC.
3. Demand and inventory: supplied forecast versus actual demand, stockouts, service and order completion.
4. Workforce and assets: weighted utilization, unused hours, downtime, training, maintenance and safety.
5. Allocation priorities: existing decision labels and scores, action queue, and a fixed-capacity demand sensitivity test.

## Navigation and filters

Use the five navigation tabs at the top of each page. Power BI Desktop requires Ctrl+click for navigation actions. The ordinary page tabs also work.

Year, business unit, resource category, scenario and region slicers synchronize across pages. Selecting a chart category filters or highlights related visuals on the same page. Clear the selection or use a slicer's eraser to restore the full view.

The demand-change slicer affects only the scenario coverage, scenario capacity-gap card and gap chart. It is deliberately disconnected from the historical source data. No selection defaults to zero change.

## Measure definitions

- Mean ROI, mean forecast accuracy, mean inventory service, mean fulfilment, mean risk and mean priority are unweighted averages of the supplied record values.
- Portfolio expected ROI = (total expected return − total investment) / total investment.
- Operating margin = total operating profit / total revenue. Operating profit is not labelled EBITDA or cash flow.
- Workforce and equipment utilization = total allocated hours / total available hours.
- Order completion rate = completed orders / (completed + delayed orders).
- Demand WAPE = sum of absolute record-level forecast errors / total actual demand.
- Capacity shortfall = sum of positive record-level service-demand-minus-capacity gaps. Surplus in another record does not offset a shortage.
- Scenario capacity gap applies the selected demand change to every record with capacity fixed, then sums positive gaps.
- Scenario coverage = sum of demand served up to each record's capacity / total adjusted demand.
- LTV/CAC = average supplied LTV / average supplied CAC.
- Reallocation and review counts use the supplied Decision_Status labels. The original score formulas and classification thresholds were not supplied and are not reverse-engineered.

## Interpretation

Existing forecast columns and scores are synthetic inputs, not predictions from a newly trained model. The what-if analysis is a transparent sensitivity calculation, not a constrained optimization solver. The dataset has unequal observation counts by year (2024: 2,004; 2025: 2,000; 2026: 996); aggregate trends reflect sample composition as well as values.

The report intentionally avoids unsupported EBITDA, cash-flow and inventory-expiry calculations. Counts and financial reconciliation were checked against the CSV. Tiny financial differences of up to $0.0001 per record arise from the source's rounding.

The final PBIX embeds imported data. Refresh uses the original CSV path in this project folder. If the folder moves, update the Allocation source path through Transform data / Data source settings before refreshing.
