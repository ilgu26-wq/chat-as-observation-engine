"""
Judgment vs Execution Experiment

Research Question:
What determines AI failure and success:
Judgment capability, Execution capability, or Execution structure?

Core Hypothesis:
High execution without structure produces catastrophic variance,
regardless of judgment quality.
"""

import json
import random
import statistics
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime


class AgentType(Enum):
    JUDGMENT_ONLY = "A"
    HIGH_EXECUTION = "B"
    DELAYED_EXECUTION = "C"
    STRUCTURED_V7 = "D"


@dataclass
class TaskState:
    ambiguity: float
    condition_change_at: int
    irreversible_cost: float
    goal_revealed_at: int


@dataclass
class ExperimentResult:
    agent: str
    run_id: int
    outcome_quality: float
    is_catastrophic: bool
    time_to_action: int
    execution_count: int
    variance_contribution: float


@dataclass
class DistributionMetrics:
    agent: str
    mean: float
    std: float
    iqr: float
    catastrophic_rate: float
    avg_time_to_action: float
    n_runs: int


class Task:
    def __init__(self, seed: int):
        random.seed(seed)
        self.state = TaskState(
            ambiguity=random.uniform(0.3, 0.9),
            condition_change_at=random.randint(2, 5),
            irreversible_cost=random.uniform(0.1, 0.5),
            goal_revealed_at=random.randint(3, 7)
        )
        self.current_turn = 0
        self.executed = False
        self.outcome = None
    
    def get_judgment_signal(self) -> float:
        base = 0.5 + random.gauss(0, 0.1)
        if self.current_turn < self.state.goal_revealed_at:
            base += random.gauss(0, self.state.ambiguity * 0.3)
        return max(0, min(1, base))
    
    def execute(self, quality: float) -> float:
        if self.executed:
            return self.outcome
        
        self.executed = True
        
        if self.current_turn < self.state.condition_change_at:
            penalty = self.state.irreversible_cost * self.state.ambiguity
            self.outcome = quality - penalty + random.gauss(0, 0.2)
        else:
            self.outcome = quality + random.gauss(0, 0.05)
        
        return self.outcome
    
    def advance(self):
        self.current_turn += 1


class Agent:
    def __init__(self, agent_type: AgentType):
        self.type = agent_type
        self.judgments = []
        self.executions = 0
        self.first_execution_turn = None
    
    def decide(self, task: Task) -> Optional[float]:
        signal = task.get_judgment_signal()
        self.judgments.append(signal)
        
        if self.type == AgentType.JUDGMENT_ONLY:
            return None
        
        elif self.type == AgentType.HIGH_EXECUTION:
            if signal > 0.4:
                return self._execute(task, signal)
        
        elif self.type == AgentType.DELAYED_EXECUTION:
            if task.current_turn >= 3 and signal > 0.5:
                return self._execute(task, signal)
        
        elif self.type == AgentType.STRUCTURED_V7:
            if self._bar1_satisfied(task) and self._constraints_met(signal):
                return self._execute(task, signal)
        
        return None
    
    def _execute(self, task: Task, quality: float) -> float:
        if self.first_execution_turn is None:
            self.first_execution_turn = task.current_turn
        self.executions += 1
        return task.execute(quality)
    
    def _bar1_satisfied(self, task: Task) -> bool:
        return task.current_turn >= task.state.condition_change_at
    
    def _constraints_met(self, signal: float) -> bool:
        if len(self.judgments) < 2:
            return False
        
        recent = self.judgments[-2:]
        consistency = 1 - abs(recent[0] - recent[1])
        return consistency > 0.5 and signal > 0.45


def simulate(agent_type: AgentType, seed: int, max_turns: int = 10) -> ExperimentResult:
    task = Task(seed)
    agent = Agent(agent_type)
    
    outcome = None
    for _ in range(max_turns):
        result = agent.decide(task)
        if result is not None:
            outcome = result
        task.advance()
    
    if outcome is None:
        if agent_type == AgentType.JUDGMENT_ONLY:
            outcome = 0.3
        elif agent_type == AgentType.STRUCTURED_V7:
            outcome = 0.5
        else:
            outcome = 0.0
    
    is_catastrophic = outcome < 0.1 and agent.executions > 0
    
    return ExperimentResult(
        agent=agent_type.value,
        run_id=seed,
        outcome_quality=max(0, min(1, outcome)) * 10,
        is_catastrophic=is_catastrophic,
        time_to_action=agent.first_execution_turn or max_turns,
        execution_count=agent.executions,
        variance_contribution=abs(outcome - 0.5)
    )


