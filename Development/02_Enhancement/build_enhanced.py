import ast,json,uuid,shutil,re,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; WORK=Path(__file__).parent
REPORT=WORK/'Dashboard.Report'; DEF=REPORT/'definition'; MODEL=WORK/'Dashboard.SemanticModel'/'definition'
if not REPORT.exists():
 shutil.copytree(ROOT/'working/Team4.Report',REPORT)
 shutil.copytree(ROOT/'working/Team4.SemanticModel',WORK/'Dashboard.SemanticModel',ignore=shutil.ignore_patterns('.pbi'))
shutil.copytree(ROOT/'working/Team4.SemanticModel/definition',MODEL,dirs_exist_ok=True)
# Use only reusable visual helper functions, never execute the old build.
source=ast.parse((ROOT/'working/build_report.py').read_text(encoding='utf8'))
allowed=['dump','uid','lit','color','props','field','m','c','projection','visual','text','chart','table','slicer']
INK='#19344A'
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'helpers','exec'))
NAVY='#10283F';TEAL='#007F87';BLUE='#447DAD';GOLD='#B87815';RED='#B84646';INK='#19344A';MUTED='#536B7C';BG='#F0F4F6';BORDER='#DCE6EC'
# Replace only this task's generated report definitions, preserving the source project.
for d in [DEF/'pages',DEF/'bookmarks']:
 if d.exists():
  assert d.resolve().is_relative_to(WORK.resolve());shutil.rmtree(d)
dump(WORK/'Dashboard.pbip',{'version':'1.0','artifacts':[{'report':{'path':'Dashboard.Report'}}],'settings':{'enableAutoRecovery':True}})
dump(REPORT/'definition.pbir',{'version':'4.0','datasetReference':{'byPath':{'path':'../Dashboard.SemanticModel'}}})
base=(ROOT/'working/Team4.SemanticModel/definition/tables/Allocation.tmdl').read_text(encoding='utf-8-sig')
new=[]
def measure(n,e,fmt='#,0',folder='07 Decision intelligence',desc=''):
 new.append('\n\t/// '+(desc or n)+f"\n\tmeasure '{n}' = {e}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: {folder}\n")
