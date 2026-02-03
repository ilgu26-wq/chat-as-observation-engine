"""
Generate Final Violin Plot: B vs D Only

Execution power increases variance.
Execution structure compresses it.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

with open("results/jve_results.json", "r") as f:
    data = json.load(f)

metrics = data["metrics"]
B_outcomes = metrics["B"]["outcomes"]
D_outcomes = metrics["D"]["outcomes"]
B_mean = metrics["B"]["mean"]
D_mean = metrics["D"]["mean"]

fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')

ax.axhspan(-0.5, 1.5, color='#ffcccc', alpha=0.5, zorder=0)
ax.axhline(y=1.5, color='#cc0000', linewidth=1.5, linestyle='--', alpha=0.7)
ax.text(1.5, 0.3, "Irreversible Failure Zone", ha="center", fontsize=10, 
        color='#990000', weight='bold', style='italic')

parts = ax.violinplot(
    [B_outcomes, D_outcomes],
    positions=[1, 2],
    showmeans=False,
    showmedians=False,
    showextrema=False,
    widths=0.6
)

colors = ['#e53935', '#26a69a']
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(colors[i])
    pc.set_edgecolor('#333333')
    pc.set_linewidth(1.5)
    pc.set_alpha(0.85)

ax.scatter([1, 2], [B_mean, D_mean], color="white", s=80, zorder=6, edgecolor='black', linewidth=2)

ax.annotate(
    '',
    xy=(1, 0.5), xytext=(1, 2.5),
    arrowprops=dict(arrowstyle='<->', color='#cc0000', lw=2),
    zorder=3
)
ax.text(0.7, 1.5, "tail\nrisk", ha='center', va='center', fontsize=9, color='#990000', weight='bold')

ax.annotate(
    'Bar1 + Constraint',
    xy=(2, 8.5),
    ha='center',
    fontsize=10,
    color='#00695c',
    weight='bold',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#e0f2f1', edgecolor='#26a69a', linewidth=1.5)
)

ax.set_xticks([1, 2])
ax.set_xticklabels(['High-Execution', 'Structured (V7)'], fontsize=12, weight='bold')
ax.set_ylabel("Outcome Quality", fontsize=12)
ax.set_ylim(-1, 11)
ax.set_xlim(0.3, 2.7)

ax.set_title(
    "Execution Power vs Execution Structure",
    fontsize=15,
    weight='bold',
    pad=15
)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

red_patch = mpatches.Patch(color='#e53935', alpha=0.85, label='High-Execution: Wide variance, 11% catastrophic')
teal_patch = mpatches.Patch(color='#26a69a', alpha=0.85, label='Structured (V7): Compressed, 0% catastrophic')
ax.legend(handles=[red_patch, teal_patch], loc='upper left', framealpha=0.9, fontsize=9)

plt.tight_layout()
plt.savefig("../images/judgment_vs_execution_distribution.png", dpi=200, facecolor='white', bbox_inches='tight')
print("✅ Saved: images/judgment_vs_execution_distribution.png")
plt.close()
