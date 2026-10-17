import csv, json, uuid, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'working'
REPORT=WORK/'Team4.Report'
DEF=REPORT/'definition'
MODEL=WORK/'Team4.SemanticModel'/'definition'
DATA=ROOT/'Group_9226_Team_4_Enterprise_Dataset.csv'
rows=list(csv.DictReader(DATA.open(encoding='utf-8-sig')))
headers=list(rows[0])
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
def uid(): return uuid.uuid4().hex[:20]
def lit(v):
    val=('true' if v else 'false') if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+str(v).replace("'","''")+"'"
    return {'expr':{'Literal':{'Value':val}}}
def color(v): return {'solid':{'color':lit(v)}}
def props(**kw): return [{'properties':kw}]
NAVY='#112B45'; TEAL='#008C95'; BLUE='#407DB0'; GOLD='#D89836'; INK='#20364B'; MUTED='#63788B'; BG='#F2F5F8'; BORDER='#DCE5ED'

# Preserve the existing project's identity; add its model and report pages.
MODEL.mkdir(parents=True,exist_ok=True)
(MODEL/'tables').mkdir(exist_ok=True)
(MODEL/'model.tmdl').write_text('''model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_ProTooling = ["DevMode"]

ref table Allocation
ref table Calendar
ref table 'Demand Scenario'
ref cultureInfo en-US
''',encoding='utf-8')

measures=[]
def measure(name,expr,fmt='#,0',folder='01 Overview',desc=''):
    measures.append((name,expr,fmt,folder,desc))
currency='$#,0;($#,0);$0'; pct='0.0%;(0.0%);0.0%'
for name,col in [('Allocated Budget','Budget_Allocated_USD'),('Actual Spend','Actual_Spend_USD'),('Revenue','Revenue_USD'),('Operating Profit','Operating_Profit_USD'),('Direct Cost','Direct_Cost_USD'),('Operating Cost','Operating_Cost_USD'),('Investment','Investment_Amount_USD'),('Expected Return','Expected_Return_USD'),('Budget Remaining','Budget_Variance_USD'),('Forecast Revenue','Forecast_Revenue_USD'),('Maintenance Cost','Maintenance_Cost_USD')]:
    measure(name,f'SUM(Allocation[{col}])',currency,'02 Finance')
for name,col in [('Demand','Demand_Units'),('Supply','Supply_Units'),('Inventory','Inventory_Units'),('Stockouts','Stockout_Units'),('Forecast Demand','Forecast_Demand'),('Orders Completed','Orders_Completed'),('Orders Delayed','Orders_Delayed'),('Workforce Available','Workforce_Available_Hours'),('Workforce Allocated','Workforce_Allocated_Hours'),('Equipment Available','Equipment_Available_Hours'),('Equipment Allocated','Equipment_Allocated_Hours'),('Downtime Hours','Downtime_Hours'),('Training Hours','Training_Hours'),('Service Capacity','Service_Capacity'),('Service Demand','Service_Demand')]:
    measure(name,f'SUM(Allocation[{col}])','#,0','03 Operations')
measure('Records','COUNTROWS(Allocation)')
for name,col in [('Mean ROI','ROI_Pct'),('Mean Forecast Accuracy','Demand_Forecast_Accuracy_Pct'),('Mean Inventory Service','Inventory_Service_Level_Pct'),('Mean Workforce Utilization','Workforce_Utilization_Pct'),('Mean Equipment Utilization','Equipment_Utilization_Pct'),('Mean Capacity Coverage','Capacity_Coverage_Pct'),('Mean Order Fulfilment','Order_Fulfilment_Pct'),('Mean Safety Compliance','Safety_Compliance_Pct')]:
    measure(name,f'AVERAGE(Allocation[{col}])',pct,'04 Rates','Unweighted mean of supplied record-level percentages; reconciles to publication where applicable.')
for name,col in [('Mean Resource Risk','Resource_Risk_Score'),('Mean Optimization Priority','Optimization_Priority_Score'),('Customer Satisfaction','Customer_Satisfaction_Score')]:
    measure(name,f'AVERAGE(Allocation[{col}])','0.0','05 Risk and decisions')