pct='0.0%;(0.0%);0.0%';money='$#,0;($#,0);$0'
for n,e,fmt,desc in [
('Net Budget Variance','[Allocated Budget]-[Actual Spend]',money,'Positive = budget remaining; negative = overspend. Net totals can hide record exceptions.'),
('Overspend Amount','SUMX(Allocation,MAX(0,Allocation[Actual_Spend_USD]-Allocation[Budget_Allocated_USD]))',money,'Sum positive record overspend; not netted against underspend.'),
('Overspend Records','COUNTROWS(FILTER(Allocation,Allocation[Actual_Spend_USD]>Allocation[Budget_Allocated_USD]))','#,0','Records with spending greater than allocated budget.'),
('Negative ROI Records','COUNTROWS(FILTER(Allocation,Allocation[ROI_Pct]<0))','#,0','Supplied record ROI below zero.'),
('Order Delay Rate','DIVIDE([Orders Delayed],[Orders Completed]+[Orders Delayed])',pct,'Delayed / (completed + delayed); ratio of sums.'),
('Total Orders','[Orders Completed]+[Orders Delayed]','#,0','Completed plus delayed orders in selected observations.'),
('Shortage Rate','DIVIDE([Stockouts],[Demand])',pct,'Stockout units / actual demand units.'),
('Forecast Bias','DIVIDE([Forecast Demand]-[Demand],[Demand])',pct,'Positive = supplied forecast overestimates actual demand; signed summed error / actual demand.'),
('Mean Inventory Observation','AVERAGE(Allocation[Inventory_Units])','#,0.0','Mean inventory observation; not current stock on hand and not a three-year inventory total.'),
('Revenue per Record','DIVIDE([Revenue],[Records])',money,'Revenue / allocation observations. Controls population size, not changing portfolio mix.'),
('Demand per Record','DIVIDE([Demand],[Records])','#,0.0','Actual demand / observed records; not a continuous demand forecast.'),
('Forecast per Record','DIVIDE([Forecast Demand],[Records])','#,0.0','Supplied forecast / observed records, paired with actual demand.'),
('Downtime per Record','DIVIDE([Downtime Hours],[Records])','0.0','Downtime / allocation records; observations, not unique asset hours.'),
('Capacity Gap Rate','DIVIDE([Capacity Shortfall],[Service Demand])',pct,'Positive record-level gaps summed / total service demand.'),
('Shortage Records','COUNTROWS(FILTER(Allocation,Allocation[Service_Demand]>Allocation[Service_Capacity]))','#,0','Records with positive baseline service-capacity shortfall.'),
('Baseline Coverage','1-DIVIDE([Capacity Shortfall],[Service Demand])',pct,'Demand covered at each record, capped at demand, then aggregated.'),
('Gap Change','[Scenario Capacity Gap]-[Capacity Shortfall]','+#,0;-#,0;0','Selected demand scenario shortfall minus baseline shortfall; units.'),
('Coverage Change','([Scenario Coverage]-[Baseline Coverage])*100','+0.0" pp";-0.0" pp";0.0" pp"','Percentage-point difference from baseline coverage.'),
('Attention Share','DIVIDE([Attention Records],[Records])',pct,'Supplied Review/Reallocate count / selected record count.'),
('Attention Budget M','DIVIDE([Attention Budget],1000000)','$0.00"m"','Associated budget, not savings or an approved transfer amount.'),
('Demand Context','"Demand change: " & FORMAT([Selected Demand Change],"+0%;-0%;0%") & " | capacity held fixed"','', 'Sensitivity calculation; supplied labels and scores do not change.'),
('Context Label','IF(ISEMPTY(Allocation),"No matching observations",FORMAT([Records],"#,0") & " records | " & IF(ISFILTERED(Calendar[Year]),CONCATENATEX(VALUES(Calendar[Year]),Calendar[Year],", "),"2024-2026") & " | " & IF(HASONEVALUE(Allocation[Business_Unit]),SELECTEDVALUE(Allocation[Business_Unit]),FORMAT(DISTINCTCOUNT(Allocation[Business_Unit]),"0") & " business units"))','','Visible filter context; empty selections are explicitly identified.'),
('Executive Insight','IF(ISEMPTY(Allocation),"No records match these filters. Use Reset filters.",FORMAT([Attention Records],"#,0") & " supplied exceptions carry " & FORMAT([Attention Budget]/1000000,"$0.0") & "m of budget. " & FORMAT([Order Delay Rate],"0.0%") & " of orders are delayed; " & FORMAT([Capacity Shortfall],"#,0") & " service units lack record-level capacity. Investigate constraints before reallocating.")','','Filter-responsive evidence, not a recommendation of optimal allocations.'),
('Record Context','IF(HASONEVALUE(Allocation[Record_ID]),SELECTEDVALUE(Allocation[Record_ID]) & " | " & FORMAT(SELECTEDVALUE(Allocation[Record_Date]),"dd MMM yyyy") & " | " & SELECTEDVALUE(Allocation[Business_Unit]) & " | " & SELECTEDVALUE(Allocation[Project_or_Product]),"Select one record via drill-through")','','Inherited record identity, date, unit and initiative.'),
('Record Exception','IF(HASONEVALUE(Allocation[Record_ID]),"Supplied status: " & SELECTEDVALUE(Allocation[Decision_Status]) & ". " & IF([Capacity Shortfall]>0,"Capacity shortage; ","No baseline capacity shortage; ") & IF([Orders Delayed]>0,"delayed orders; ","") & IF([Net Budget Variance]<0,"overspending; ","") & IF([Portfolio Expected ROI]<0,"negative expected ROI; ","") & "Review timing, skills, location and approval constraints.","Drill through from an allocation ID to inspect the evidence.")','','Observed flags explain evidence; supplied status formula is undocumented.'),
('Gap Color','IF([Scenario Capacity Gap]>[Capacity Shortfall],"#B84646","#007F87")','','Semantic adverse/favorable color; numbers and labels remain primary.'),
('Variance Color','IF([Net Budget Variance]<0,"#B84646","#007F87")','','Negative budget remaining is adverse.'),
]:measure(n,e,fmt,desc=desc)
# Empty filter ratios remain BLANK rather than a misleading zero or 100%.
new=[s.replace("= 1-DIVIDE([Capacity Shortfall],[Service Demand])","= IF([Service Demand]>0,1-DIVIDE([Capacity Shortfall],[Service Demand]))") for s in new]
for n,e,fmt in [
('Test Records','COUNTROWS(Predictions)','#,0'),('Model MAE','AVERAGE(Predictions[Model_Absolute_Error])','0.00'),('Baseline MAE','AVERAGE(Predictions[Baseline_Absolute_Error])','0.00'),('Model RMSE','SQRT(AVERAGE(Predictions[Model_Squared_Error]))','0.00'),('Baseline RMSE','SQRT(AVERAGE(Predictions[Baseline_Squared_Error]))','0.00'),('Model WAPE','DIVIDE(SUM(Predictions[Model_Absolute_Error]),SUM(Predictions[Actual_Demand]))',pct),('Baseline WAPE','DIVIDE(SUM(Predictions[Baseline_Absolute_Error]),SUM(Predictions[Actual_Demand]))',pct),('MAE Difference','[Model MAE]-[Baseline MAE]','+0.00;-0.00;0.00'),('Model Bias','DIVIDE(SUM(Predictions[Model_Prediction])-SUM(Predictions[Actual_Demand]),SUM(Predictions[Actual_Demand]))',pct),('Model Finding','IF(ISEMPTY(Predictions),"No 2026 held-out records in this selection.",IF([Model MAE]<[Baseline MAE],"Ridge has lower MAE in this selection.","Historical unit baseline has lower MAE in this selection.") & " Full held-out test: ridge 113.96 vs baseline 113.42 units. No overall predictive improvement demonstrated.")','')]:measure(n,e,fmt,'08 Model evaluation','2026 held-out records only; filters do not retrain the model. Positive MAE difference is worse than baseline.')
base=base.replace('\tcolumn Record_ID',''.join(new)+'\n\tcolumn Record_ID',1)
base=re.sub(r'\n\t\tformatString: *\n','\n',base)
(MODEL/'tables/Allocation.tmdl').write_text(base,encoding='utf8')
# Parameterize sources once; retain imported data for portable saved-file inspection.
expr='expression SourceFolder = "'+str(ROOT).replace('\\','/')+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
(MODEL/'expressions.tmdl').write_text(expr,encoding='utf8')
base=base.replace('File.Contents("'+str(ROOT/'Group_9226_Team_4_Enterprise_Dataset.csv')+'")','File.Contents(SourceFolder & "/Group_9226_Team_4_Enterprise_Dataset.csv")')
(MODEL/'tables/Allocation.tmdl').write_text(base,encoding='utf8')
model=(MODEL/'model.tmdl').read_text();model+='\nref expression SourceFolder\nref table Predictions\n';(MODEL/'model.tmdl').write_text(model)
pcols=list(csv.DictReader((WORK/'Heldout_Predictions.csv').open()).fieldnames)
parts=['table Predictions']
for n in pcols:parts += [f'\tcolumn {n}', '\t\tdataType: '+('string' if n=='Record_ID' else 'double'),'\t\tsummarizeBy: none',f'\t\tsourceColumn: {n}','']
parts+=['\tpartition Predictions = m','\t\tmode: import','\t\tsource =','\t\t\tlet','\t\t\t    Source = Csv.Document(File.Contents(SourceFolder & "/working/enhancement/Heldout_Predictions.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),','\t\t\t    Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),','\t\t\t    Typed = Table.TransformColumnTypes(Headers,{'+','.join('{"'+n+'",'+('type text' if n=='Record_ID' else 'type number')+'}' for n in pcols)+'},"en-US")','\t\t\tin Typed']
(MODEL/'tables/Predictions.tmdl').write_text('\n'.join(parts))
with (MODEL/'relationships.tmdl').open('a') as f:f.write('\nrelationship '+str(uuid.uuid4())+'\n\tfromColumn: Predictions.Record_ID\n\ttoColumn: Allocation.Record_ID\n')
# Visual system: 1280 x 720, restrained navy rail, analytical teal and explicit exception colors.
ids=['executive','financial','service','capacity','priorities','model_evidence','unit_detail','record_detail','definitions']
names=['01 Portfolio','02 Financial','03 Demand & Service','04 Capacity','05 Priorities','06 Model Evidence','Business Unit Detail','Allocation Record Detail','KPI Definitions']
visuals=[]; allvisuals={}; current=0
old_visual=visual
def visual(*args,**kwargs):
 v=old_visual(*args,**kwargs);co=v['visual']['visualContainerObjects'];co['border']=props(show=lit(False));
 if 'title' in co:co['title'][0]['properties']['fontSize']=lit(13)
 return v
