import json, uuid, re, copy
from pathlib import Path
W = Path(__file__).parent
P = W/'Dashboard.Report/definition/pages'
CAL = W/'Dashboard.SemanticModel/definition/tables/Calendar.tmdl'
TEAL = "'#007F87'"
def lit(v): return {'expr': {'Literal': {'Value': v}}}
def col(c): return {'solid': {'color': lit(c)}}
def load(pg, vid): return json.loads((P/pg/'visuals'/vid/'visual.json').read_text(encoding='utf-8-sig'))
def save(pg, vid, v):
    d = P/pg/'visuals'/vid; d.mkdir(parents=True, exist_ok=True)
    (d/'visual.json').write_text(json.dumps(v, indent=2), encoding='utf-8')
def ensure_default_fill(v, color=TEAL):
    dp = v['visual']['objects'].setdefault('dataPoint', [])
    dp[:] = [e for e in dp if 'selector' in e]  # keep per-series entries
    dp.insert(0, {'properties': {'fill': col(color), 'defaultColor': col(color)}})
def labels_on(v, size='10D'):
    v['visual']['objects']['labels'] = [{'properties': {'show': lit('true'), 'fontSize': lit(size), 'color': col("'#20364B'")}}]
def pad(v, val='18D'):
    v['visual']['objects']['categoryAxis'][0]['properties']['innerPadding'] = lit(val)
def pos(v, **k): v['position'].update(k)
def title(v, t): v['visual']['visualContainerObjects']['title'][0]['properties']['text'] = lit("'" + t + "'")
def fit_table(v):
    o = v['visual']['objects']; w = v['position']['width']
    widths = o.get('columnWidth', [])
    tot = sum(float(x['properties']['value']['expr']['Literal']['Value'].rstrip('DL')) for x in widths)
    if tot > w - 35:
        for x in widths:
            val = float(x['properties']['value']['expr']['Literal']['Value'].rstrip('DL'))
            x['properties']['value'] = lit(f"{round(val*(w-35)/tot,1)}D")
def proj(entity, prop, kind='Measure', display=None):
    return {'field': {kind: {'Expression': {'SourceRef': {'Entity': entity}}, 'Property': prop}},
            'queryRef': f'{entity}.{prop}', 'nativeQueryRef': prop, 'displayName': display or prop}
newid = lambda: uuid.uuid4().hex[:20]

# ---------- 1. Portfolio: narrow scorecard, add flagged-budget bar chart ----------
t = load('executive', '9b5efaa1c7454b93ac71'); pos(t, width=440); fit_table(t); save('executive', '9b5efaa1c7454b93ac71', t)
bar = load('financial', '403a954559cd4ce99fdb'); bar = copy.deepcopy(bar)
bid = 'a1b2c3d4e5f60718293a'; bar['name'] = bid
bar['position'] = {'x': 886, 'y': 354, 'z': 40, 'height': 235, 'width': 374, 'tabOrder': 40}
q = bar['visual']['query']
q['queryState']['Y']['projections'] = [proj('Allocation', 'Attention Budget M', display='Flagged budget ($m)')]
q['queryState']['Category']['projections'][0]['active'] = True
q['sortDefinition'] = {'sort': [{'field': {'Measure': {'Expression': {'SourceRef': {'Entity': 'Allocation'}}, 'Property': 'Attention Budget M'}}, 'direction': 'Descending'}]}
bar['visual']['objects']['dataPoint'] = [{'properties': {'fill': col("'#C9862B'")}, 'selector': {'metadata': 'Allocation.Attention Budget M'}}]
ensure_default_fill(bar, "'#C9862B'"); labels_on(bar); pad(bar)
title(bar, 'Where flagged budget sits | $m, Review + Reallocate')
save('executive', bid, bar)

# ---------- 2. Financial: taller charts, labels, colour, scatter labels, overlap, quarterly trend ----------
b = load('financial', '403a954559cd4ce99fdb'); pos(b, height=188); ensure_default_fill(b); labels_on(b, '9D'); pad(b); save('financial', '403a954559cd4ce99fdb', b)
s = load('financial', 'f021211525b14396a60b'); pos(s, height=188)
s['visual']['objects']['categoryLabels'] = [{'properties': {'show': lit('true'), 'fontSize': lit('9D'), 'color': col("'#20364B'")}}]
s['visual']['objects']['categoryAxis'][0]['properties']['showAxisTitle'] = lit('true')
s['visual']['objects']['valueAxis'][0]['properties']['showAxisTitle'] = lit('true')
save('financial', 'f021211525b14396a60b', s)
c = load('financial', '9e0186488f7c4137b593'); pos(c, height=58); save('financial', '9e0186488f7c4137b593', c)
fn = load('financial', 'c78c3152e60649ac9da7'); pos(fn, y=482, height=28); save('financial', 'c78c3152e60649ac9da7', fn)
tb = load('financial', 'd71bfc0ae32c483dafb4'); pos(tb, y=518, height=165, width=800); fit_table(tb); save('financial', 'd71bfc0ae32c483dafb4', tb)
ln = copy.deepcopy(load('unit_detail', '239689bf5c9e44979f64'))
lid = 'b2c3d4e5f6071829304b'; ln['name'] = lid
ln['position'] = {'x': 832, 'y': 518, 'z': 41, 'height': 165, 'width': 428, 'tabOrder': 41}
lq = ln['visual']['query']['queryState']
lq['Category']['projections'] = [dict(proj('Calendar', 'Year Quarter', 'Column', 'Quarter'), active=True)]
lq['Y']['projections'] = [proj('Allocation', 'Revenue per Record', display='Revenue per record')]
ln['visual']['query'].pop('sortDefinition', None)
ln['visual']['objects']['valueAxis'][0]['properties']['start'] = lit('0D')
ensure_default_fill(ln)
title(ln, 'Revenue per record by quarter | normalized for record counts')
save('financial', lid, ln)