for name,expr,desc in [
 ('Budget Utilization','DIVIDE([Actual Spend],[Allocated Budget])','Total spend / total allocated budget.'),
 ('Operating Margin','DIVIDE([Operating Profit],[Revenue])','Operating profit / revenue; not EBITDA.'),
 ('Portfolio Expected ROI','DIVIDE([Expected Return]-[Investment],[Investment])','Investment-weighted expected net return; distinct from mean record ROI.'),
 ('Workforce Utilization','DIVIDE([Workforce Allocated],[Workforce Available])','Allocated / available hours; weighted by available hours.'),
 ('Equipment Utilization','DIVIDE([Equipment Allocated],[Equipment Available])','Allocated / available hours; weighted by available hours.'),
 ('Order Completion Rate','DIVIDE([Orders Completed],[Orders Completed]+[Orders Delayed])','Completed / (completed + delayed) orders.'),
 ('Digital Adoption','DIVIDE(SUM(Allocation[Digital_Transactions]),SUM(Allocation[Total_Transactions]))','Digital / total transactions.'),
 ('Demand WAPE','DIVIDE(SUMX(Allocation,ABS(Allocation[Demand_Units]-Allocation[Forecast_Demand])),[Demand])','Sum absolute forecast error / actual demand. Existing synthetic forecasts; not new model validation.')]:
    measure(name,expr,pct,'04 Rates',desc)
measure('Average CAC','AVERAGE(Allocation[Customer_Acquisition_Cost_USD])',currency,'02 Finance')
measure('Average LTV','AVERAGE(Allocation[Customer_Lifetime_Value_USD])',currency,'02 Finance')
measure('LTV to CAC','DIVIDE([Average LTV],[Average CAC])','0.0"x"','02 Finance','Ratio of average supplied LTV to average supplied CAC.')
measure('Unused Workforce Hours','[Workforce Available]-[Workforce Allocated]','#,0','03 Operations')
measure('Unused Equipment Hours','[Equipment Available]-[Equipment Allocated]','#,0','03 Operations')
measure('Capacity Shortfall','SUMX(Allocation,MAX(0,Allocation[Service_Demand]-Allocation[Service_Capacity]))','#,0','03 Operations','Sum of positive record-level capacity gaps; avoids netting surplus against unrelated shortages.')
measure('Review Records','CALCULATE([Records],KEEPFILTERS(Allocation[Decision_Status] = "Review"))','#,0','05 Risk and decisions')
measure('Reallocation Records','CALCULATE([Records],KEEPFILTERS(Allocation[Decision_Status] = "Reallocate"))','#,0','05 Risk and decisions','Count of supplied Reallocate labels; no undocumented score threshold inferred.')
measure('Attention Records','CALCULATE([Records],KEEPFILTERS(Allocation[Decision_Status] <> "Maintain"))','#,0','05 Risk and decisions')
measure('Attention Budget','CALCULATE([Allocated Budget],KEEPFILTERS(Allocation[Decision_Status] <> "Maintain"))',currency,'05 Risk and decisions')
measure('Selected Demand Change','SELECTEDVALUE(\'Demand Scenario\'[Demand Change],0)',pct,'06 Scenario')
measure('Scenario Demand','[Service Demand]*(1+[Selected Demand Change])','#,0','06 Scenario')
measure('Scenario Capacity Gap','SUMX(Allocation,MAX(0,Allocation[Service_Demand]*(1+[Selected Demand Change])-Allocation[Service_Capacity]))','#,0','06 Scenario','Illustrative scenario with fixed capacity. No optimization solver or trained AI model is implied.')
measure('Scenario Coverage','DIVIDE(SUMX(Allocation,MIN(Allocation[Service_Capacity],Allocation[Service_Demand]*(1+[Selected Demand Change]))),[Scenario Demand])',pct,'06 Scenario')

parts=['table Allocation',f'\tlineageTag: {uuid.uuid4()}']
for n,expr,fmt,folder,desc in measures:
    if desc: parts.append('\n\t/// '+desc)
    parts.extend([f"\tmeasure '{n}' = {expr}",f'\t\tformatString: {fmt}',f'\t\tdisplayFolder: {folder}',f'\t\tlineageTag: {uuid.uuid4()}',''])
