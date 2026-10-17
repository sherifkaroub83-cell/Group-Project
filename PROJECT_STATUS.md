# Project Status

**Last updated:** 17 October 2026
**Submission deadline:** To be announced on Moodle (also TBA: executive presentation date)

## Deliverables

Moodle accepts exactly three files, named as below (see [Final_Deliverables/](Final_Deliverables/)).

| # | Deliverable | Required file | Status |
|---|---|---|---|
| 1 | Executive Power BI dashboard | `Group_9226_Team_4_Dashboard.pbix` | 🟡 Built and fixed; final checks still open |
| 2 | Executive presentation (12–15 slides) | `Group_9226_Team_4_Presentation.pptx` | 🔴 Not started in this repo |
| 3 | Comprehensive analytical report (20–25 pages) | `Group_9226_Team_4_Report.pdf` | 🔴 Not started in this repo |

The dashboard PDF export in `Final_Deliverables/Supporting/` is **not** the analytical report. It can be used for figures in the report and presentation.

## Completed

- **Data review.** 5,000 records and 60 fields, with no missing cells or duplicate IDs. Records per year are uneven (2,004 / 2,000 / 996), so trends are shown per record.
- **Dashboard.** Six pages: Portfolio, Financial, Demand & Service, Capacity, Priorities and Model Evidence. Three hidden pages: Business Unit drill-through, Record drill-through and KPI definitions. All visuals are native Power BI visuals.
- **KPI reconciliation.** Dashboard figures were checked against the CSV. Examples: allocated budget $2.52bn, operating profit $1.45bn, budget execution 99.6%, weighted expected ROI 22.2%, 293 records flagged for review or reallocation. Full table in [Implementation_Validation.md](Development/02_Enhancement/Implementation_Validation.md).
- **What-if analysis.** Demand is changed by −10%, 0%, +10% or +20% while capacity stays fixed, and the resulting capacity gaps are shown on the Priorities page.
- **AI experiment.** A ridge regression predicting demand, trained on 2024, tuned on 2025 and tested on 2026. It did **not** beat the baseline of each business unit's historical mean (held-out WAPE 18.27% vs 18.19%). This result must be reported honestly in the report and presentation.
- **Fixes (17 Oct).** Layout, labels, axes and new charts on every page, then refreshed and checked in Power BI Desktop. See [CHANGES.md](Development/03_Fixes_2026-10-17/CHANGES.md).

## Open items

| Item | Owner | Notes |
|---|---|---|
| Build the presentation (PPTX) | Team | Must include model evidence and AI-use disclosure |
| Write the analytical report (PDF) | Team, integrated by Sherif | Must include model evidence, AI-use disclosure, refresh procedure, references and team contributions |
| Re-point PBIX data sources | Sherif | The submitted PBIX still uses the old CSV paths from before this reorganization (project root and `working/enhancement/`). Opening it works because the data is embedded; refreshing it needs Change Source |
| Final PBIX checks | Sherif | Listed as pending in the validation note: reopen the saved file, reset/navigation buttons, scenario selections, cross-filtering, native PDF export |
| Domain sign-off | Each member | Each owner reviews their pages against the CSV (see team table in [README.md](README.md)) |
| Check consistency across all three deliverables | Team | KPIs, model metrics and recommendations must match in the PBIX, PPTX and PDF |

## Known limitations to disclose

- The data is synthetic and educational. Supplied forecasts and scores are inputs, not outputs of a model we trained.
- No EBITDA, cash-flow or inventory-expiry figures are claimed, because the data does not support them.
- The what-if analysis is a sensitivity test, not an optimizer. Spare hours cannot simply be moved across sites, skills or assets.
- Expected ROI is not realized return.
