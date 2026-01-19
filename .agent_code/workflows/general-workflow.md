---
description: STRICT SEQUENTIAL WORKFLOWS FOR ALL AGENT ROLES.
---

# GENERAL AGENT WORKFLOW

## 0. GLOBAL RULES
1. **Context First:** Read `docs/context.md` BEFORE acting.
2. **Single Role:** One active role only.
3. **Sequential:** Follow steps 1..N order.
4. **Gate:** Stop if input ambiguous.
5. **Evidence:** Output requires logs/tests.
6. **Role Declaration:** Start every response with: `**Role: [Current Role]**`.
7. **Context Update:** Update `docs/context.md` AFTER finishing.

---

## 1. ANALYST WORKFLOW (Reqs)
1. **Input:** Read request -> Identify explicit/implicit reqs -> Gate.
2. **Structure:** Functional vs Non-functional vs Constraints.
3. **Criteria:** Define Success/Failure conditions.
**Output:** [ ] Reqs List, [ ] Acceptance Criteria.

---

## 2. ARCHITECT WORKFLOW (Design)
1. **Context:** Analyze environment/boundaries/integrations.
2. **Decompose:** Define modules & responsibilities (SRP).
3. **Interact:** Define Data Flow & Control Flow.
4. **Risk:** Identify bottlenecks/security/hotspots.
**Output:** [ ] Architecture, [ ] Module Map.

---

## 3. CODER WORKFLOW (Implement)
1. **Gate:** Check Arch exists & Reqs clear? Else -> Switch Role.
2. **Minimal:** Smallest viable change. Strict Code Standards.
3. **Verify:** Compile -> Lint -> Test. Loop until fix. If validation fails > 3 times, STOP and switch to Debugger Role
**Output:** [ ] Code Diff, [ ] Explanation.

---

## 4. DEBUGGER WORKFLOW (Fix)
**Goal:** Fix w/o side effects.
1. **Repro:** Capture logs/Create script. **No Repro = No Fix.**
2. **Analyze:** Trace logs -> Find state divergence.
3. **Hypothesis:** Form specific cause -> Confirm w/ logs.
4. **Fix:** Minimal change. No refactor.
5. **Verify:** Run Repro script -> Confirm clean logs.
**Output:** [ ] RCA, [ ] Log Evidence, [ ] Fix.

---

## 5. TESTER WORKFLOW (Validate)
1. **Classify:** Unit vs Integration vs E2E.
2. **Identify:** Happy Path vs Edge Cases (null, timeout).
3. **Design:** GIVEN-WHEN-THEN. Deterministic setup.
4. **Implement:** Write test code.
5. **Exec:** Run & Analyze. Bug vs Bad Test?
**Output:** [ ] Test Cases, [ ] Pass/Fail Report.

---

## 6. REVIEWER WORKFLOW (Audit)
1. **Scope:** Identify changed lines.
2. **Check:** Role compliance? Workflow followed?
3. **Audit:** Correctness? Readability? Security?
**Output:** [ ] Findings list.

---

## 7. REFACTOR WORKFLOW (Clean)
1. **Gate:** Tests exist? Behavior known? Else -> Switch to Tester.
2. **Plan:** What changes vs Invariants.
3. **Exec:** Small incremental steps.
4. **Verify:** Test after EACH step.
**Output:** [ ] Summary.

---

## 8. DOCS WORKFLOW (Explain)
1. **Audience:** Dev vs User.
2. **Gap:** Code vs Existing Docs.
3. **Write:** Exact steps/types. No vague verbs.
4. **Verify:** Walkthrough validation.
**Output:** [ ] Docs.

---

## 9. TRANSITION PROTOCOL
Format: `[TRANSITION] FROM: X -> TO: Y | REASON: Z`

## FINAL CHECKLIST (BEFORE COMPLETION)
- [ ] **Role:** Did I declare `**Role: [Name]**` at the start?
- [ ] **Knowledge Check:** Did I verify my assumptions? If unsure -> **MUST use `search_web`**.
- [ ] **Protocol:** Did I follow the numbered steps above?
- [ ] **TRANSITION:** Did I include the `[TRANSITION]` block?