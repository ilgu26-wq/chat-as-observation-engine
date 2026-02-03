# EXP: Macro → Micro Division of Labor Validation

## Purpose (Macro Question)

```
왜 분업이 없는 시스템은 규모가 커질수록 반드시 붕괴하는가?
왜 V7 구조는 미시 단계로 갈수록 더 안정해지는가?
```

이 실험은 "잘 작동한다"를 보지 않는다.
→ **왜 작동할 수밖에 없는지를 검증한다.**

---

## Macro Hypotheses (System-Level)

### H0 (기각 대상)

실행 능력이 충분히 높으면
판단·실행을 분리하지 않아도 시스템은 안정적이다.

### H1 (대립 가설)

실행 능력이 커질수록
분업이 없는 시스템은 분산과 catastrophic risk가 증가한다.

### H2 (V7 가설)

분업 원리를 구조로 고정하면
규모가 커질수록 오히려 분산이 압축된다.

---

## Macro Structure Definition

### Comparison Systems

| System | 구조 |
|--------|------|
| S1 | 판단 + 실행 결합 |
| S2 | 판단 → 즉시 실행 |
| S3 | V7 (관찰 → 구조 → 실행) |

### Macro Metrics

| 지표 | 설명 |
|------|------|
| Mean Performance | 평균 성능 |
| Std | 분산 |
| Catastrophic Rate | 회복 불가 실패율 |
| Recovery Cost | 복구 비용 |
| Loop Stability | N iteration 생존 |

### Macro Prediction

```
규모(N)가 증가할수록:
- S1, S2: 분산↑ / catastrophic↑
- S3(V7): 분산↓ / catastrophic≈0
```

---

## Micro Descent (Macro → Micro)

"왜 그런지"를 보기 위해 시스템을 **미시 상태 분포**로 분해한다.

### Micro State Space (5 Axes)

각 행동은 다음 5개 축 좌표를 가진다:

| 축 | 범위 |
|----|------|
| Failure Cost | 0 → high |
| Reversibility | free → locked |
| Time Model | τ → wall-clock |
| Freedom | low → high |
| Information Gain | low → high |

---

## Micro Hypotheses

### h1 — Freedom–Cost Collision

자유도가 높은 상태에서 비용이 있는 행동이 발생하면
→ **catastrophic risk 급증**

### h2 — Time Model Conflict

τ 공간에서 결정된 판단을 wall-clock 공간에 즉시 투입하면
→ **tail risk 발생**

### h3 — Structure Absence

Bar1 + Constraint 없이 실행이 발생한 상태는
→ **분산 상한이 존재하지 않는다**

---

## Micro Experiment Design

### Step 1 — Action Log Collection

각 시스템에서 모든 실행을 다음 형태로 기록:

```python
{
    "state_id": str,
    "failure_cost": float,      # 0 ~ 1
    "reversibility": float,     # 0 (locked) ~ 1 (free)
    "time_model": str,          # "tau" or "wall_clock"
    "freedom": float,           # 0 ~ 1
    "info_gain": float,         # 0 ~ 1
    "outcome": float            # 0 ~ 10
}
```

### Step 2 — Distribution Comparison

**S1/S2:**
- High freedom × High cost 영역에 점 밀집

**S3 (V7):**
- High freedom은 cost=0 영역에만 존재
- cost>0 영역은 freedom 낮음

### Step 3 — Critical Boundary Check

```
Catastrophic는 항상
(freedom × cost) 임계선을 넘을 때 발생한다

V7은 이 경계를 구조로 차단한다.
```

---

## Macro–Micro Connection

| 거시 현상 | 미시 원인 |
|-----------|-----------|
| 분산 폭발 | 자유도–비용 충돌 |
| tail risk | 시간 모델 불일치 |
| 안정 누적 | 구조적 경계 유지 |

> **거시 성능은 미시 분포의 적분 결과다**

---

## Success Criteria

V7이 다음을 만족하면 가설 채택:

| 조건 | 기준 |
|------|------|
| Catastrophic 위치 | 원리 위반 지점에서만 발생 |
| V7 구조 | 해당 원리 위반 지점이 구조적으로 불가능 |
| Loop 안정성 | 반복 루프에서도 분포 형태 유지 |

---

## Experiment Meaning

이 실험은 말한다:

```
"V7이 잘 설계됐다" ❌

"V7은 실패가 발생할 수 없는
 상태공간만 허용한다" ⭕
```

---

## One-Line Conclusion

> **Systems don't fail because they lack intelligence.**
> **They fail because high freedom meets high cost without structure in between.**

---

## Next Steps

1. **5개 축 좌표계 한 장 시각화**
2. **원리 위반 시 붕괴 시뮬레이션**
3. **이 구조를 AI Safety 논문 포맷으로 재작성**

---

## Connection to Previous Experiments

| 이전 실험 | 본 실험 |
|-----------|---------|
| EXPERIMENT_JUDGMENT_VS_EXECUTION | 실행력 분산 검증 |
| EXPERIMENT_OBSERVER_EXECUTOR | 역할 분리 검증 |
| **MACRO_TO_MICRO_DIVISION** | **거시→미시 원인 검증** |