def txt(t,x,y,w,h,size=12,col=INK,bg=None,bold=False):return text(t,x,y,w,h,size,col,bg,bold)
def action(label,x,y,w,destination,typ='PageNavigation',active=False):
 v=txt(label,x,y,w,32,11,'#FFFFFF' if active else '#BED0DE',TEAL if active else NAVY,True)
 pp={'show':lit(True),'type':lit(typ)}
 if typ=='PageNavigation':pp['navigationSection']=lit(destination)
 elif typ=='Bookmark':pp['bookmark']=lit(destination)
 v['visual']['visualContainerObjects']['visualLink']=props(**pp);return v

def kpi(n,label,x,y,w=190,h=82,units=0,precision=1,accent=TEAL):
 v=visual('card',x,y,w,h,label,{'Values':[m(n)]},{'labels':props(color=color(accent),fontSize=lit(26),labelDisplayUnits=lit(units),labelPrecision=lit(precision),fontFamily=lit('Segoe UI Semibold')),'categoryLabels':props(show=lit(False))});return v

def narrative(n,x,y,w,h,size=15,bg='#E2F0F0'):
 v=kpi(n,None,x,y,w,h,precision=0);v['visual']['objects']['labels']=props(color=color(INK),fontSize=lit(size),wordWrap=lit(True));v['visual']['visualContainerObjects']['background']=props(show=lit(True),color=color(bg),transparency=lit(0));return v

