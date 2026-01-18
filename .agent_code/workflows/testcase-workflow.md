---
description: TEST CASE GENERATION WORKFLOW
---

# TEST CASE GENERATION WORKFLOW

> **GOAL:** Generate realistic, traceable test cases from Specs.
> **RULE:** Spec-Driven. No Assumptions. Real-world behavior.

## 1. INPUT INPUT & DECOMPOSITION
- **Inputs:** Spec, Roles, Constraints. If ambiguous -> STOP.
- **Decompose:** Atomic requirements (Functional, Non-functional, Error).
  - *Example:* `REQ-LOGIN-01`.

## 2. PERSONA & JOURNEY MODELING
- **Personas:** New User, Power User, Malicious User.
- **Journeys:** Entry -> Action -> System Response -> Exit.
  - Must include: Happy Path, Interrupted Flow, Abuse.

## 3. DERIVATION RULES (FAILURE-FIRST)
1. **Dimensions:** Valid, Invalid, Boundary, Timeout, Concurrency.
2. **Failure Rule:** Every Happy Path MUST have at least 1 Failure Case + 1 Recovery Case.

## 4. TEST CASE TEMPLATE (MANDATORY)
```markdown
### <ID> - <Title>
- **Reqs:** <IDs>
- **Persona:** <Name>
- **Preconditions:** <State>
- **Steps:** 1. Action...
- **Expected:** <Result>
- **Post:** <State>
- **Negative Notes:** <Edge cases>
```

## 5. VALIDATION
- **Matrix:** Every Req covered? Every Persona covered?
- **Realism:** Executable? Constraints respected?

## 6. OUTPUT
- File: `TEST_CASES.md`
- Format: Markdown Table or Template above.