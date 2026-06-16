# The Salary Illusion, Gender
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.patches import Patch
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')
 
# COLORS
BG      = '#0f1117'
PANEL   = '#1a1d2e'
GOLD    = '#f5c842'
TEAL    = '#4fc3b0'
RED     = '#e05c5c'
MUTED   = '#4a4f6a'
WHITE   = '#e8eaf0'
SUBTEXT = '#8891b0'
 
plt.rcParams.update({
    'figure.facecolor':   BG,
    'axes.facecolor':     PANEL,
    'axes.edgecolor':     MUTED,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'axes.spines.left':   False,
    'axes.spines.bottom': False,
    'grid.color':         MUTED,
    'grid.alpha':         0.3,
    'grid.linewidth':     0.5,
    'text.color':         WHITE,
    'axes.labelcolor':    SUBTEXT,
    'xtick.color':        SUBTEXT,
    'ytick.color':        SUBTEXT,
    'font.family':        'sans-serif',
    'axes.titlesize':     13,
    'axes.titleweight':   'bold',
    'axes.titlecolor':    WHITE,
    'axes.labelsize':     10,
    'xtick.labelsize':    9,
    'ytick.labelsize':    9,
    'legend.facecolor':   PANEL,
    'legend.edgecolor':   MUTED,
    'legend.labelcolor':  WHITE,
})
 
def euro(v):
    return f'€{v:,.0f}'
def save(name):
    plt.tight_layout(pad=1.5)
    plt.savefig(f'{name}.png', dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'  saved → {name}.png')
print('Loading data...')
 
df_raw = pd.read_csv('Salary.csv', sep=';', thousands='.', decimal=',')
df_cpi_raw = pd.read_csv('ipc.csv', sep=';')
df_cpi_raw = df_cpi_raw.rename(columns={'Period':'period','Total':'cpi'})
df_cpi_raw['year'] = df_cpi_raw['period'].str[:4].astype(int)
df_cpi_raw['cpi']  = pd.to_numeric(df_cpi_raw['cpi'], errors='coerce')
df_cpi = (df_cpi_raw
    .groupby('year')['cpi'].mean()
    .reset_index()
    .query('year >= 2008')
    .reset_index(drop=True))
df_cpi['cpi'] = (df_cpi['cpi'] / df_cpi['cpi'].iloc[0]) * 100
def get_real_salary(gender_label):
    df = df_raw[
        (df_raw['Sex'] == gender_label) &
        (df_raw['Autonomous Communities'] == 'National Total') &
        (df_raw['Measurements and percentiles'] == 'Average')
    ].copy()
    df = (df.rename(columns={'Periodo':'year','Total':'salary'})
            [['year','salary']]
            .sort_values('year')
            .reset_index(drop=True))
    df['year'] = df['year'].astype(int)
    df = pd.merge(df, df_cpi, on='year').dropna().reset_index(drop=True)
    df['real_salary'] = (df['salary'] / df['cpi']) * 100
    return df
 
men   = get_real_salary('Males')
women = get_real_salary('Females')
years = sorted(set(men['year']) & set(women['year']))
men   = men[men['year'].isin(years)].reset_index(drop=True)
women = women[women['year'].isin(years)].reset_index(drop=True)
 
Y0 = years[0];  Y1 = years[-1]
gap_start  = men['real_salary'].iloc[0]  - women['real_salary'].iloc[0]
gap_end    = men['real_salary'].iloc[-1] - women['real_salary'].iloc[-1]
gap_series = men['real_salary'].values   - women['real_salary'].values
men_growth   = (men['real_salary'].iloc[-1]   / men['real_salary'].iloc[0]   - 1)*100
women_growth = (women['real_salary'].iloc[-1] / women['real_salary'].iloc[0] - 1)*100
 
print(f'  Men real salary:   {euro(men["real_salary"].iloc[0])} → {euro(men["real_salary"].iloc[-1])}  (+{men_growth:.1f}%)')
print(f'  Women real salary: {euro(women["real_salary"].iloc[0])} → {euro(women["real_salary"].iloc[-1])}  (+{women_growth:.1f}%)')
print(f'  Gap in {Y0}: {euro(gap_start)}')
print(f'  Gap in {Y1}: {euro(gap_end)}')
 
# ── CHART 7: Men vs Women real salary ───────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(men['year'], men['real_salary'], color=GOLD, linewidth=2.5,
        marker='o', markersize=6, markerfacecolor=BG, markeredgewidth=2, markeredgecolor=GOLD)
ax.plot(women['year'], women['real_salary'], color=TEAL, linewidth=2.5,
        marker='o', markersize=6, markerfacecolor=BG, markeredgewidth=2, markeredgecolor=TEAL)
ax.fill_between(men['year'], men['real_salary'], women['real_salary'], alpha=0.10, color=RED)
ax.text(Y1 + 0.2, men['real_salary'].iloc[-1],   'Men',   color=GOLD, fontsize=10, weight='bold', va='center')
ax.text(Y1 + 0.2, women['real_salary'].iloc[-1], 'Women', color=TEAL, fontsize=10, weight='bold', va='center')
mid = (men['real_salary'].iloc[-1] + women['real_salary'].iloc[-1]) / 2
ax.annotate(f'Gap today:\n{euro(gap_end)}/year',
            xy=(Y1, mid), xytext=(Y1 - 6, mid + 700),
            fontsize=9, color=RED, weight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: euro(x)))
ax.set_title(f'Women earn {euro(gap_end)} less per year than men — even after adjusting for inflation')
ax.set_xlabel('Year');  ax.set_ylabel('Real salary (in 2008 euros)')
ax.set_xlim(Y0 - 0.5, Y1 + 2.5)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart7_men_vs_women')
 
 
# CHART 8: Gender gap per year 
gap_colors = []
for i, g in enumerate(gap_series):
    if i == 0:
        gap_colors.append(MUTED)
    elif g > gap_series[i - 1]:
        ## gap grew
        gap_colors.append(RED)    
    else:
        ## gap shrank
        gap_colors.append(TEAL)   
 
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(years, gap_series, color=gap_colors, width=0.6, zorder=2)
for bar, val, col in zip(bars, gap_series, gap_colors):
    ax.text(bar.get_x() + bar.get_width()/2, val + 60,
            euro(val), ha='center', fontsize=7.5, weight='bold', color=col)
ax.legend(handles=[
    Patch(facecolor=TEAL,  label='Gap got smaller that year'),
    Patch(facecolor=RED,   label='Gap got bigger that year'),
    Patch(facecolor=MUTED, label='Starting year'),
], fontsize=9)
closed = gap_start - gap_end
years_to_close = int(gap_end / (closed / (Y1 - Y0))) if closed > 0 else 999
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: euro(x)))
ax.set_title(f'Gap closed by {euro(closed)} in 16 years — at this rate it takes until {Y1 + years_to_close} to disappear')
ax.set_xlabel('Year');  ax.set_ylabel('Difference in real salary (men minus women)')
ax.set_ylim(0, max(gap_series) * 1.22)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart8_gap_by_year')
 
 
print()
print('=' * 50)
print('  GENDER RESULTS')
print('=' * 50)
print(f'  Men gained:    +{men_growth:.1f}% in real terms')
print(f'  Women gained:  +{women_growth:.1f}% in real terms')
print(f'  Gap in {Y0}:  {euro(gap_start)} per year')
print(f'  Gap in {Y1}:  {euro(gap_end)} per year')
print(f'  Closed by:     {euro(closed)}')
print(f'  At this rate the gap closes in: {Y1 + years_to_close}')
print()
print('  Chart 7 and chart 8 saved.')
print('=' * 50)