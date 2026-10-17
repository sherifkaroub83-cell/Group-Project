from pathlib import Path
import csv,json,collections,openpyxl,importlib.util
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent
w=openpyxl.load_workbook(R/'Group_9226_Team_4_Analytics_Workbook.xlsx',read_only=True,data_only=True)
summary={s.title:{'rows':s.max_row,'columns':s.max_column,'values':list(s.values)} for s in w};(O/'workbook_review.json').write_text(json.dumps(summary,indent=2,default=str));print({k:(v['rows'],v['columns']) for k,v in summary.items()})
r=list(csv.DictReader((R/'Group_9226_Team_4_Enterprise_Dataset.csv').open(encoding='utf-8-sig')))
checks={}
checks['profit_identity_max_error']=max(abs(float(x['Operating_Profit_USD'])-(float(x['Revenue_USD'])-float(x['Direct_Cost_USD'])-float(x['Operating_Cost_USD']))) for x in r)
checks['budget_variance_max_error']=max(abs(float(x['Budget_Variance_USD'])-(float(x['Budget_Allocated_USD'])-float(x['Actual_Spend_USD']))) for x in r)
checks['negative_numeric_values']={k:sum(float(x[k])<0 for x in r) for k in list(r[0])[18:] if any(float(x[k])<0 for x in r)}
checks['resource_ids']=len({x['Resource_ID'] for x in r});checks['initiatives']=len({x['Project_or_Product'] for x in r});checks['distinct_dates']=len({x['Record_Date'] for x in r})
(O/'governance.json').write_text(json.dumps(checks,indent=2));print(checks)
for m in ['pypdfium2','PIL','reportlab']:print(m, bool(importlib.util.find_spec(m)))
