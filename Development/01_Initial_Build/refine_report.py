import json
from pathlib import Path
R=Path(__file__).resolve().parent/'Team4.Report'/'definition'
def lit(v):return {'expr':{'Literal':{'Value':('true' if v else 'false') if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
def color(v):return {'solid':{'color':lit(v)}}
def prop(**kw):return [{'properties':kw}]
aliases={'Business_Unit':'Business unit','Project_or_Product':'Product / initiative','Scenario_Label':'Scenario','Decision_Status':'Decision','Record_ID':'Record','Mean ROI':'ROI','Mean Order Fulfilment':'Fulfilment','Workforce Utilization':'Workforce %','Equipment Utilization':'Equipment %','Attention Records':'Attention','Operating Profit':'Profit','Operating Margin':'Margin','Mean Inventory Service':'Service %','Orders Delayed':'Delayed','Demand WAPE':'WAPE','Downtime Hours':'Downtime (h)','Maintenance Cost':'Maintenance','Unused Equipment Hours':'Spare hours','Mean Safety Compliance':'Safety %','Mean Optimization Priority':'Priority','Mean Resource Risk':'Risk','Capacity Shortfall':'Capacity gap','Allocated Budget':'Budget','Actual Spend':'Spend','Forecast Demand':'Forecast','Orders Completed':'Completed','Scenario Capacity Gap':'Scenario gap'}
for f in R.glob('pages/*/visuals/*/visual.json'):
 d=json.loads(f.read_text(encoding='utf-8-sig'));v=d['visual'];p=d['position'];o=v.setdefault('objects',{});co=v.setdefault('visualContainerObjects',{})
 kind=v['visualType']
 if kind=='shape' and p['z']==0:
  v['visualType']='textbox';v['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':'','textStyle':{'fontSize':'10pt'}}]}]}}]}
  co['background']=prop(show=lit(True),color=color('#112B45'),transparency=lit(0));co['border']=prop(show=lit(False))
 if kind=='textbox':
  if p['y']==14:p['height']=34;p['y']=8
  if p['y']==43:p['height']=54;p['y']=34
  if p['y']==146:p['height']=34;p['y']=142
  if p['y']==972:p['height']=30;p['y']=966
  if p['y']<92:co['background']=prop(show=lit(False))
  for obj in o.get('general',[]):
   for para in obj.get('properties',{}).get('paragraphs',[]):
    para['horizontalTextAlignment']='left'
    for run in para.get('textRuns',[]):
     if p['y']==34:run.setdefault('textStyle',{})['fontSize']='24pt'
 if kind in ['clusteredBarChart','clusteredColumnChart','lineChart']:
  ys=v.get('query',{}).get('queryState',{}).get('Y',{}).get('projections',[])
  palette=['#008C95','#407DB0','#D89836']
  if len(ys)>1:
   o['dataPoint']=[{'selector':{'metadata':s['queryRef']},'properties':{'fill':color(palette[i%3])}} for i,s in enumerate(ys)]
  for key in ['categoryAxis','valueAxis']:
   o.setdefault(key,prop())[0]['properties']['fontSize']=lit(11)
  if kind=='lineChart':
   o['lineStyles']=prop(strokeWidth=lit(2.5))
 if kind=='tableEx':
  ps=v['query']['queryState']['Values']['projections']
  for pp in ps:
   n=next(iter(pp['field'].values()))['Property'];pp['displayName']=aliases.get(n,n.replace('_',' '))
  widths=[]
  if p['width']<800:
   first=174
   rest=(p['width']-first-26)/(len(ps)-1)
   for i,pp in enumerate(ps):widths.append({'selector':{'metadata':pp['queryRef']},'properties':{'value':lit(first if i==0 else rest)}})
  else:
   ws=[100,180,158,108,95,85,90,125]
   for i,pp in enumerate(ps):widths.append({'selector':{'metadata':pp['queryRef']},'properties':{'value':lit(ws[i])}})
  o['columnWidth']=widths
  o.setdefault('columnHeaders',prop())[0]['properties']['autoSizeColumnWidth']=lit(False)
  o['columnHeaders'][0]['properties']['fontSize']=lit(11)
  o.setdefault('values',prop())[0]['properties']['fontSize']=lit(11)
 if kind=='slicer':
  ps=v.get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[])
  if ps and ps[0]['field'].get('Column',{}).get('Property')=='Demand Change':o['selection']=prop(singleSelect=lit(True),selectAllCheckboxEnabled=lit(False))
 if kind=='card':
  tt=co.get('title',[{}])[0].get('properties',{}).get('text',{}).get('expr',{}).get('Literal',{}).get('Value','')
  if tt=="'Available workforce hours'":co['title'][0]['properties']['text']=lit('Unused workforce hours')
 f.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
pages=R/'pages/pages.json';d=json.loads(pages.read_text());d['activePageName']='9383f2eb13e59bb0918a';pages.write_text(json.dumps(d,indent=2))
print('Refined header spacing, series colors, table widths, and scenario selection.')
