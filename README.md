# AI-Assisted Resource Allocation and Business Performance Optimization

Capstone group project for **Data Analytics for AI Business**, Group 9226, Team 4. The project is based on a synthetic enterprise dataset: 5,000 records and 60 fields covering 2024–2026.

For progress, open items and owners, see **[PROJECT_STATUS.md](PROJECT_STATUS.md)**.

## Repository layout

| Folder | Contents |
|---|---|
| [Final_Deliverables/](Final_Deliverables/) | Files for the Moodle submission (PBIX, PPTX, report PDF), plus supporting exports |
| [Course_Materials/](Course_Materials/) | Course brief, announcement, supplied reference publication and analytics workbook |
| [Data/](Data/) | Supplied master dataset (`Group_9226_Team_4_Enterprise_Dataset.csv`) |
| [Development/01_Initial_Build/](Development/01_Initial_Build/) | First PBIP build of the dashboard, its build scripts, KPI checks and report notes |
| [Development/02_Enhancement/](Development/02_Enhancement/) | Redesigned dashboard, demand-regression experiment, audit and validation notes |
| [Development/03_Fixes_2026-10-17/](Development/03_Fixes_2026-10-17/) | Latest PBIP source with visual and layout fixes ([CHANGES.md](Development/03_Fixes_2026-10-17/CHANGES.md)) |

## Team

| Member | Reg. No. | Focus |
|---|---|---|
| Ahmed Mostafa Helmy | 24220861 | Asset reliability, downtime, maintenance |
| Sherif Samy Karoub | 24225778 | Financial definitions, investment allocation, report integration |
| Ahmed Mahmoud Elsayed Gohar | 24221240 | Initiative profitability, CAC/LTV |
| Abdelrahman Mohamed Mahmoud Ataalla | 24225790 | Demand, inventory, forecasting experiment |
| Mostafa Badr El-Din Abdo Ghonim | 24225799 | Workforce capacity, safety, scenario analysis |

## Refreshing the dashboard

The PBIX has its data embedded, so it opens without the CSV files. Refreshing it needs two local files:

- `Data/Group_9226_Team_4_Enterprise_Dataset.csv`
- `Development/02_Enhancement/Heldout_Predictions.csv`

If they are in a different folder on your machine, open **Transform data → Data source settings → Change Source** and point both sources to your copies.

> **Note:** The Python scripts in `Development/` were written for the earlier folder layout (`working/...`). They are kept as a record of how the files were built and won't run as-is unless you update their paths.