def ch(kind,title,x,y,w,h,cat,vals,sort=None):
 v=chart(kind,title,x,y,w,h,cat,vals,sort=sort)
 o=v['visual']['objects'];o['labels']=props(show=lit(False),fontSize=lit(11));o['categoryAxis']=props(showAxisTitle=lit(False),fontSize=lit(11),labelColor=color(MUTED));o['valueAxis']=props(showAxisTitle=lit(False),fontSize=lit(11),labelColor=color(MUTED),gridlineColor=color('#E4EBEF'))
 o['dataPoint']=[{'selector':{'metadata':'Allocation.'+n},'properties':{'fill':color([TEAL,BLUE,GOLD][i%3])}} for i,n in enumerate(vals)]
 v['visual']['query']['queryState']['Tooltips']={'projections':[projection(m('Records'))]}
 return v
aliases={'Business_Unit':'Business unit','Project_or_Product':'Initiative','Record_ID':'Record','Decision_Status':'Status','Scenario_Label':'Scenario','Portfolio Expected ROI':'Exp. ROI','Operating Profit':'Profit','Operating Margin':'Margin','Order Delay Rate':'Delay %','Order Completion Rate':'Complete %','Capacity Gap Rate':'Gap %','Mean Optimization Priority':'Priority','Mean Resource Risk':'Risk','Scenario Capacity Gap':'Selected gap','Capacity Shortfall':'Base gap','Net Budget Variance':'Remaining','Attention Records':'Attention','Workforce Utilization':'Workforce %','Equipment Utilization':'Equipment %','Total Orders':'Orders','Shortage Rate':'Shortage %','Mean Safety Compliance':'Safety %'}
def tab(title,x,y,w,h,fields,sort=None,widths=None):
 v=table(title,x,y,w,h,fields,sort);o=v['visual']['objects'];o['grid']=props(gridVertical=lit(False),gridHorizontal=lit(False),rowPadding=lit(7));o['columnHeaders']=props(fontColor=color('#FFFFFF'),backColor=color(NAVY),fontSize=lit(11),wordWrap=lit(True),autoSizeColumnWidth=lit(False));o['values']=props(fontColorPrimary=color(INK),backColorPrimary=color('#FFFFFF'),backColorSecondary=color('#F3F7FA'),fontSize=lit(11),wordWrap=lit(False))
 ps=v['visual']['query']['queryState']['Values']['projections'];ws=widths or [180]+[(w-202)/(len(ps)-1)]*(len(ps)-1)
 o['columnWidth']=[{'selector':{'metadata':p['queryRef']},'properties':{'value':lit(ws[i])}} for i,p in enumerate(ps)]
 for p in ps:p['displayName']=aliases.get(p['nativeQueryRef'],p['nativeQueryRef'].replace('_',' '))
 return v

def start(i,title,question,filters=True):
 global visuals,current
 visuals=[];current=i
 txt('',0,0,1280,91,10,bg=NAVY)
 txt('TEAM 4  /  RESOURCE INTELLIGENCE',20,8,900,23,10,'#70CBD0',bold=True)
 txt(title,20,31,1030,40,23,'#FFFFFF',bold=True)
 for j,l in enumerate(['PORTFOLIO','FINANCIAL','DEMAND / SERVICE','CAPACITY','PRIORITIES','MODEL EVIDENCE']):action(l,20+j*177,79,169,ids[j],active=i==j)
 action('RESET FILTERS',1100,32,160,'reset_all','Bookmark')
 txt(question,20,115,1240,30,13,INK,bold=True)
 if filters:
  for n,label,x,w,t in [('Year','Year',20,155,'Calendar'),('Business_Unit','Business unit',185,290,'Allocation'),('Scenario_Label','Operating scenario',485,285,'Allocation'),('Region','Region',780,255,'Allocation')]:slicer(n,label,x,150,w,t)
  action('KPI GUIDE',1045,164,215,'definitions')
  narrative('Context Label',20,207,1240,28,11,'#F0F4F6')
 txt('SYNTHETIC EDUCATIONAL DATA  |  USD  |  Right-click a business unit or record to drill through. Desktop actions: Ctrl+click.',20,694,1238,24,9,MUTED)

