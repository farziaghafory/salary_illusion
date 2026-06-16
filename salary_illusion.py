# The Salary Illusion — Dark Theme Version
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')
 
# COLORS
BG        = '#0f1117'   
PANEL     = '#1a1d2e'   
GOLD      = '#f5c842'   
TEAL      = '#4fc3b0'   
RED       = '#e05c5c'  
MUTED     = '#4a4f6a'   
WHITE     = '#e8eaf0'   
SUBTEXT   = '#8891b0'   
 
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
df_sal = df_raw[
    (df_raw['Sex'] == 'Both genders') &
    (df_raw['Autonomous Communities'] == 'National Total') &
    (df_raw['Measurements and percentiles'] == 'Average')
].copy()
df_sal = (df_sal
    .rename(columns={'Periodo':'year','Total':'salary'})
    [['year','salary']]
    .sort_values('year')
    .reset_index(drop=True))
df_sal['year'] = df_sal['year'].astype(int)
 
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
 
df = pd.merge(df_sal, df_cpi, on='year').dropna().reset_index(drop=True)
df['real_salary'] = (df['salary'] / df['cpi']) * 100
df['nom_growth']  = df['salary'].pct_change() * 100
df['real_growth'] = df['real_salary'].pct_change() * 100
 
S0  = df['salary'].iloc[0];   S1  = df['salary'].iloc[-1]
R1  = df['real_salary'].iloc[-1];  GAP = S1 - R1
Y0  = int(df['year'].iloc[0]); Y1  = int(df['year'].iloc[-1])
NOM_PCT  = (S1/S0 - 1)*100;   REAL_PCT = (R1/S0 - 1)*100
NEG      = int((df['real_growth'] < 0).sum())
growth   = df['real_growth'].dropna().values
 
print(f'  {Y0}-{Y1}  |  Nominal: +{NOM_PCT:.1f}%  |  Real: +{REAL_PCT:.1f}%  |  Gap: {euro(GAP/12)}/month')
 
 
# CHART 1: Salary on paper 
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(df['year'], df['salary'], color=GOLD, linewidth=2.5,
        marker='o', markersize=7, markerfacecolor=BG, markeredgewidth=2, markeredgecolor=GOLD)
ax.fill_between(df['year'], df['salary'], alpha=0.08, color=GOLD)
for _, r in df[df['year'] % 2 == 0].iterrows():
    ax.annotate(euro(r['salary']), xy=(r['year'], r['salary']),
                xytext=(0, 12), textcoords='offset points',
                ha='center', fontsize=8, color=GOLD, weight='bold')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: euro(x)))
ax.set_title(f'Average salary in Spain went up {NOM_PCT:.0f}% between {Y0} and {Y1}')
ax.set_xlabel('Year');  ax.set_ylabel('Gross salary per year')
ax.set_ylim(S0 * 0.88, S1 * 1.12)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart1_salary_on_paper')
 
 
#  CHART 2: Prices going up
fig, ax = plt.subplots(figsize=(11, 5))
bar_colors = [RED if y >= 2021 else MUTED for y in df['year']]
ax.bar(df['year'], df['cpi'] - 100, color=bar_colors, width=0.6, zorder=2)
ax.axhline(0, color=SUBTEXT, linewidth=0.8, linestyle='--')
if 2022 in df['year'].values:
    v22 = float(df[df['year']==2022]['cpi'].values[0]) - 100
    ax.annotate('2022 — prices jumped\nmore than any year\nin the last 40 years',
                xy=(2022, v22), xytext=(2018, v22 + 3),
                fontsize=8.5, color=RED, weight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(facecolor=RED,   label='High inflation (2021–2023)'),
    Patch(facecolor=MUTED, label='Normal years'),
], fontsize=9, frameon=True)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'+{x:.0f}%' if x > 0 else f'{x:.0f}%'))
ax.set_title(f'But prices also went up — especially after 2021')
ax.set_xlabel('Year');  ax.set_ylabel(f'Cumulative price rise since {Y0}')
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart2_prices_going_up')
 
 
# CHART 3: The big reveal
fig, ax = plt.subplots(figsize=(12, 6))
nom_idx  = (df['salary']      / df['salary'].iloc[0])      * 100
real_idx = (df['real_salary'] / df['real_salary'].iloc[0]) * 100
 
ax.plot(df['year'], nom_idx, color=GOLD, linewidth=2.8,
        marker='o', markersize=6, markerfacecolor=BG, markeredgewidth=2, markeredgecolor=GOLD)
ax.plot(df['year'], real_idx, color=TEAL, linewidth=2.8,
        marker='o', markersize=6, markerfacecolor=BG, markeredgewidth=2, markeredgecolor=TEAL)
ax.fill_between(df['year'], nom_idx, real_idx, where=(nom_idx >= real_idx),
                alpha=0.15, color=RED)
