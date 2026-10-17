from pathlib import Path
import csv,json,collections,hashlib,zipfile,re,importlib.util
R=Path(__file__).resolve().parents[2]; O=Path(__file__).parent
rows=list(csv.DictReader((R/'Group_9226_Team_4_Enterprise_Dataset.csv').open(encoding='utf-8-sig')))
for r in rows:
 for k in list(r)[18:]:r[k]=float(r[k])
s=lambda k,rs=rows:sum(r[k] for r in rs)
kpi={'Records':len(rows),'Allocated Budget':s('Budget_Allocated_USD'),'Actual Spend':s('Actual_Spend_USD'),'Revenue':s('Revenue_USD'),'Operating Profit':s('Operating_Profit_USD'),'Budget Utilization':s('Actual_Spend_USD')/s('Budget_Allocated_USD'),'Operating Margin':s('Operating_Profit_USD')/s('Revenue_USD'),'Portfolio Expected ROI':(s('Expected_Return_USD')-s('Investment_Amount_USD'))/s('Investment_Amount_USD'),'Workforce Utilization':s('Workforce_Allocated_Hours')/s('Workforce_Available_Hours'),'Equipment Utilization':s('Equipment_Allocated_Hours')/s('Equipment_Available_Hours'),'Order Completion':s('Orders_Completed')/(s('Orders_Completed')+s('Orders_Delayed')),'Attention Budget':sum(r['Budget_Allocated_USD'] for r in rows if r['Decision_Status'] in ['Review','Reallocate'])}
scenarios={}
for f in [-.1,0,.1,.2]:
 d=sum(r['Service_Demand']*(1+f) for r in rows);g=sum(max(0,r['Service_Demand']*(1+f)-r['Service_Capacity']) for r in rows)
 scenarios[str(f)]={'gap':g,'coverage':1-g/d}
a={'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'Group_9226_Team_4_Project.pbix',R/'Group_9226_Team_4_Enterprise_Dataset.csv']},'kpis':kpi,'scenarios':scenarios,'years':dict(collections.Counter(r['Record_Date'][:4] for r in rows)),'decisions':dict(collections.Counter(r['Decision_Status'] for r in rows)),'missing':sum(v=='' for r in rows for v in r.values()),'duplicate_ids':len(rows)-len({r['Record_ID'] for r in rows}),'date_range':[min(r['Record_Date'] for r in rows),max(r['Record_Date'] for r in rows)],'unit_resource':{b:sorted({r['Resource_Category'] for r in rows if r['Business_Unit']==b}) for b in sorted({r['Business_Unit'] for r in rows})},'scenario_service':{b:{'records':len(t:=[r for r in rows if r['Scenario_Label']==b]),'delay_rate':s('Orders_Delayed',t)/(s('Orders_Completed',t)+s('Orders_Delayed',t))} for b in sorted({r['Scenario_Label'] for r in rows})}}
mdl=(R/'working/Team4.SemanticModel/definition/tables/Allocation.tmdl').read_text(encoding='utf-8-sig');a['measures']=len(re.findall(r'^\s*measure ',mdl,re.M));a['relationships']=(R/'working/Team4.SemanticModel/definition/relationships.tmdl').read_text()
with zipfile.ZipFile(R/'Group_9226_Team_4_Project.pbix') as z:
 a['pages']=[json.loads(z.read(n))['displayName'] for n in z.namelist() if n.endswith('/page.json')];a['custom_visuals']=[n for n in z.namelist() if 'customvisual' in n.lower()]
(O/'audit.json').write_text(json.dumps(a,indent=2));print(json.dumps(a,indent=2));print('NUMPY',importlib.util.find_spec('numpy'))
