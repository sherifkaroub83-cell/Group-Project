"""Reproducible educational demand regression. No current outcomes are predictors."""
from pathlib import Path
import csv,json,math,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent
rows=list(csv.DictReader((R/'Group_9226_Team_4_Enterprise_Dataset.csv').open(encoding='utf-8-sig')))
features=['Business_Unit','Region','Project_or_Product']
train=[r for r in rows if r['Record_Date'][:4]=='2024'];valid=[r for r in rows if r['Record_Date'][:4]=='2025'];test=[r for r in rows if r['Record_Date'][:4]=='2026']
def design_fit(rs):
 cats={f:sorted({r[f] for r in rs}) for f in features};return cats
def transform(rs,cats):
 return np.array([[1.]+[float(r[f]==v) for f in features for v in cats[f]]+[math.sin(2*math.pi*int(r['Record_Date'][5:7])/12),math.cos(2*math.pi*int(r['Record_Date'][5:7])/12)] for r in rs])
def target(rs):return np.array([float(r['Demand_Units']) for r in rs])
def fit(rs,alpha):
 cats=design_fit(rs);x=transform(rs,cats);pen=np.eye(x.shape[1])*alpha;pen[0,0]=0;coef=np.linalg.solve(x.T@x+pen,x.T@target(rs));return cats,coef
def predict(rs,fit):return np.maximum(0,transform(rs,fit[0])@fit[1])
def baseline(rs,training):
 av={b:np.mean([float(r['Demand_Units']) for r in training if r['Business_Unit']==b]) for b in {r['Business_Unit'] for r in training}};glob=np.mean(target(training));return np.array([av.get(r['Business_Unit'],glob) for r in rs])
def metrics(y,p):
 e=p-y;return {'n':len(y),'MAE':float(np.mean(abs(e))),'RMSE':float(np.sqrt(np.mean(e**2))),'WAPE':float(sum(abs(e))/sum(y)),'bias_pct':float(sum(e)/sum(y))}
trials={a:metrics(target(valid),predict(valid,fit(train,a))) for a in [1,10,100,1000]};alpha=min(trials,key=lambda a:trials[a]['MAE']);final=fit(train+valid,alpha);pred=predict(test,final);base=baseline(test,train+valid);y=target(test)
result={'purpose':'Estimate allocation-record demand before outcomes using only assumed known unit, region, initiative and scheduled month. Educational feasibility study, not deployable forecast.','target':'Demand_Units','eligible_predictors':features+['scheduled month sine/cosine'],'timing_assumption':'Unit, region, initiative and scheduled observation month assumed known at planning time; source has no event-time feature availability log.','excluded':'All supplied forecasts, demand/supply/capacity/outcomes, scores, labels, numeric financial and resource measures, identifiers, demand/inventory/risk status.','validation':'Train 2024 (2004); select ridge penalty on 2025 (2000) MAE; freeze design, refit 2024-2025; evaluate once on 2026 (996).','baseline':'Business-unit historical mean demand fitted on training window; global mean fallback for unseen unit.','validation_trials':trials,'selected_alpha':alpha,'test_model':metrics(y,pred),'test_baseline':metrics(y,base),'segments':{},'limitations':['Synthetic educational data with embedded relationships. No real-world generalization claim.','Repeated entities are excluded as predictors; test estimates future observations in known portfolio, not new-entity performance.','Sparse irregular dates; record demand regression is not a continuous demand time-series forecast.','No Reallocate classifier: only 11 labels and supplied score components risk leakage.','No optimization or achieved savings demonstrated.']}
for b in sorted({r['Business_Unit'] for r in test}):
 ix=np.array([r['Business_Unit']==b for r in test]);result['segments'][b]={'model':metrics(y[ix],pred[ix]),'baseline':metrics(y[ix],base[ix])}
result['conclusion']='Ridge improves held-out MAE versus baseline.' if result['test_model']['MAE']<result['test_baseline']['MAE'] else 'Ridge does not beat the informative baseline on held-out MAE; retain baseline for this experiment.'
(O/'model_results.json').write_text(json.dumps(result,indent=2));(O/'model_parameters.json').write_text(json.dumps({'categories':final[0],'coefficients':final[1].tolist(),'alpha':alpha},indent=2))
with (O/'Heldout_Predictions.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Record_ID','Actual_Demand','Model_Prediction','Baseline_Prediction','Model_Absolute_Error','Baseline_Absolute_Error','Model_Squared_Error','Baseline_Squared_Error'])
 for r,a,p,b in zip(test,y,pred,base):w.writerow([r['Record_ID'],a,p,b,abs(p-a),abs(b-a),(p-a)**2,(b-a)**2])
print(json.dumps(result,indent=2))