ax.axhline(100, color=MUTED, linewidth=1, linestyle='--')
ax.text(Y1 + 0.2, nom_idx.iloc[-1],  'Salary on paper', color=GOLD, fontsize=9, weight='bold', va='center')
ax.text(Y1 + 0.2, real_idx.iloc[-1], 'What you can buy', color=TEAL, fontsize=9, weight='bold', va='center')
mid = (nom_idx.iloc[-1] + real_idx.iloc[-1]) / 2
ax.annotate(f'{euro(GAP/12)}/month\nlost to inflation',
            xy=(Y1, mid), xytext=(Y1 - 5, mid + 8),
            fontsize=9, color=RED, weight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
ax.set_title(f'Salaries went up {NOM_PCT:.0f}% — but what you can buy only went up {REAL_PCT:.0f}%')
ax.set_xlabel('Year');  ax.set_ylabel(f'Index (2008 = 100)')
ax.set_xlim(Y0 - 0.5, Y1 + 4)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart3_the_big_reveal')
 
 
# CHART 4: Good and bad years
yr_df = df.dropna(subset=['real_growth']).copy()
bar_c = [TEAL if v >= 0 else RED for v in yr_df['real_growth']]
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(yr_df['year'], yr_df['real_growth'], color=bar_c, width=0.6, zorder=2)
ax.axhline(0, color=SUBTEXT, linewidth=1)
for bar, val in zip(bars, yr_df['real_growth']):
    ax.text(bar.get_x() + bar.get_width()/2,
            val + (0.15 if val >= 0 else -0.35),
            f'{val:+.1f}%', ha='center',
            va='bottom' if val >= 0 else 'top',
            fontsize=7.5, color=WHITE, weight='bold')
if 2022 in yr_df['year'].values:
    v = float(yr_df[yr_df['year']==2022]['real_growth'].values[0])
    ax.annotate('Worst year —\nprices outpaced\nsalary growth',
                xy=(2022, v), xytext=(2019, v - 2.5),
                fontsize=8.5, color=RED, weight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
ax.set_title(f'{NEG} out of {len(yr_df)} years — real purchasing power actually fell')
ax.set_xlabel('Year');  ax.set_ylabel('Change in real salary (%)')
ax.set_ylim(yr_df['real_growth'].min() - 2.5, yr_df['real_growth'].max() + 2.5)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart4_good_and_bad_years')
 
 
# CHART 5: Monte Carlo / confidence
np.random.seed(42)
boot = np.array([
    np.random.choice(growth, size=len(growth), replace=True).mean()
    for _ in range(1000)
])
lo, hi    = np.percentile(boot, [2.5, 97.5])
boot_mean = boot.mean()
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(boot, bins=40, color=TEAL, alpha=0.5, edgecolor=BG, linewidth=0.5)
ax.axvline(lo,        color=RED,    linestyle='--', linewidth=1.8, label=f'Lower bound: {lo:.2f}%')
ax.axvline(hi,        color=RED,    linestyle='--', linewidth=1.8, label=f'Upper bound: {hi:.2f}%')
ax.axvline(boot_mean, color=GOLD,   linestyle='-',  linewidth=2,   label=f'Average: {boot_mean:.2f}%')
ax.axvline(0,         color=SUBTEXT,linestyle=':',  linewidth=1.5, label='Zero line (no change)')
ax.axvspan(lo, hi, alpha=0.08, color=TEAL)
ax.set_title(f'1,000 simulations — real salary growth ranged from {lo:.1f}% to {hi:.1f}%')
ax.set_xlabel('Average real salary growth per year (%)');  ax.set_ylabel('Simulations')
ax.legend(fontsize=9)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart5_how_sure_are_we')
 
 
# CHART 6: the real number
fig, ax = plt.subplots(figsize=(9, 5))
labels = ['Salary on paper', 'Real purchasing power', 'Lost to inflation']
values = [S1, R1, GAP]
colors = [GOLD, TEAL, RED]
bars = ax.bar(labels, values, color=colors, width=0.45, zorder=2)
for bar, val, col in zip(bars, values, colors):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 250,
            euro(val), ha='center', fontsize=12, weight='bold', color=col)
ax.annotate(f'= {euro(GAP/12)} every month',
            xy=(2, GAP * 0.5), xytext=(1.35, GAP * 0.75),
            fontsize=9.5, color=RED, weight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.3))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: euro(x)))
ax.set_title(f'{euro(GAP/12)} disappears every month — earned but never felt')
ax.set_ylabel(f'Euros per year in {Y1}')
ax.set_ylim(0, S1 * 1.20)
ax.yaxis.grid(True); ax.xaxis.grid(False)
save('chart6_the_real_number')
 
 
#Test
t_stat, p_value = stats.ttest_1samp(growth, popmean=0)
print()
print('=' * 50)
print('  RESULTS')
print('=' * 50)
print(f'  Salary on paper:  {euro(S0)} → {euro(S1)}  (+{NOM_PCT:.1f}%)')
print(f'  Real value:       {euro(S0)} → {euro(R1)}  (+{REAL_PCT:.1f}%)')
print(f'  Lost per month:   {euro(GAP/12)}')
print(f'  Bad years:        {NEG} out of 16')
print(f'  Simulation range: {lo:.2f}% to {hi:.2f}%')
print(f'  p-value:          {p_value:.4f}')
print()
print('  All 6 charts saved.')
print('=' * 50)