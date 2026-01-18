---
description: EXECUTION FLOW TESTING WORKFLOW
---

# EXECUTION FLOW TESTING WORKFLOW

> **GOAL:** Validate REAL runtime behavior matches Design.
> **SCOPE:** End-to-End flows, State transitions, Resources.

## 1. ANALYSIS & FLOW GRAPH
- **Inputs:** Source code, Entry points (main, API, events).
- **Map:** Build **Functional Flow Graph** (Nodes = State/Logic/SideFX).
- **Rule:** Define ALL error/timeout paths.

## 2. SCENARIO DESIGN (REALISM)
- **Scenarios:** Cold Start, Network Fail, Concurrent Access, Crash Recovery.
- **Rule:** Test **Negative Cases** explicitly. Silent success on failure = Critical Bug.

## 3. VALIDATION LOOP
For each Step in Flow:
1. **Pre-check:** Inputs, State, Resources (Memory/Locks).
2. **Execute:** Run step (Real or Sim).
3. **Verify:** Output correct? Side effects? Cleanup?
4. **Compare:** Match against `TEST_CASES.md` (if exists).

## 4. CONFLICT DETECTION
- **Resources:** Leaks? Deadlocks? Race Conditions?
- **Env:** Permissions? Battery policies?

## 5. INSTRUMENTATION (NO BLIND DEBUG)
- If specific behavior unclear -> Add **Flow Logs** (State Transitions) & **Resource Logs**.

## 6. OUTPUT ARTIFACTS
1. **Flow Report:** Valid/Invalid steps.
2. **Defect List:** Critical/High/Med/Low.
   - *Actionable descriptions.*

**GOLDEN RULE:** Real execution behavior > Documentation.