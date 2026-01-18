---
description: AGENT CODING RULES
---

# AGENT CODING RULES

> **PRIORITY:** Correctness > Clarity > Maintainability > Performance.
> **INVALID IF:** Logic is unproven, tests missing, or errors swallowed.

## 1. PRE-CODING CHECK
Before writing code, MUST define:
1. **Inputs/Outputs** & **Edge Cases.**
2. **Failure Modes** (How does it break?).
3. **Test Strategy** (How to prove it works?).

## 2. MINIMALISM & STYLE
- **Scope:** Implement ONLY required features. No premature optimization.
- **Functions:** Verb-based naming, Single Responsibility, Low nesting.
- **Files:** One clear purpose. No circular imports.

## 3. ROBUSTNESS & SECURITY
- **Errors:** Explicit handling. Fail fast. **NEVER swallow exceptions.**
- **Inputs:** Validate at boundaries.
- **Logs:** Structured, actionable logs for non-trivial logic. Explain WHY.

## 4. TESTING (MANDATORY)
- **Rule:** No new logic/fix without tests.
- **Quality:** Deterministic, Isolated, Readable (Given-When-Then).
- **Refactor:** Only refactor if tests exist. Behavior must remain identical.

## 5. REVIEW CHECKLIST (SELF-CORRECT)
- [ ] Code matches spec?
- [ ] No unused variables/imports?
- [ ] Error paths handled?
- [ ] Logs exist?
- [ ] Tests pass?

**ENFORCEMENT:** Violations = REJECT.