def finish(i,drill=None,tooltip=False):
 p=DEF/'pages'/ids[i];page={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.2.0/schema.json','name':ids[i],'displayName':names[i],'displayOption':'FitToPage','width':1280,'height':720,'objects':{'background':props(color=color(BG),transparency=lit(0))}}
 if i>=6:page['visibility']='HiddenInViewMode'
 if drill:
  fn=ids[i]+'_filter';page['filterConfig']={'filters':[{'name':fn,'field':field(drill,'Allocation',False),'type':'Categorical','howCreated':'Drillthrough'}]}
  page['pageBinding']={'name':ids[i]+'_binding','type':'Drillthrough','acceptsFilterContext':'Default','parameters':[{'name':ids[i]+'_param','boundFilter':fn,'fieldExpr':field(drill,'Allocation',False)}]}
 if tooltip:page['pageBinding']={'name':'definitions_binding','type':'Tooltip'}
 # Explicit filtering rather than ambiguous highlighting between analytic visuals.
 sources=[v for v in visuals if v['visual']['visualType'] in ['clusteredBarChart','clusteredColumnChart','scatterChart','tableEx']]
 targets=[v for v in visuals if 'query' in v['visual'] and v['visual']['visualType']!='slicer']
 page['visualInteractions']=[{'source':a['name'],'target':b['name'],'type':'DataFilter'} for a in sources for b in targets if a!=b]
 for v in visuals:
  if v['visual']['visualType']=='card' and i<6:
   v['visual']['visualContainerObjects']['visualTooltip']=props(show=lit(True),type=lit('ReportPage'),section=lit('definitions'))
 dump(p/'page.json',page)
 for v in visuals:dump(p/'visuals'/v['name']/'visual.json',v)
 allvisuals[ids[i]]=visuals

def status_filter(v):
 v['filterConfig']={'filters':[{'name':uid(),'field':field('Decision_Status','Allocation',False),'type':'Categorical','filter':{'Version':2,'From':[{'Name':'a','Entity':'Allocation','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'a'}},'Property':'Decision_Status'}}],'Values':[[{'Literal':{'Value':"'Review'"}}],[{'Literal':{'Value':"'Reallocate'"}}]]}}}]}}]}

start(0,'Executive resource portfolio','Where should management focus attention, and why?')
kpi('Operating Profit','Operating profit',20,242,240,100,1e9,2)
kpi('Budget Utilization','Budget execution',270,242,195,100)
kpi('Portfolio Expected ROI','Weighted expected ROI',475,242,245,100)
kpi('Order Delay Rate','Orders delayed',730,242,195,100,accent=GOLD)
kpi('Attention Budget M','Associated attention budget',935,242,325,100,precision=2,accent=GOLD)
narrative('Executive Insight',20,354,400,176,16)
txt('MANAGEMENT ROUTE\nInvestigate the unit, then the allocation.\nValidate timing and feasibility before approving any transfer. Associated budget is not savings.',20,540,400,141,13,INK,'#E2F0F0')
tab('Portfolio trade-offs | right-click a unit to investigate',436,354,824,235,[c('Business_Unit'),m('Portfolio Expected ROI'),m('Order Delay Rate'),m('Capacity Gap Rate'),m('Attention Records')],sort=(m('Attention Records'),'Descending'),widths=[220,135,130,130,150])
kpi('Allocated Budget','Allocated budget',436,601,260,80,1e9,2);kpi('Capacity Shortfall','Uncovered service units',708,601,270,80,1000,1,accent=GOLD);kpi('Attention Records','Review / Reallocate records',990,601,270,80,precision=0)
finish(0)

start(1,'Financial performance & capital allocation','Which allocations create value, and where is capital exposed?')
for j,(n,l) in enumerate([('Revenue','Revenue'),('Operating Profit','Operating profit'),('Operating Margin','Operating margin'),('Portfolio Expected ROI','Weighted expected ROI'),('Net Budget Variance','Budget remaining')]):kpi(n,l,20+j*250,242,240,82,1e9 if j<2 else 1e6 if j==4 else 0,2)
ch('clusteredBarChart','Budget remaining by unit | negative = overspend',20,337,400,243,c('Business_Unit'),['Net Budget Variance'],(m('Net Budget Variance'),'Ascending'))
v=visual('scatterChart',433,337,390,243,'Investment vs expected ROI',{'Category':[c('Business_Unit')],'X':[m('Investment')],'Y':[m('Portfolio Expected ROI')],'Size':[m('Records')],'Tooltips':[m('Operating Profit'),m('Records')]},{'categoryAxis':props(showAxisTitle=lit(False),fontSize=lit(11)),'valueAxis':props(showAxisTitle=lit(False),fontSize=lit(11)),'dataPoint':props(defaultColor=color(TEAL)),'categoryLabels':props(show=lit(False))})
kpi('Overspend Amount','Gross record overspend',838,337,205,95,1e6,2,RED);kpi('Overspend Records','Overspending records',1055,337,205,95,precision=0,accent=RED)
kpi('Negative ROI Records','Negative supplied ROI records',838,445,422,95,precision=0,accent=RED)
txt('Net remaining budget can conceal gross overspend.\nBubble size = observed records; hover for unit.',838,546,422,46,11,MUTED)
tab('Initiative economics | totals across selected observations; ranked by profit',20,594,1240,90,[c('Project_or_Product'),m('Revenue'),m('Operating Profit'),m('Operating Margin'),m('Portfolio Expected ROI')],(m('Operating Profit'),'Descending'),[270,240,240,220,240])
finish(1)

start(2,'Demand, inventory & service','Where do supply mismatches affect service, relative to the volume at risk?')
for j,(n,l) in enumerate([('Demand WAPE','Supplied forecast WAPE'),('Forecast Bias','Forecast bias (+ over)'),('Shortage Rate','Stockouts / demand'),('Order Delay Rate','Delayed / total orders'),('Mean Inventory Observation','Mean inventory observation')]):kpi(n,l,20+j*250,242,240,82,precision=1)
ch('lineChart','Demand & supplied forecast per record | monthly',20,337,610,220,c('Year Month','Calendar'),['Demand per Record','Forecast per Record'],(c('Year Month','Calendar'),'Ascending'))
ch('clusteredBarChart','Order-delay rate by operating scenario',646,337,614,220,c('Scenario_Label'),['Order Delay Rate'],(m('Order Delay Rate'),'Descending'))
tab('Service severity and volume | compare rates alongside populations',20,570,970,113,[c('Scenario_Label'),m('Records'),m('Total Orders'),m('Order Delay Rate'),m('Stockouts'),m('Shortage Rate')],(m('Order Delay Rate'),'Descending'),[215,95,155,150,155,155])
txt('INTERPRETATION\nInventory is an observation mean, not current stock. WAPE is error magnitude; bias is signed error. Dates are irregular.',1005,570,255,113,11,MUTED,'#E2F0F0')
finish(2)

start(3,'Workforce, equipment & capacity','Where are usable capacity and service demand misaligned?')
for j,(n,l) in enumerate([('Workforce Utilization','Weighted workforce use'),('Equipment Utilization','Weighted equipment use'),('Unused Workforce Hours','Unused workforce hours'),('Unused Equipment Hours','Unused equipment hours'),('Shortage Records','Records with capacity gaps')]):kpi(n,l,20+j*250,242,240,82,1000 if j in [2,3] else 0,0 if j==4 else 1)
ch('clusteredBarChart','Allocated / available hours by business unit',20,337,610,230,c('Business_Unit'),['Workforce Utilization','Equipment Utilization'])
ch('clusteredColumnChart','Service gap / service demand by business unit',646,337,614,230,c('Business_Unit'),['Capacity Gap Rate'])
tab('Constraint evidence | right-click a business unit for records',20,580,900,104,[c('Business_Unit'),m('Downtime per Record'),m('Maintenance Cost'),m('Mean Safety Compliance')],None,[235,210,210,210])
txt('REDEPLOYMENT CHECK\nUnused hours cannot automatically move across dates, skills, locations or assets. Confirm safety, maintenance and approvals first.',935,580,325,104,11,MUTED,'#E2F0F0')
finish(3)

start(4,'Allocation priorities & demand sensitivity','Which exceptions need review, and how does demand change capacity pressure?')
for j,(n,l) in enumerate([('Review Records','Supplied Review'),('Reallocation Records','Supplied Reallocate'),('Attention Budget M','Associated attention budget'),('Scenario Capacity Gap','Selected-scenario gap'),('Gap Change','Gap change vs baseline')]):kpi(n,l,20+j*250,242,240,82,1000 if j in [3,4] else 0,2 if j==2 else 1 if j in [3,4] else 0, GOLD if j in [3,4] else TEAL)
slicer('Demand Change','Demand change (single choice)',20,337,280,'Demand Scenario',False)['visual']['objects']['selection']=props(singleSelect=lit(True),selectAllCheckboxEnabled=lit(False))
kpi('Baseline Coverage','Baseline coverage',20,410,280,83);kpi('Scenario Coverage','Selected coverage',20,506,280,83)
txt('Fixed capacity. Record-level gaps.\nScores and statuses stay supplied.\nNo optimal allocation is claimed.',20,600,280,82,12,MUTED)
ch('clusteredBarChart','Baseline and selected capacity shortfall | units',316,337,944,194,c('Business_Unit'),['Capacity Shortfall','Scenario Capacity Gap'])
v=tab('Top supplied priorities | attention queue; full records through unit drill-through',316,544,944,139,[c('Record_ID'),c('Business_Unit'),c('Decision_Status'),m('Mean Optimization Priority'),m('Capacity Shortfall'),m('Scenario Capacity Gap')],(m('Mean Optimization Priority'),'Descending'),[130,220,120,115,155,170]);status_filter(v)
finish(4)

start(5,'Model evidence | demand regression','Does a leakage-aware model improve demand estimates beyond a historical unit baseline?')
for j,(n,l) in enumerate([('Test Records','Held-out records (2026)'),('Model MAE','Ridge MAE | units'),('Baseline MAE','Baseline MAE | units'),('Model WAPE','Ridge WAPE'),('MAE Difference','MAE difference (+ worse)')]):kpi(n,l,20+j*250,242,240,82,precision=0 if j==0 else 2,accent=RED if j==4 else TEAL)
narrative('Model Finding',20,337,1240,74,15)
ch('clusteredBarChart','Held-out MAE by business unit | lower is better',20,425,610,250,c('Business_Unit'),['Model MAE','Baseline MAE'])
txt('EVALUATION DESIGN\nTrain 2024: 2,004 records. Tune on 2025: 2,000.\nRefit 2024-25; held-out 2026: 996. Ridge penalty = 1.\nBaseline: training-window business-unit mean.\n\nINPUTS & LIMITS\nOnly unit, region, initiative and scheduled month.\nPlanning-time availability is assumed, not logged.\nNo outcomes, supplied forecasts, scores or IDs used.\nSynthetic, irregular observations; no deployment claim.\nFilters inspect errors; they do not retrain the model.',646,425,614,250,13,INK,'#E2F0F0')
finish(5)

start(6,'Business-unit investigation','Inherited filters identify the selected business unit and its observations.',False)
action('BACK',20,155,160,'','Back');narrative('Context Label',190,150,1070,52,13)
for j,(n,l) in enumerate([('Records','Records'),('Revenue per Record','Revenue / record'),('Order Delay Rate','Order-delay rate'),('Capacity Shortfall','Capacity shortfall'),('Attention Records','Supplied attention records')]):kpi(n,l,20+j*250,215,240,82,1000 if j==3 else 0,1)
ch('lineChart','Revenue per record by year | populations differ',20,310,610,190,c('Year','Calendar'),['Revenue per Record'],(c('Year','Calendar'),'Ascending'))
tab('Year populations | not YTD; no annualization',646,310,614,190,[c('Year','Calendar'),m('Records'),m('Revenue per Record'),m('Downtime per Record')],(c('Year','Calendar'),'Ascending'),[110,100,200,180])
tab('Full allocation detail | scroll/search filters; right-click a Record for investigation',20,515,1240,168,[c('Record_ID'),c('Record_Date'),c('Project_or_Product'),c('Decision_Status'),m('Mean Optimization Priority'),m('Capacity Shortfall'),m('Scenario Capacity Gap')],(m('Mean Optimization Priority'),'Descending'),[130,150,260,140,130,190,190])
finish(6,'Business_Unit')

start(7,'Allocation-record evidence','Verify the economic and operational evidence before any management action.',False)
action('BACK',20,155,160,'','Back');narrative('Record Context',190,150,1070,55,13)
for j,(n,l) in enumerate([('Allocated Budget','Budget'),('Actual Spend','Spend'),('Net Budget Variance','Budget remaining'),('Investment','Investment'),('Portfolio Expected ROI','Expected ROI')]):kpi(n,l,20+j*250,218,240,82,1000 if j<4 else 0,1)
tab('Demand and service evidence',20,315,610,103,[m('Demand'),m('Supply'),m('Stockouts'),m('Orders Completed'),m('Orders Delayed')],None,[110,110,110,140,115])
tab('Hours and capacity evidence',646,315,614,103,[m('Workforce Available'),m('Workforce Allocated'),m('Equipment Available'),m('Equipment Allocated')],None,[145,145,145,150])
tab('Inherited context and supplied decision',20,435,1240,98,[c('Resource_ID'),c('Resource_Category'),c('Scenario_Label'),c('Decision_Status'),m('Mean Resource Risk'),m('Mean Optimization Priority')],None,[180,180,240,180,190,230])
kpi('Capacity Shortfall','Baseline capacity gap',20,548,260,82);kpi('Scenario Capacity Gap','Selected-scenario gap',292,548,260,82);kpi('Operating Profit','Operating profit',564,548,260,82,1000,1);kpi('Expected Return','Expected return',836,548,424,82,1000,1)
narrative('Record Exception',20,642,1240,45,12)
finish(7,'Record_ID')

start(8,'Definitions, denominators & limitations','Metric guide | interpretation is part of the decision.',False)
action('BACK',20,152,160,'','Back')
txt('FINANCE\nBudget execution = spend / allocated budget.\nOperating margin = operating profit / revenue; not EBITDA.\nExpected ROI = (expected return - investment) / investment.\nMean record ROI is unweighted and separately labeled.\nAttention budget is associated budget, not savings.\n\nDEMAND & SERVICE\nCompletion = completed / (completed + delayed).\nWAPE = sum absolute record errors / actual demand.\nBias = (forecast - actual demand) / actual demand.\nShortage rate = stockout units / actual demand.\nMean inventory observation is not current on-hand stock.',20,200,610,370,14,INK,'#FFFFFF')
txt('CAPACITY & SCENARIOS\nUtilization = allocated hours / available hours.\nGap = sum positive record demand-minus-capacity gaps.\nCoverage = record-capped supply / total service demand.\nDemand changes; capacity stays fixed. No gap netting.\nUnused equipment and workforce hours are separate.\n\nEVIDENCE LIMITS\n2024: 2,004; 2025: 2,000; 2026: 996 observations.\nPer-record measures control size, not changing mix.\nOne resource category per business unit; no duplicate filter.\nZero denominators return blank (not applicable).\nSynthetic results do not establish real-world causation.',646,200,614,370,14,INK,'#FFFFFF')
txt('AI DISCLOSURE  |  Codex assisted with model code, DAX, report construction and documentation. The project team retains responsibility for final analytical judgement. The ridge experiment is separate from supplied forecasts and sensitivity calculations.',20,588,1240,91,13,MUTED,'#E2F0F0')
finish(8,tooltip=True)

# Reset captures every shared slicer and clears chart selections; keeps the current page.
sections={}
for pid,vs in allvisuals.items():
 sections[pid]={'visualContainers':{v['name']:{'singleVisual':{'visualType':v['visual']['visualType'],'objects':{'merge':{'general':[{'properties':{'filter':None}}]}}}} for v in vs if v['visual']['visualType']=='slicer'}}
dump(DEF/'bookmarks/reset_all.bookmark.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/1.0.0/schema.json','name':'reset_all','displayName':'Reset filters','options':{'suppressActiveSection':True,'suppressDisplay':True},'explorationState':{'version':'1.0','activeSection':ids[0],'sections':sections}})
dump(DEF/'bookmarks/bookmarks.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json','items':[{'name':'reset_all'}]})
dump(DEF/'pages/pages.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':ids,'activePageName':ids[0]})
print('Enhanced project generated:',sum(map(len,allvisuals.values())),'native visuals;',len(new),'additional measures')

# Compatibility normalization for installed Power BI Desktop.
for fp in (MODEL/'tables').glob('*.tmdl'):
 s=fp.read_text(encoding='utf-8-sig').replace('SourceFolder & "','"'+str(ROOT).replace(chr(92),'/'))
 s=re.sub(r'\n\t\tformatString: *\n','\n',s)
 fp.write_text(s,encoding='utf8')
ep=MODEL/'expressions.tmdl'
if ep.exists():ep.rename(WORK/'SourceFolder.tmdl.reference')
mp=MODEL/'model.tmdl';mp.write_text(mp.read_text().replace('ref expression SourceFolder\n',''))