def analyze_distribution(results: List[ExperimentResult]) -> DistributionMetrics:
    qualities = [r.outcome_quality for r in results]
    times = [r.time_to_action for r in results]
    catastrophic_count = sum(1 for r in results if r.is_catastrophic)
    
    sorted_q = sorted(qualities)
    n = len(sorted_q)
    q1 = sorted_q[n // 4]
    q3 = sorted_q[3 * n // 4]
    
    return DistributionMetrics(
        agent=results[0].agent,
        mean=statistics.mean(qualities),
        std=statistics.stdev(qualities) if len(qualities) > 1 else 0,
        iqr=q3 - q1,
        catastrophic_rate=catastrophic_count / len(results),
        avg_time_to_action=statistics.mean(times),
        n_runs=len(results)
    )


def run_full_experiment(n_runs: int = 100) -> Dict:
    print(f"\n{'='*60}")
    print("JUDGMENT VS EXECUTION EXPERIMENT")
    print(f"{'='*60}")
    print(f"Runs per agent: {n_runs}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    all_results = {}
    all_metrics = {}
    
    for agent_type in AgentType:
        print(f"Running Agent {agent_type.value} ({agent_type.name})...")
        results = [simulate(agent_type, seed) for seed in range(n_runs)]
        metrics = analyze_distribution(results)
        
        all_results[agent_type.value] = [asdict(r) for r in results]
        all_metrics[agent_type.value] = asdict(metrics)
        
        print(f"  Mean: {metrics.mean:.2f}, Std: {metrics.std:.2f}, "
              f"Catastrophic: {metrics.catastrophic_rate*100:.1f}%")
    
    print()
    print("="*60)
    print("HYPOTHESIS TESTING")
    print("="*60)
    
    A = all_metrics["A"]
    B = all_metrics["B"]
    C = all_metrics["C"]
    D = all_metrics["D"]
    
    h1_pass = B["std"] > A["std"] and B["std"] > D["std"]
    h2_pass = A["catastrophic_rate"] < 0.05
    h3_pass = D["std"] < B["std"] * 0.7
    
    print(f"\nH1: Var(B) > Var(A) and Var(B) > Var(D)")
    print(f"    B.std={B['std']:.3f}, A.std={A['std']:.3f}, D.std={D['std']:.3f}")
    print(f"    Result: {'PASS ✓' if h1_pass else 'FAIL ✗'}")
    
    print(f"\nH2: Catastrophic(A) ≈ 0")
    print(f"    A.catastrophic={A['catastrophic_rate']*100:.1f}%")
    print(f"    Result: {'PASS ✓' if h2_pass else 'FAIL ✗'}")
    
    print(f"\nH3: Var(D) << Var(B)")
    print(f"    D.std={D['std']:.3f}, B.std={B['std']:.3f}, ratio={D['std']/B['std']:.2f}")
    print(f"    Result: {'PASS ✓' if h3_pass else 'FAIL ✗'}")
    
    print()
    print("="*60)
    print("DISTRIBUTION COMPARISON")
    print("="*60)
    print(f"\n{'Agent':<25} {'Mean':>8} {'Std':>8} {'IQR':>8} {'Catast%':>8} {'τ':>6}")
    print("-"*60)
    for agent in ["A", "B", "C", "D"]:
        m = all_metrics[agent]
        print(f"{AgentType(agent).name:<25} {m['mean']:>8.2f} {m['std']:>8.3f} "
              f"{m['iqr']:>8.3f} {m['catastrophic_rate']*100:>7.1f}% {m['avg_time_to_action']:>6.1f}")
    
    experiment_data = {
        "experiment": "Judgment vs Execution",
        "timestamp": datetime.now().isoformat(),
        "n_runs": n_runs,
        "hypotheses": {
            "H1": {"description": "Execution amplifies variance", "result": h1_pass},
            "H2": {"description": "Judgment alone no catastrophe", "result": h2_pass},
            "H3": {"description": "Structure compresses variance", "result": h3_pass}
        },
        "metrics": all_metrics,
        "all_passed": h1_pass and h2_pass and h3_pass
    }
    
    return experiment_data


def save_results(data: Dict, filepath: str = "results/jve_results.json"):
    import os
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved to: {filepath}")


if __name__ == "__main__":
    results = run_full_experiment(n_runs=100)
    save_results(results)
    
    print("\n" + "="*60)
    if results["all_passed"]:
        print("ALL HYPOTHESES CONFIRMED ✓")
        print("Execution structure is the determining factor.")
    else:
        print("SOME HYPOTHESES FAILED")
        print("Review experimental design.")
    print("="*60)
