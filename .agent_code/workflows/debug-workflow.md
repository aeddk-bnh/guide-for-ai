---
description: AGENT DEBUG WORKFLOW
---

# AGENT DEBUG WORKFLOW

> **GOAL:** Fix bugs using **LOGS**, not guesses.
> **RULE:** No Reproduction = No Fix.

## 1. PRE-DEBUG CHECK
- **Code:** Syntax valid?
- **Env:** Logs accessible? Filter tools (`grep`) ready?
- **Action:** Fix build/add logs BEFORE debugging.

## 2. DEBUG LOOP
`Observe -> Isolate -> Instrument -> Execute -> Analyze -> Prove -> Fix`

1. **Observe:** Define expected vs actual.
2. **Isolate:** Find the "Suspect Window" (Last good state -> First bad state).
3. **Instrument:** Add **Structured Logs** (Entry/Exit/Decision/State).
   - *Rule:* Mark debug logs clearly (e.g. `[DEBUG]`).
4. **Execute:** Run reproduction. **Capture Logs.**
   - *Safety:* Read filtered logs ONLY (<300 lines). Don't flood Context.
5. **Analyze:** Find divergence.
   - *Loop:* If ambiguous, add MORE logs and repeat. **DO NOT GUESS.**
6. **Prove:** Root cause MUST be backed by specific log lines.

## 3. FIX & CLEANUP
1. **Fix:** Minimal change. No refactor.
2. **Cleanup (CRITICAL):** Remove `[DEBUG]` logs. Convert useful ones to `INFO`.
3. **Verify:** Re-run repro script. Confirm clean logs.

## 4. OUTPUT CONTRACT
- [ ] Failure Description.
- [ ] Log Evidence (Filtered).
- [ ] Root Cause Analysis.
- [ ] Fix Diff.
- [ ] **Cleanup Confirmation.**