for i,h in enumerate(headers):
    typ='dateTime' if h=='Record_Date' else 'string' if i<18 else 'double'
    parts.extend([f'\tcolumn {h}',f'\t\tdataType: {typ}',f'\t\tlineageTag: {uuid.uuid4()}',f'\t\tsummarizeBy: none',f'\t\tsourceColumn: {h}'])
    if typ=='dateTime':parts.append('\t\tformatString: yyyy-mm-dd')
    elif typ=='double':parts.append('\t\tformatString: '+(pct if h.endswith('_Pct') else currency if h.endswith('_USD') else '#,0.0'))
    parts.append('')
types=', '.join('{"'+h+'", '+('type date' if h=='Record_Date' else 'type text' if i<18 else 'type number')+'}' for i,h in enumerate(headers))
source=f'''let
    Source = Csv.Document(File.Contents("{DATA}"),[Delimiter=",", Columns=60, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{{types}}}, "en-US")
in
    Typed'''
parts.extend(['\tpartition Allocation = m','\t\tmode: import','\t\tsource =']+['\t\t\t'+l for l in source.splitlines()])
(MODEL/'tables/Allocation.tmdl').write_text('\n'.join(parts)+'\n',encoding='utf-8')
cal=['table Calendar']
for name,typ,fmt in [('Date','dateTime','yyyy-mm-dd'),('Year','int64','0'),('Month','string',None),('Month Number','int64','0'),('Year Month','string',None),('Year Month Sort','int64','0')]:
    cal.extend([f"\tcolumn '{name}'",f'\t\tdataType: {typ}','\t\tsummarizeBy: none',f'\t\tsourceColumn: {name}'])
    if fmt:cal.append('\t\tformatString: '+fmt)
    if name=='Month':cal.append("\t\tsortByColumn: 'Month Number'")
    if name=='Year Month':cal.append("\t\tsortByColumn: 'Year Month Sort'")
    if name.endswith('Sort') or name=='Month Number':cal.append('\t\tisHidden')
    cal.append('')
cal.extend(['\tpartition Calendar = m','\t\tmode: import','\t\tsource =','\t\t\tlet','\t\t\t    Dates = Table.FromColumns({List.Dates(#date(2024,1,1),1096,#duration(1,0,0,0))},{"Date"}),','\t\t\t    Typed = Table.TransformColumnTypes(Dates,{{"Date",type date}}),','\t\t\t    Y = Table.AddColumn(Typed,"Year",each Date.Year([Date]),Int64.Type),','\t\t\t    M = Table.AddColumn(Y,"Month",each Date.ToText([Date],"MMM","en-US"),type text),','\t\t\t    N = Table.AddColumn(M,"Month Number",each Date.Month([Date]),Int64.Type),','\t\t\t    YM = Table.AddColumn(N,"Year Month",each Date.ToText([Date],"yyyy-MM","en-US"),type text),','\t\t\t    S = Table.AddColumn(YM,"Year Month Sort",each Date.Year([Date])*100+Date.Month([Date]),Int64.Type)','\t\t\tin S'])
(MODEL/'tables/Calendar.tmdl').write_text('\n'.join(cal)+'\n',encoding='utf-8')
(MODEL/'relationships.tmdl').write_text(f'''relationship {uuid.uuid4()}
\tfromColumn: Allocation.Record_Date
\ttoColumn: Calendar.Date
''',encoding='utf-8')
(MODEL/'tables/Demand Scenario.tmdl').write_text('''table 'Demand Scenario'
\tcolumn 'Demand Change'
\t\tdataType: double
\t\tformatString: +0%;-0%;0%
\t\tsummarizeBy: none
\t\tsourceColumn: Demand Change

\tpartition 'Demand Scenario' = m
\t\tmode: import
\t\tsource = #table(type table [Demand Change=number],{{-0.1},{0},{0.1},{0.2}})
''',encoding='utf-8')

