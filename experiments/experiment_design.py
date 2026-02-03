#!/usr/bin/env python3
"""
CHAT INTERFACE EFFICIENCY EXPERIMENT
=====================================

Research Question:
Why is GPT-style chat (conversational interface) the most efficient?
And can we make it more efficient using V7 structure?

Core Hypotheses (V7-style):
H1 (Irreversibility Fit): User intent is not fixed before Bar1, 
    it converges through dialogue (τ accumulation).
H2 (τ Efficiency): Chat success rate improves with τ, 
    while form/one-shot plateaus.
H3 (V7-Optimized): Structured chat achieves same quality with fewer τ.

Conditions:
A = Free Chat (baseline GPT)
B = Form/One-shot (non-conversational)
C = V7-Structured Chat (STATE/Bar1/Constraint/τ-plan)
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
from pathlib import Path

@dataclass
class Turn:
    turn_idx: int
    user_intent_summary: str
    assistant_output_summary: str
    change_type: str  # "major", "minor", "none"
    violation_flag: bool = False

@dataclass
class ExperimentRun:
    task_id: str
    condition: str  # A, B, C
    start_prompt: str
    turns: List[Turn]
    final_output_path: Optional[str] = None
    
    # Metrics
    tau_success: int = 0
    time_min: float = 0.0
    quality_score: float = 0.0  # 0-10
    violations: int = 0
    delta_intent: str = ""
    convergence_rate: float = 0.0
    notes: str = ""
    
    timestamp: str = ""

TASKS = [
    {
        "id": "T1",
        "name": "README Structure Rewrite",
        "description": "Improve readability and logical flow of README",
        "intent_ambiguity": "high"
    },
    {
        "id": "T2", 
        "name": "Experiment Report Formatting",
        "description": "Convert experiment results to institutional report format",
        "intent_ambiguity": "medium"
    },
    {
        "id": "T3",
        "name": "File/Folder Structure + Commit Messages",
        "description": "Organize files and write commit messages",
        "intent_ambiguity": "medium"
    },
    {
        "id": "T4",
        "name": "Document Link Structure",
        "description": "Design link structure between two documents",
        "intent_ambiguity": "high"
    },
    {
        "id": "T5",
        "name": "One-Page Concept Diagram",
        "description": "Create diagram explaining core concept (Storm/Bar1)",
        "intent_ambiguity": "very_high"
    },
    {
        "id": "T6",
        "name": "2-Minute Interview Explanation",
        "description": "Explain V7 in one paragraph for interview",
        "intent_ambiguity": "high"
    }
]

CONDITIONS = {
    "A": {
        "name": "Free Chat",
        "description": "Baseline GPT conversation, no structure",
        "protocol": None
    },
    "B": {
        "name": "Form/One-shot",
        "description": "Single input, single output (max 1 revision)",
        "protocol": "Fill form with all requirements upfront"
    },
    "C": {
        "name": "V7-Structured Chat",
        "description": "Structured dialogue with V7 grammar",
        "protocol": """
