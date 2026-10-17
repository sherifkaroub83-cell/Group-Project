import json,re
from pathlib import Path
W=Path(__file__).parent
R=W/'Dashboard.Report/definition/pages'
M=W/'Dashboard.SemanticModel/definition'
def lit(v):return {'expr':{'Literal':{'Value':str(v)+'D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
def field(n):return {'Measure':{'Expression':{'SourceRef':{'Entity':'Allocation'}},'Property':n}}
a=M/'tables/Allocation.tmdl'
s=a.read_text(encoding='utf-8-sig')
s=re.sub(r'\n\t\tformatString: *\n','\n',s)
for name,col,metric in [('Top Initiative','Project_or_Product','Operating Profit'),('Top Attention','Record_ID','Mean Optimization Priority')]:
 if "measure '"+name+"'" not in s:
  expr='VAR SelectedItems = ALLSELECTED(Allocation['+col+']) VAR TopItems = TOPN(5, SelectedItems, ['+metric+'], DESC, Allocation['+col+'], ASC) RETURN IF(CONTAINS(TopItems, Allocation['+col+'], SELECTEDVALUE(Allocation['+col+'])),1,0)'
  s+="\n\tmeasure '"+name+"' = "+expr+"\n\t\tformatString: 0\n\t\tdisplayFolder: 09 Presentation\n"
a.write_text(s,encoding='utf8')
for folder in R.iterdir():
 if not folder.is_dir():continue
 for f in folder.glob('visuals/*/visual.json'):
  v=json.loads(f.read_text());p=v['position'];vis=v['visual'];k=vis['visualType'];o=vis.get('objects',{});co=vis.get('visualContainerObjects',{})
  if k=='tableEx':
   o['grid'][0]['properties']['rowPadding']=lit(2)
   o['columnHeaders'][0]['properties']['fontSize']=lit(10)
   o['values'][0]['properties']['fontSize']=lit(10)
  if folder.name in ['service','capacity']:
   if k in ['lineChart','clusteredBarChart','clusteredColumnChart']:p['height']=155
   if k=='tableEx':p['y']=505;p['height']=180
   if k=='textbox' and p['y'] in [570,580]:p['y']=505;p['height']=180
  if folder.name=='financial':
   if k in ['clusteredBarChart','scatterChart']:p['height']=155
   if k=='tableEx':p['y']=505;p['height']=180
   if k=='card' and p['y']==337:p['height']=75
   if k=='card' and p['y']==445:p['y']=420;p['height']=72
   if k=='textbox' and p['y'] in [546,686]:
    vis['objects']['general'][0]['properties']['paragraphs']=[{'textRuns':[{'value':'Net totals can hide record overspend. Bubble size = records.','textStyle':{'fontSize':'10pt','color':'#536B7C'}}]}]
    p.update(x=838,y=478,width=422,height=25)
  if folder.name=='priorities':
   if k=='clusteredBarChart':p['height']=150
   if k=='tableEx':p['y']=500;p['height']=185
  if k=='tableEx' and folder.name in ['financial','priorities']:
   measure='Top Initiative' if folder.name=='financial' else 'Top Attention'
   fl={'name':'top_five','field':field(measure),'type':'Advanced','filter':{'Version':2,'From':[{'Name':'a','Entity':'Allocation','Type':0}],'Where':[{'Condition':{'Comparison':{'ComparisonKind':0,'Left':{'Measure':{'Expression':{'SourceRef':{'Source':'a'}},'Property':measure}},'Right':{'Literal':{'Value':'1L'}}}}}]}}
   filters=v.setdefault('filterConfig',{}).setdefault('filters',[]);filters[:]=[x for x in filters if x['name']!='top_five'];filters.append(fl)
   co['title'][0]['properties']['text']=lit('Top 5 initiatives by profit | selected observations' if folder.name=='financial' else 'Top 5 supplied priorities | selected attention records')
  if folder.name=='record_detail' and k=='tableEx':
   if p['y']==315:p['height']=115
   if p['y']==435:p['height']=107
  if k=='tableEx':
   widths=o.get('columnWidth',[])
   total=sum(float(x['properties']['value']['expr']['Literal']['Value'].rstrip('DL')) for x in widths)
   if total>p['width']-35:
    for x in widths:x['properties']['value']=lit(round(float(x['properties']['value']['expr']['Literal']['Value'].rstrip('DL'))*(p['width']-35)/total,1))
  f.write_text(json.dumps(v,indent=2))
# Open at the unfiltered executive view.
p=R/'pages.json';d=json.loads(p.read_text());d['activePageName']='executive';p.write_text(json.dumps(d,indent=2))
print('Applied compact tables, responsive top-five summaries and record panel sizing.')

# Native text boxes need enough line height to avoid internal scroll bars.
for folder in R.iterdir():
 if not folder.is_dir():continue
 for f in folder.glob('visuals/*/visual.json'):
  v=json.loads(f.read_text());p=v['position'];vis=v['visual'];k=vis['visualType'];o=vis.get('objects',{})
  if k=='textbox':
   if p['y']==8:p.update(y=0,height=34)
   elif p['y']==31:p.update(y=25,height=51)
   elif p['y']==79:p.update(y=75,height=39)
   elif p['y']==32:p.update(y=25,height=42)
   elif p['y']==115:p.update(y=110,height=39)
   elif p['y']==164:p.update(y=158,height=42)
   elif p['y']==694:p.update(y=685,height=35)
   elif p['y']==478:p.update(y=472,height=32)
  if folder.name in ['financial','service','capacity']:
   if k in ['lineChart','clusteredBarChart','clusteredColumnChart','scatterChart']:
    p['height']=185
    ca=o.setdefault('categoryAxis',[{'properties':{}}])[0]['properties'];ca['fontSize']=lit(10);ca['minimumCategoryWidth']=lit(12);ca['maxMarginFactor']=lit(45)
   if k=='tableEx':p.update(y=532,height=153)
   if k=='textbox' and p['y']==505:p.update(y=532,height=153)
  if folder.name=='priorities' and k=='clusteredBarChart':
   p['height']=153
   o.setdefault('categoryAxis',[{'properties':{}}])[0]['properties'].update(minimumCategoryWidth=lit(10),fontSize=lit(10))
  if folder.name=='service' and k=='lineChart':
   v=json.loads(json.dumps(v).replace('Year Month','Date'))
   v['visual']['objects']['categoryAxis'][0]['properties']['axisType']=lit('Scalar')
   v['visual']['visualContainerObjects']['title'][0]['properties']['text']=lit('Demand & supplied forecast per record | observed dates')
  f.write_text(json.dumps(v,indent=2))
print('Expanded text lines; continuous-date trend; compact category bands.')

# Fit every summary row while reserving sufficient chart space.
a=M/'tables/Allocation.tmdl';s=a.read_text()
s=re.sub(r"(measure 'Top Attention' = ).*",r"\1VAR TopItems = TOPN(5, ALLSELECTED(Allocation), Allocation[Optimization_Priority_Score], DESC, Allocation[Record_ID], ASC) RETURN IF(CONTAINS(TopItems, Allocation[Record_ID], SELECTEDVALUE(Allocation[Record_ID])),1,0)",s)
a.write_text(s)
for folder in R.iterdir():
 if not folder.is_dir():continue
 for f in folder.glob('visuals/*/visual.json'):
  v=json.loads(f.read_text());p=v['position'];vis=v['visual'];k=vis['visualType'];o=vis.get('objects',{})
  if folder.name in ['financial','service','capacity','priorities']:
   if k=='card' and p['y']==242:p['height']=74
   if k in ['lineChart','clusteredBarChart','clusteredColumnChart','scatterChart']:
    p.update(y=322,height=174)
    if k=='clusteredBarChart' and folder.name in ['capacity','priorities']:vis['visualType']='clusteredColumnChart'
   if k=='tableEx':p.update(y=505,height=180)
   if k=='textbox' and p['y']==532:p.update(y=505,height=180)
  if k=='slicer':
   # Restore default data selection while keeping source binding.
   for x in o.get('general',[]):x.get('properties',{}).pop('filter',None)
  f.write_text(json.dumps(v,indent=2))
print('Corrected global attention ranking; all summary rows and categories fit.')