# Native Power BI visual definitions.
def field(name,table='Allocation',is_measure=True):
    return {('Measure' if is_measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
def m(name):return (name,'Allocation',True)
def c(name,table='Allocation'):return (name,table,False)
def projection(f):
    n,t,ismeasure=f
    return {'field':field(n,t,ismeasure),'queryRef':t+'.'+n,'nativeQueryRef':n,'displayName':n.replace('_',' ')}
pages=[]; visuals=[]
def visual(kind,x,y,w,h,title=None,roles=None,objects=None,sort=None):
    name=uid();z=len(visuals)+1
    v={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.3.0/schema.json','name':name,'position':{'x':x,'y':y,'z':z,'width':w,'height':h,'tabOrder':z},'visual':{'visualType':kind,'drillFilterOtherVisuals':True}}
    vo={'background':props(show=lit(True),color=color('#FFFFFF'),transparency=lit(0)),'border':props(show=lit(True),color=color(BORDER),radius=lit(8)),'visualHeader':props(show=lit(False))}
    if title:vo['title']=props(show=lit(True),text=lit(title),fontColor=color(INK),fontSize=lit(12),fontFamily=lit('Segoe UI Semibold'),titleWrap=lit(True))
    if roles:
        v['visual']['query']={'queryState':{role:{'projections':[projection(f) for f in fs]} for role,fs in roles.items()}}
        if sort:
            sf,di=sort;v['visual']['query']['sortDefinition']={'sort':[{'field':field(*sf),'direction':di}]}
    v['visual']['visualContainerObjects']=vo
    if objects:v['visual']['objects']=objects
    visuals.append(v);return v
def text(txt,x,y,w,h,size=12,col=INK,bg=None,bold=False):
    v=visual('textbox',x,y,w,h)
    v['visual']['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':txt,'textStyle':{'fontFamily':'Segoe UI Semibold' if bold else 'Segoe UI','fontSize':str(size)+'pt','color':col}}]}]}}]}
    v['visual']['visualContainerObjects']={'background':props(show=lit(bg is not None),color=color(bg or '#FFFFFF'),transparency=lit(0)),'border':props(show=lit(False)),'visualHeader':props(show=lit(False))}
    return v
def card(name,title,x,y,w=244,h=106,fmt=None):
    obj={'labels':props(color=color(TEAL),fontSize=lit(28),fontFamily=lit('Segoe UI Semibold'),labelDisplayUnits=lit(0 if fmt else 1000000000 if name in ['Allocated Budget','Actual Spend','Revenue','Operating Profit','Investment','Forecast Revenue','Attention Budget'] else 0),labelPrecision=lit(2 if name in ['Allocated Budget','Actual Spend','Revenue','Operating Profit','Investment','Forecast Revenue','Attention Budget'] else 1)),'categoryLabels':props(show=lit(False))}
    return visual('card',x,y,w,h,title,{'Values':[m(name)]},obj)
def chart(kind,title,x,y,w,h,cat,vals,series=None,sort=None):
    roles={'Category':[cat],'Y':[m(n) for n in vals]}
    if series:roles['Series']=[series]
    obj={'legend':props(show=lit(len(vals)>1 or series is not None),position=lit('Top'),fontSize=lit(10),labelColor=color(MUTED)),
         'categoryAxis':props(showAxisTitle=lit(False),fontSize=lit(10),labelColor=color(MUTED)),
         'valueAxis':props(showAxisTitle=lit(False),fontSize=lit(10),labelColor=color(MUTED),gridlineColor=color('#E8EEF3')),
         'labels':props(show=lit(kind in ['clusteredBarChart','clusteredColumnChart']),fontSize=lit(10),color=color(INK)),
         'dataPoint':props(defaultColor=color(TEAL))}
    return visual(kind,x,y,w,h,title,roles,obj,sort)
def table(title,x,y,w,h,fields,sort=None):
    return visual('tableEx',x,y,w,h,title,{'Values':fields},{'grid':props(gridVertical=lit(False),gridHorizontal=lit(True),gridHorizontalColor=color('#E8EEF3'),rowPadding=lit(7)),'columnHeaders':props(fontColor=color('#FFFFFF'),backColor=color(NAVY),fontSize=lit(10),wordWrap=lit(True)),'values':props(fontColorPrimary=color(INK),backColorPrimary=color('#FFFFFF'),backColorSecondary=color('#F3F7FA'),fontSize=lit(10),wordWrap=lit(False)),'total':props(totals=lit(False))},sort)
