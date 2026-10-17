import json
from pathlib import Path
P = Path(__file__).parent/'Dashboard.Report/definition/pages'
def lit(v): return {'expr': {'Literal': {'Value': v}}}
def edit(pg, vid, fn):
    f = P/pg/'visuals'/vid/'visual.json'; v = json.loads(f.read_text(encoding='utf-8-sig')); fn(v)
    f.write_text(json.dumps(v, indent=2), encoding='utf-8')
def setpos(**k): return lambda v: v['position'].update(k)
# Portfolio scorecard: explicit column widths so unit names are not truncated
def widths(v):
    w = {'Business_Unit': 138, 'Portfolio Expected ROI': 68, 'Order Delay Rate': 62, 'Capacity Gap Rate': 60, 'Attention Records': 72}
    for e in v['visual']['objects'].get('columnWidth', []):
        key = e['selector']['metadata'].split('.', 1)[1]
        if key in w: e['properties']['value'] = lit(f"{w[key]}D")
    print([e['selector']['metadata'] for e in v['visual']['objects'].get('columnWidth', [])])
edit('executive', '9b5efaa1c7454b93ac71', widths)
# Financial + Demand: give tables room so no scrollbar
for vid in ['403a954559cd4ce99fdb', 'f021211525b14396a60b']: edit('financial', vid, setpos(height=182))
for vid in ['d71bfc0ae32c483dafb4', 'b2c3d4e5f6071829304b']: edit('financial', vid, setpos(y=510, height=173))
def small_axis(v):
    v['visual']['objects']['categoryAxis'][0]['properties']['fontSize'] = lit('9D')
edit('financial', 'b2c3d4e5f6071829304b', small_axis)
for vid in ['b9e7a4be467740028f72', 'aa8b44166e514c9c8ad8']: edit('service', vid, setpos(height=182))
for vid in ['2770b846153c4802b2ae', 'cbe557ef62104c519c64']: edit('service', vid, setpos(y=510, height=173))
# Short quarter labels: 24-Q1
c = Path(__file__).parent/'Dashboard.SemanticModel/definition/tables/Calendar.tmdl'
s = c.read_text(encoding='utf-8-sig')
s = s.replace('each Text.From(Date.Year([Date])) & " Q" & Text.From(Date.QuarterOfYear([Date]))',
              'each Text.End(Text.From(Date.Year([Date])),2) & "-Q" & Text.From(Date.QuarterOfYear([Date]))')
c.write_bytes(s.encode('utf-8'))
print('pass 2 applied', '"-Q"' in s)
