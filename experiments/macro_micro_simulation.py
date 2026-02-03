"""
Macro → Micro Division Simulation

Generate 5-axis state space data and visualize Freedom × Cost distribution.
"""

import json
import random
import matplotlib.pyplot as plt
import numpy as np

random.seed(42)
np.random.seed(42)

N_SAMPLES = 2000

def generate_s1_data(n):
    """S1: 판단 + 실행 결합 (분업 없음)"""
    data = []
    for i in range(n):
        freedom = random.random()
        cost = random.random()
        reversibility = random.random()
        time_model = random.choice(["tau", "wall"])
        info_gain = random.random()
        
        if freedom > 0.6 and cost > 0.5:
            if random.random() < 0.15:
                outcome = "catastrophic"
            elif random.random() < 0.4:
                outcome = "fail"
            else:
                outcome = "success"
        else:
            outcome = "success" if random.random() < 0.7 else "fail"
        
        data.append({
            "system": "S1",
            "iteration": i,
            "failure_cost": cost,
            "reversibility": reversibility,
            "time_model": time_model,
            "freedom": freedom,
            "info_gain": info_gain,
            "outcome": outcome
        })
    return data

def generate_s2_data(n):
    """S2: 판단 → 즉시 실행 (약한 분업)"""
    data = []
    for i in range(n):
        freedom = random.random()
        cost = random.random() * 0.8 + 0.1
        reversibility = random.random() * 0.6
        time_model = "wall"
        info_gain = random.random() * 0.5
        
        if freedom > 0.5 and cost > 0.4:
            if random.random() < 0.10:
                outcome = "catastrophic"
            elif random.random() < 0.35:
                outcome = "fail"
            else:
                outcome = "success"
        else:
            outcome = "success" if random.random() < 0.75 else "fail"
        
        data.append({
            "system": "S2",
            "iteration": i,
            "failure_cost": cost,
            "reversibility": reversibility,
            "time_model": time_model,
            "freedom": freedom,
            "info_gain": info_gain,
            "outcome": outcome
        })
    return data

def generate_v7_data(n):
    """S3 (V7): 관찰 → 구조 → 실행 (완전 분업)"""
    data = []
    for i in range(n):
        freedom = random.random()
        
        if freedom > 0.5:
            cost = random.random() * 0.1
            reversibility = 0.8 + random.random() * 0.2
            time_model = "tau"
        else:
            cost = random.random() * 0.6
            reversibility = 0.3 + random.random() * 0.4
            time_model = "wall"
        
        info_gain = 0.4 + random.random() * 0.5
        
        outcome = "success" if random.random() < 0.85 else "fail"
        
        data.append({
            "system": "S3_V7",
            "iteration": i,
            "failure_cost": cost,
            "reversibility": reversibility,
            "time_model": time_model,
            "freedom": freedom,
            "info_gain": info_gain,
            "outcome": outcome
        })
    return data

s1_data = generate_s1_data(N_SAMPLES)
s2_data = generate_s2_data(N_SAMPLES)
v7_data = generate_v7_data(N_SAMPLES)

all_data = s1_data + s2_data + v7_data

with open("results/macro_micro_states.json", "w") as f:
    json.dump(all_data, f, indent=2)
print(f"✅ Generated {len(all_data)} state samples")

def count_outcomes(data):
    outcomes = {"success": 0, "fail": 0, "catastrophic": 0}
    for d in data:
        outcomes[d["outcome"]] += 1
    return outcomes

print("\n📊 Outcome Distribution:")
for name, data in [("S1", s1_data), ("S2", s2_data), ("V7", v7_data)]:
    outcomes = count_outcomes(data)
    cat_rate = outcomes["catastrophic"] / len(data) * 100
    print(f"  {name}: catastrophic={outcomes['catastrophic']} ({cat_rate:.1f}%)")

fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor='white')

color_map = {"success": "#4CAF50", "fail": "#FFC107", "catastrophic": "#F44336"}

for ax, (name, data) in zip(axes, [("S1: No Division", s1_data), 
                                     ("S2: Weak Division", s2_data), 
                                     ("V7: Full Structure", v7_data)]):
    freedoms = [d["freedom"] for d in data]
    costs = [d["failure_cost"] for d in data]
    colors = [color_map[d["outcome"]] for d in data]
    
    ax.scatter(freedoms, costs, c=colors, alpha=0.5, s=15, edgecolors='none')
    
    ax.axhline(y=0.5, color='#999', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0.5, color='#999', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.fill_between([0.5, 1.0], 0.5, 1.0, color='#ffcccc', alpha=0.2, zorder=0)
    
    cat_count = sum(1 for d in data if d["outcome"] == "catastrophic")
    ax.set_title(f"{name}\n(catastrophic: {cat_count})", fontsize=12, weight='bold')
    ax.set_xlabel("Freedom", fontsize=10)
    ax.set_ylabel("Failure Cost", fontsize=10)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#4CAF50', label='Success'),
    Patch(facecolor='#FFC107', label='Fail'),
    Patch(facecolor='#F44336', label='Catastrophic'),
    Patch(facecolor='#ffcccc', alpha=0.5, label='Danger Zone')
]
fig.legend(handles=legend_elements, loc='upper center', ncol=4, 
           bbox_to_anchor=(0.5, 1.02), frameon=False, fontsize=10)

plt.suptitle("Freedom × Failure Cost Distribution\n", fontsize=14, weight='bold', y=1.08)

plt.tight_layout()
plt.savefig("../images/freedom_cost_distribution.png", dpi=200, facecolor='white', 
            bbox_inches='tight', pad_inches=0.3)
print("\n✅ Saved: images/freedom_cost_distribution.png")
plt.close()

print("\n🔍 Key Observation:")
print("   V7: High freedom points cluster in low-cost region")
print("   S1/S2: High freedom × High cost region has catastrophic events")
print("   → V7 structurally removes the danger zone")