def slicer(name,label,x,y,w,table='Allocation',sync=True):
    v=visual('slicer',x,y,w,58,None,{'Values':[c(name,table)]},{'data':props(mode=lit('Dropdown')),'header':props(show=lit(True),text=lit(label),fontColor=color(MUTED),textSize=lit(10)),'items':props(fontColor=color(INK),textSize=lit(11)),'selection':props(selectAllCheckboxEnabled=lit(True),singleSelect=lit(False))})
    if sync:v['visual']['syncGroup']={'groupName':'Shared '+name,'fieldChanges':True,'filterChanges':True}
    return v
names=['01 Executive','02 Financial','03 Demand & Inventory','04 Workforce & Assets','05 Allocation Priorities']
ids=['9383f2eb13e59bb0918a','finance_team4','demand_team4','capacity_team4','priority_team4']
def start(i,title,subtitle):
    global visuals
    visuals=[]
    text('TEAM 4  /  ENTERPRISE ANALYTICS',24,14,720,25,11,'#74D2D3',NAVY,True)
    text(title,24,43,1300,42,25,'#FFFFFF',NAVY,True)
    text('GROUP 9226\n2024–2026',1400,23,170,57,11,'#C3D4E2',NAVY)
    for j,label in enumerate(['Overview','Financial value','Demand & inventory','People & assets','Allocation priorities']):
        v=text(f'{j+1:02}   {label}',24+j*314,100,300,38,12,'#FFFFFF' if i==j else INK,TEAL if i==j else '#E5EDF3',True)
        v['visual']['visualContainerObjects']['visualLink']=props(show=lit(True),type=lit('PageNavigation'),navigationSection=lit(ids[j]))
    text(subtitle,24,146,1552,27,11,MUTED)
    for name,label,x,w,t in [('Year','Year',24,170,'Calendar'),('Business_Unit','Business unit',206,352,'Allocation'),('Resource_Category','Resource',570,250,'Allocation'),('Scenario_Label','Scenario',832,360,'Allocation'),('Region','Region',1204,372,'Allocation')]:slicer(name,label,x,180,w,t)
    text('SYNTHETIC EDUCATIONAL DATA  •  USD  •  Select a chart to cross-filter; clear slicers with the eraser. Navigation: Ctrl+click in Desktop.',24,972,1550,22,9,MUTED)
