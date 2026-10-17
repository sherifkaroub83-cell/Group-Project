import json,re
from pathlib import Path
R=Path(__file__).parent/'Dashboard.Report/definition/pages'
def lit(v):return {'expr':{'Literal':{'Value':str(v)+'D' if isinstance(v,(int,float)) else "'"+v+"'"}}}
for folder in R.iterdir():
 if not folder.is_dir():continue
 for f in folder.glob('visuals/*/visual.json'):
  v=json.loads(f.read_text());p=v['position'];kind=v['visual']['visualType'];o=v['visual'].get('objects',{})
  if folder.name in ['service','capacity']:
   if kind in ['lineChart','clusteredBarChart','clusteredColumnChart']:p['height']=155
   if kind=='tableEx':p['y']=505;p['height']=180;o['grid'][0]['properties']['rowPadding']=lit(3)
   if kind=='textbox' and p['y'] in [570,580]:p['y']=505;p['height']=180
  if folder.name=='financial':
   if kind in ['clusteredBarChart','scatterChart']:p['height']=155
   if kind=='tableEx':p['y']=505;p['height']=180;o['grid'][0]['properties']['rowPadding']=lit(3)
   if kind=='card' and p['y']==337:p['height']=75
   if kind=='card' and p['y']==445:p['y']=420;p['height']=72
   if kind=='textbox' and p['y']==546:p['y']=686;p['height']=5
  if folder.name=='priorities':
   if kind=='clusteredBarChart':p['height']=150
   if kind=='tableEx':p['y']=500;p['height']=185;o['grid'][0]['properties']['rowPadding']=lit(3)
  f.write_text(json.dumps(v,indent=2))
print('Adjusted analytic panel heights for complete summary rows.')