# ---------- 3. Demand & Service: delay chart shows all 5 scenarios ----------
d = load('service', 'b9e7a4be467740028f72'); pos(d, height=188); ensure_default_fill(d); labels_on(d, '9D'); pad(d); save('service', 'b9e7a4be467740028f72', d)
l2 = load('service', 'aa8b44166e514c9c8ad8'); pos(l2, height=188); save('service', 'aa8b44166e514c9c8ad8', l2)
st = load('service', '2770b846153c4802b2ae'); pos(st, y=518, height=165); save('service', '2770b846153c4802b2ae', st)
tx = load('service', 'cbe557ef62104c519c64'); pos(tx, y=518, height=165); save('service', 'cbe557ef62104c519c64', tx)

# ---------- 4. Capacity: gap chart colour + labels ----------
g = load('capacity', 'b303483a9c4b420f9a8e'); ensure_default_fill(g); labels_on(g, '9D'); save('capacity', 'b303483a9c4b420f9a8e', g)
u = load('capacity', '0164497b72424e409708'); labels_on(u, '9D'); save('capacity', '0164497b72424e409708', u)

# ---------- 5. Unit drill-through: honest axis ----------
ul = load('unit_detail', '239689bf5c9e44979f64'); ul['visual']['objects']['valueAxis'][0]['properties']['start'] = lit('0D')
labels_on(ul, '9D'); save('unit_detail', '239689bf5c9e44979f64', ul)

# ---------- 6. Priorities: demand-change slicer defaults to 0% ----------
sl = load('priorities', 'c2471bef90f54f3a8eda')
sl['visual']['objects']['general'] = [{'properties': {'filter': {'filter': {'Version': 2,
    'From': [{'Name': 'd', 'Entity': 'Demand Scenario', 'Type': 0}],
    'Where': [{'Condition': {'In': {'Expressions': [{'Column': {'Expression': {'SourceRef': {'Source': 'd'}}, 'Property': 'Demand Change'}}],
                                    'Values': [[{'Literal': {'Value': '0D'}}]]}}}]}}}}]
save('priorities', 'c2471bef90f54f3a8eda', sl)

# ---------- 7. Model evidence: text fits without scrolling ----------
me = load('model_evidence', '49755aaf11a3490cb5ff')
for para in me['visual']['objects']['general'][0]['properties']['paragraphs']:
    for r in para.get('textRuns', []):
        r.setdefault('textStyle', {})['fontSize'] = '10pt'
save('model_evidence', '49755aaf11a3490cb5ff', me)

# ---------- 8. Calendar: Year Quarter columns ----------
s = CAL.read_text(encoding='utf-8-sig')
if "Year Quarter" not in s:
    s = s.replace('\tpartition Calendar = m',
        "\tcolumn 'Year Quarter'\n\t\tdataType: string\n\t\tlineageTag: " + str(uuid.uuid4()) +
        "\n\t\tsummarizeBy: none\n\t\tsourceColumn: Year Quarter\n\t\tsortByColumn: 'Year Quarter Sort'\n\n"
        "\tcolumn 'Year Quarter Sort'\n\t\tdataType: int64\n\t\tisHidden\n\t\tformatString: 0\n\t\tlineageTag: " + str(uuid.uuid4()) +
        "\n\t\tsummarizeBy: none\n\t\tsourceColumn: Year Quarter Sort\n\n\tpartition Calendar = m")
    s = s.replace('\t\t\t\tin S',
        '\t\t\t\t    Q = Table.AddColumn(S,"Year Quarter",each Text.From(Date.Year([Date])) & " Q" & Text.From(Date.QuarterOfYear([Date])),type text),\n'
        '\t\t\t\t    QS = Table.AddColumn(Q,"Year Quarter Sort",each Date.Year([Date])*10+Date.QuarterOfYear([Date]),Int64.Type)\n'
        '\t\t\t\tin QS')
    CAL.write_text(s, encoding='utf-8')
# open on Portfolio
pj = P/'pages.json'; d = json.loads(pj.read_text(encoding='utf-8-sig')); d['activePageName'] = 'executive'; pj.write_text(json.dumps(d, indent=2))
print('fixes applied')