def finish(i):
    p=DEF/'pages'/ids[i]
    page={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.2.0/schema.json','name':ids[i],'displayName':names[i],'displayOption':'FitToPage','height':1000,'width':1600,'objects':{'background':props(color=color(BG),transparency=lit(0))}}
    # Header background uses native shape, behind all other objects.
    v=visual('shape',0,0,1600,92,objects={'shape':props(tileShape=lit('rectangle')),'fill':props(show=lit(True),fillColor=color(NAVY),transparency=lit(0)),'outline':props(show=lit(False))})
    v['position']['z']=0;v['position']['tabOrder']=999
    v['visual']['visualContainerObjects']={'background':props(show=lit(False)),'border':props(show=lit(False)),'visualHeader':props(show=lit(False))}
    dump(p/'page.json',page)
    for v in visuals:dump(p/'visuals'/v['name']/'visual.json',v)
    pages.append((i,len(visuals)))
def cards(items):
    for j,(name,title) in enumerate(items):card(name,title,24+j*262,252,242,104)

start(0,'Resource allocation. Business performance.','A connected view of capital, service and capacity. Start with the portfolio, then investigate the drivers.')
cards([('Allocated Budget','Allocated budget'),('Actual Spend','Actual spend'),('Operating Profit','Operating profit'),('Mean ROI','Mean record ROI'),('Mean Resource Risk','Mean risk / 100'),('Reallocation Records','Reallocation records')])
chart('clusteredBarChart','Operating profit by business unit',24,374,754,272,c('Business_Unit'),['Operating Profit'],sort=(m('Operating Profit'),'Descending'))
chart('lineChart','Revenue and operating profit by month',796,374,780,272,c('Year Month','Calendar'),['Revenue','Operating Profit'],sort=(c('Year Month','Calendar'),'Ascending'))
chart('clusteredColumnChart','Spend and budget by resource',24,662,754,288,c('Resource_Category'),['Allocated Budget','Actual Spend'])
table('Portfolio scorecard — compare return, service and capacity',796,662,780,288,[c('Business_Unit'),m('Mean ROI'),m('Mean Order Fulfilment'),m('Workforce Utilization'),m('Equipment Utilization'),m('Attention Records')])
finish(0)

start(1,'Financial performance & investment value','Follow budget execution through profit and expected return. Portfolio ROI is investment-weighted; operating profit is not EBITDA.')
cards([('Revenue','Revenue'),('Operating Profit','Operating profit'),('Operating Margin','Operating margin'),('Budget Utilization','Budget utilization'),('Portfolio Expected ROI','Expected portfolio ROI'),('LTV to CAC','LTV / CAC')])
chart('clusteredBarChart','Allocated budget versus actual spend',24,374,754,272,c('Business_Unit'),['Allocated Budget','Actual Spend'])
chart('lineChart','Monthly profit and spending',796,374,780,272,c('Year Month','Calendar'),['Operating Profit','Actual Spend'],sort=(c('Year Month','Calendar'),'Ascending'))
visual('scatterChart',24,662,754,288,'Investment versus expected ROI — business units',{'Category':[c('Business_Unit')],'X':[m('Investment')],'Y':[m('Portfolio Expected ROI')],'Size':[m('Operating Profit')],'Tooltips':[m('Revenue'),m('Mean Resource Risk')]},{'categoryAxis':props(showAxisTitle=lit(True),axisTitle=lit('Investment (USD)')),'valueAxis':props(showAxisTitle=lit(True),axisTitle=lit('Expected portfolio ROI')),'dataPoint':props(defaultColor=color(TEAL)),'categoryLabels':props(show=lit(True))})
table('Product economics — ranked by operating profit',796,662,780,288,[c('Project_or_Product'),m('Revenue'),m('Operating Profit'),m('Operating Margin'),m('Mean ROI'),m('LTV to CAC')],sort=(m('Operating Profit'),'Descending'))
finish(1)

start(2,'Demand, inventory & service delivery','Compare supplied forecasts with demand, locate stockouts, and connect inventory availability to completed orders.')
cards([('Demand','Demand units'),('Inventory','Inventory units'),('Stockouts','Stockout units'),('Mean Forecast Accuracy','Mean forecast accuracy'),('Mean Inventory Service','Mean inventory service'),('Order Completion Rate','Order completion rate')])
chart('lineChart','Actual demand versus supplied forecast',24,374,754,272,c('Year Month','Calendar'),['Demand','Forecast Demand'],sort=(c('Year Month','Calendar'),'Ascending'))
chart('clusteredBarChart','Stockouts by business unit',796,374,780,272,c('Business_Unit'),['Stockouts'],sort=(m('Stockouts'),'Descending'))
chart('clusteredColumnChart','Completed and delayed orders by scenario',24,662,754,288,c('Scenario_Label'),['Orders Completed','Orders Delayed'])
table('Supply and forecast exceptions by business unit',796,662,780,288,[c('Business_Unit'),m('Demand'),m('Supply'),m('Stockouts'),m('Demand WAPE'),m('Mean Inventory Service'),m('Orders Delayed')],sort=(m('Stockouts'),'Descending'))
finish(2)

start(3,'Workforce, equipment & operating capacity','Utilization uses allocated / available hours. Capacity shortfall adds record-level gaps so surplus cannot hide a shortage.')
cards([('Workforce Utilization','Workforce utilization'),('Equipment Utilization','Equipment utilization'),('Unused Workforce Hours','Available workforce hours'),('Downtime Hours','Downtime hours'),('Mean Safety Compliance','Mean safety compliance'),('Capacity Shortfall','Capacity shortfall')])
chart('clusteredBarChart','Workforce and equipment utilization',24,374,754,272,c('Business_Unit'),['Workforce Utilization','Equipment Utilization'])
chart('lineChart','Downtime and training hours by month',796,374,780,272,c('Year Month','Calendar'),['Downtime Hours','Training Hours'],sort=(c('Year Month','Calendar'),'Ascending'))
chart('clusteredColumnChart','Capacity shortfall by business unit',24,662,754,288,c('Business_Unit'),['Capacity Shortfall'],sort=(m('Capacity Shortfall'),'Descending'))
table('Operating constraints and safety',796,662,780,288,[c('Business_Unit'),m('Downtime Hours'),m('Maintenance Cost'),m('Unused Equipment Hours'),m('Mean Safety Compliance'),m('Mean Order Fulfilment')],sort=(m('Downtime Hours'),'Descending'))
finish(3)

start(4,'Predictive view & allocation priorities','Supplied forecasts and decision labels • Illustrative demand scenario with fixed capacity • Recommendations require management review.')
cards([('Reallocation Records','Reallocation records'),('Review Records','Review records'),('Attention Budget','Budget flagged for attention'),('Mean Optimization Priority','Mean priority score / 100'),('Scenario Coverage','Scenario demand coverage'),('Scenario Capacity Gap','Scenario capacity gap')])
slicer('Demand Change','What-if demand change',24,374,260,'Demand Scenario',False)
text('Select −10%, 0%, +10% or +20%.\nDefault: 0%. Capacity stays fixed.\nThis is a sensitivity test, not a trained AI forecast.',24,443,260,112,11,MUTED)
chart('clusteredBarChart','Mean risk and priority by scenario',300,374,620,272,c('Scenario_Label'),['Mean Resource Risk','Mean Optimization Priority'],sort=(m('Mean Resource Risk'),'Descending'))
chart('clusteredColumnChart','Capacity gap under selected demand change',938,374,638,272,c('Business_Unit'),['Scenario Capacity Gap'])
v=table('Action queue — supplied Review / Reallocate labels, highest priority first',24,662,1198,288,[c('Record_ID'),c('Business_Unit'),c('Scenario_Label'),c('Decision_Status'),m('Mean Optimization Priority'),m('Mean Resource Risk'),m('Mean ROI'),m('Capacity Shortfall')],sort=(m('Mean Optimization Priority'),'Descending'))
v['filterConfig']={'filters':[{'name':uid(),'field':field('Decision_Status','Allocation',False),'type':'Categorical','filter':{'Version':2,'From':[{'Name':'a','Entity':'Allocation','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'a'}},'Property':'Decision_Status'}}],'Values':[[{'Literal':{'Value':"'Review'"}}],[{'Literal':{'Value':"'Reallocate'"}}]]}}}]}}]}
text('DECISION CHECKLIST',1240,674,318,36,12,TEAL,bold=True)
text('1  Confirm the shortage or constraint.\n\n2  Compare expected return and service.\n\n3  Check spare hours, skills and safety.\n\n4  Approve and monitor the change.\n\nRisk and priority are supplied scores; their original formulas were not provided.',1240,715,318,225,11,INK)
finish(4)

dump(DEF/'pages/pages.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':ids,'activePageName':ids[0]})
theme={'name':'Team4 Enterprise','dataColors':[TEAL,BLUE,GOLD,'#7B6EAE','#52AAA1','#BD6872'],'background':'#FFFFFF','foreground':INK,'tableAccent':TEAL,'good':TEAL,'neutral':GOLD,'bad':'#C65A61','textClasses':{'callout':{'fontFace':'Segoe UI Semibold','color':TEAL},'title':{'fontFace':'Segoe UI Semibold','color':INK,'fontSize':12},'header':{'fontFace':'Segoe UI Semibold','color':INK},'label':{'fontFace':'Segoe UI','color':MUTED,'fontSize':10}}}
dump(REPORT/'StaticResources/RegisteredResources/Team4Enterprise.json',theme)
report=json.loads((DEF/'report.json').read_text(encoding='utf-8-sig'))
report['themeCollection']['customTheme']={'name':'Team4Enterprise','reportVersionAtImport':'5.60','type':'RegisteredResources'}
report['resourcePackages']=[x for x in report.get('resourcePackages',[]) if x['name']!='RegisteredResources']+[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'Team4Enterprise','path':'Team4Enterprise.json','type':'CustomTheme'}]}]
dump(DEF/'report.json',report)
dump(WORK/'expected_kpis.json',{'records':len(rows),'budget':sum(float(r['Budget_Allocated_USD']) for r in rows),'spend':sum(float(r['Actual_Spend_USD']) for r in rows),'profit':sum(float(r['Operating_Profit_USD']) for r in rows),'mean_roi':sum(float(r['ROI_Pct']) for r in rows)/len(rows),'reallocate':sum(r['Decision_Status']=='Reallocate' for r in rows),'review':sum(r['Decision_Status']=='Review' for r in rows)})
print('Built',len(pages),'pages;',sum(n for _,n in pages),'native visuals;',len(measures),'measures')