1. STATE: Declare current goal (document/code/design/summary/verify)
2. Bar1: Define success criterion in 1 line
3. Constraint: List forbidden actions/boundaries
4. τ-Plan: Set max turns (e.g., τ≤6)
5. Execute
"""
    }
}

def create_run(task_id: str, condition: str, start_prompt: str) -> ExperimentRun:
    return ExperimentRun(
        task_id=task_id,
        condition=condition,
        start_prompt=start_prompt,
        turns=[],
        timestamp=datetime.now().isoformat()
    )

def add_turn(run: ExperimentRun, intent: str, output: str, 
             change_type: str, violation: bool = False):
    turn = Turn(
        turn_idx=len(run.turns) + 1,
        user_intent_summary=intent,
        assistant_output_summary=output,
        change_type=change_type,
        violation_flag=violation
    )
    run.turns.append(turn)

def finalize_run(run: ExperimentRun, quality: float, delta_intent: str,
                 time_min: float, output_path: str = None, notes: str = ""):
    run.tau_success = len(run.turns)
    run.quality_score = quality
    run.delta_intent = delta_intent
    run.time_min = time_min
    run.final_output_path = output_path
    run.notes = notes
    run.violations = sum(1 for t in run.turns if t.violation_flag)
    
    # Calculate convergence rate (change reduction in later turns)
    if len(run.turns) >= 3:
        early = sum(1 for t in run.turns[:len(run.turns)//2] if t.change_type == "major")
        late = sum(1 for t in run.turns[len(run.turns)//2:] if t.change_type == "major")
        if early > 0:
            run.convergence_rate = 1 - (late / early)
        else:
            run.convergence_rate = 1.0

def save_run(run: ExperimentRun, base_path: str = "."):
    path = Path(base_path) / f"task_{run.task_id}_{run.condition}_{run.timestamp[:10]}.json"
    
    data = asdict(run)
    data["turns"] = [asdict(t) for t in run.turns]
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return path

def compare_conditions(runs: List[ExperimentRun]) -> dict:
    """Compare metrics across conditions."""
    by_condition = {"A": [], "B": [], "C": []}
    for r in runs:
        by_condition[r.condition].append(r)
    
    results = {}
    for cond, cond_runs in by_condition.items():
        if cond_runs:
            results[cond] = {
                "name": CONDITIONS[cond]["name"],
                "n": len(cond_runs),
                "avg_tau": sum(r.tau_success for r in cond_runs) / len(cond_runs),
                "avg_quality": sum(r.quality_score for r in cond_runs) / len(cond_runs),
                "avg_time": sum(r.time_min for r in cond_runs) / len(cond_runs),
                "failure_rate": sum(1 for r in cond_runs if r.quality_score < 6) / len(cond_runs),
                "avg_convergence": sum(r.convergence_rate for r in cond_runs) / len(cond_runs)
            }
    
    return results

def print_comparison(results: dict):
    print("\n" + "=" * 70)
    print("CHAT INTERFACE EFFICIENCY COMPARISON")
    print("=" * 70)
    
    print(f"\n{'Condition':<25} {'τ':>6} {'Quality':>8} {'Time':>8} {'Fail%':>8} {'Conv':>8}")
    print("-" * 70)
    
    for cond in ["A", "B", "C"]:
        if cond in results:
            r = results[cond]
            print(f"{r['name']:<25} {r['avg_tau']:>6.1f} {r['avg_quality']:>8.1f} "
                  f"{r['avg_time']:>7.1f}m {r['failure_rate']*100:>7.1f}% {r['avg_convergence']:>8.2f}")
    
    print("\n" + "=" * 70)
    print("JUDGMENT")
    print("=" * 70)
    
    if "A" in results and "C" in results:
        tau_reduction = (results["A"]["avg_tau"] - results["C"]["avg_tau"]) / results["A"]["avg_tau"] * 100
        print(f"\nτ Reduction (C vs A): {tau_reduction:.1f}%")
        
        if tau_reduction >= 20 and results["C"]["avg_quality"] >= results["A"]["avg_quality"]:
            print("H3 CONFIRMED: V7-Structured Chat is more efficient")
        else:
            print("H3 NOT CONFIRMED: Need more data or structure refinement")

if __name__ == "__main__":
    print("Chat Interface Efficiency Experiment Framework")
    print("=" * 50)
    print("\nTasks:")
    for t in TASKS:
        print(f"  {t['id']}: {t['name']} (ambiguity: {t['intent_ambiguity']})")
    
    print("\nConditions:")
    for c, info in CONDITIONS.items():
        print(f"  {c}: {info['name']}")
    
    print("\nTo run experiment:")
    print("  1. Create run: run = create_run('T1', 'A', 'initial prompt')")
    print("  2. Add turns: add_turn(run, intent, output, 'major')")
    print("  3. Finalize: finalize_run(run, quality=8.0, delta_intent='...', time_min=5.0)")
    print("  4. Save: save_run(run)")
