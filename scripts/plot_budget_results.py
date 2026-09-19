"""Rebuild the release comparison chart from audited public summary statistics."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

p=argparse.ArgumentParser();p.add_argument('run_id',nargs='?',default='v0.2-budget');a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=root/'results'/a.run_id
s=json.loads((out/'summary.json').read_text());ss=s['systems']
models=['qwen3.5:0.8b','qwen3.5:2b-q8_0','qwen3.5:4b-q8_0']
keys=['jev']+[m+' / '+b for m in models for b in ['off','512','2048']]
if set(ss)!=set(keys) or not all(ss[k]['complete'] for k in keys):raise SystemExit('Ten complete published conditions required')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'savefig.facecolor':'#ffffff','svg.fonttype':'none'})
colors={'off':'#AEC3D2','512':'#4B94BC','2048':'#15577D','jev':'#C9553C'}
y=[11.5,9.9,8.9,7.9,6.4,5.4,4.4,2.9,1.9,.9]
fig,ax=plt.subplots(figsize=(13.2,8.8));fig.subplots_adjust(left=.245,right=.925,top=.80,bottom=.15)
for k,pos in zip(keys,y):
 r=ss[k];value=r['accuracy']*100;lo,hi=[v*100 for v in r['accuracy_95ci']];budget=k.split(' / ')[-1] if k!='jev' else 'jev'
 ax.barh(pos,value,height=.66,color=colors[budget],zorder=2)
 ax.errorbar(value,pos,xerr=[[value-lo],[hi-value]],fmt='none',ecolor='#25323F',capsize=3,lw=1.25,zorder=3)
 ax.text(115,pos,f'{value:.1f}%',ha='right',va='center',fontsize=12,fontweight='bold',color=colors['jev'] if k=='jev' else '#172B3A')
labels=['Jev 1.13.0']+[f'{size}  /  {budget}' for size in ['Qwen3.5 0.8B','Qwen3.5 2B','Qwen3.5 4B'] for budget in ['No thinking','512 tokens','2,048 tokens']]
ax.set_yticks(y,labels=labels);ax.tick_params(axis='y',length=0,pad=12);ax.set(xlim=(0,117),ylim=(0,12.25),xlabel='Accuracy on JF100 (%)')
ax.set_xticks([0,25,50,75,100]);ax.grid(axis='x',color='#E8EDF1',zorder=0)
ax.axvline(77,color=colors['jev'],ls=(0,(4,4)),lw=1.15,zorder=1)
ax.axvline(25,color='#8D99A2',ls=':',lw=.8,zorder=1)
for pos in [10.8,7.15,3.65]:ax.axhline(pos,color='#E8EDF1',lw=.8,zorder=0)
fig.text(.06,.95,'Jev vs Qwen3.5: reasoning budget matters',fontsize=23,fontweight='bold',color='#172B3A')
fig.text(.06,.91,'100 original four-choice tasks · 3 trials per condition · Qwen Q8_0',fontsize=12,color='#566674')
fig.text(.06,.865,'Jev: 77.0%     |     2B + 2,048: 82.0%     |     4B + 2,048: 96.7%',fontsize=13,color='#172B3A')
fig.legend(handles=[Patch(color=colors[b],label=label) for b,label in [('off','No thinking'),('512','512-token budget'),('2048','2,048-token budget'),('jev','Jev reference')]],loc='lower left',bbox_to_anchor=(.06,.071),ncol=4,frameon=False,fontsize=10)
fig.text(.06,.047,'Whiskers: 95% bootstrap intervals, resampling paired templates within domains. Dashed line: Jev (77%).',fontsize=9,color='#667482')
fig.text(.06,.025,'Exploratory task performance, not a universal intelligence ceiling or parameter-count equivalence. Uniform guessing: 25%.',fontsize=9,color='#667482')
for ext in ['png','svg','pdf']:fig.savefig(out/f'comparison-statistical.{ext}',dpi=200)
plt.close(fig)
# Homepage: discrete budget conditions, with direct labels and a shared Jev reference.
ink, muted, grid = '#192C39', '#647480', '#E8EDF0'
series_colors = ['#82939F', '#247FA0', '#6448A3']
fig, ax = plt.subplots(figsize=(12, 7.8))
fig.subplots_adjust(left=.10, right=.80, top=.75, bottom=.21)
fig.text(.07, .94, 'JF100  /  MODEL CAPABILITY', fontsize=10, fontweight='bold', color=muted)
fig.text(.07, .875, 'Where does Jev stand?', fontsize=29, fontweight='bold', color=ink)
fig.text(.07, .82, '100 original questions · 3 trials per condition · Qwen3.5 Q8_0', fontsize=12, color=muted)
ax.set(xlim=(-.12, 2.30), ylim=(0, 104))
ax.set_yticks([0, 25, 50, 75, 100], labels=['0%', '25%', '50%', '75%', '100%'])
ax.set_xticks([0, 1, 2], labels=['Thinking off', '512 tokens', '2,048 tokens'])
ax.tick_params(axis='both', length=0, pad=12, colors=muted)
ax.grid(axis='y', color=grid, lw=.9, zorder=0)
ax.set_axisbelow(True)
ax.text(0, 1.045, 'ACCURACY', transform=ax.transAxes, fontsize=9, color=muted, fontweight='bold')
jev = ss['jev']['accuracy'] * 100
ax.axhline(jev, color=colors['jev'], lw=1.5, ls=(0, (5, 4)), zorder=1)
ax.text(2.36, jev, f'Jev  {jev:.0f}%', va='center', color=colors['jev'], fontweight='bold', fontsize=13)
for model, label, color in zip(models, ['0.8B', '2B', '4B'], series_colors):
 values = [ss[model+' / '+b]['accuracy']*100 for b in ['off', '512', '2048']]
 ax.plot([0, 1, 2], values, color=color, lw=2.6, marker='o', ms=8, markeredgecolor='white', markeredgewidth=1.8, zorder=3)
 for x, value in enumerate(values):
  # 4B/512 is close to the reference; put its label above the marker.
  offset = -22 if label == '0.8B' else 12
  ax.annotate(f'{value:.1f}%', (x, value), xytext=(0, offset), textcoords='offset points', ha='center', color=color, fontsize=12, fontweight='bold')
 ax.text(2.36, values[-1], f'Qwen3.5 {label}', va='center', color=color, fontsize=12, fontweight='bold')
fig.text(.10, .115, 'Configured thinking budget', fontsize=11, color=ink)
fig.text(.10, .077, 'Three discrete settings; spacing does not represent equal compute. Jev uses its native API.', fontsize=9, color=muted)
fig.text(.10, .046, 'Exploratory benchmark performance. Statistical intervals and paired comparisons are in the report.', fontsize=9, color=muted)
for ext in ['png', 'svg', 'pdf']:
 fig.savefig(out/f'comparison.{ext}', dpi=200)
plt.close(fig)

# Confidence curves use observed correctness, with score semantics visible.
fig,axes=plt.subplots(1,3,figsize=(12.5,4.5),layout='constrained')
for ax,model in zip(axes,models):
 ax.plot([0,1],[0,1],':',color='#AAA')
 for b in ['off','512','2048']:
  bins=s['confidence_analysis'][model+' / '+b]['reliability_bins'];ax.plot([x['mean_confidence'] for x in bins],[x['accuracy'] for x in bins],'-o',color=colors[b],label=b,ms=4)
 bins=s['confidence_analysis']['jev']['reliability_bins'];ax.plot([x['mean_confidence'] for x in bins],[x['accuracy'] for x in bins],'--',color=colors['jev'],label='Jev')
 ax.set(title=model.split(':')[1].split('-')[0].upper(),xlabel='Mean confidence / token-probability proxy',ylabel='Observed correctness',xlim=(0,1),ylim=(0,1));ax.legend(fontsize=8)
fig.suptitle('Exploratory reliability · valid answers with an available score\nQwen: emitted answer-token probability; Jev: returned confidence (different definitions)',fontsize=11)
for ext in ['png','svg','pdf']:fig.savefig(out/f'confidence.{ext}',dpi=180)
print(out/'comparison.png')
