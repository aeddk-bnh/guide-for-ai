---
description: LEAD ARCHITECTURE WORKFLOW
---

# LEAD ARCHITECTURE WORKFLOW

## INPUTS
- `docs/spec.md`

## OUTPUTS (MANDATORY)
1. **Config:** `technical_stack.md`, `.env.example`, infra configs.
2. **Design:** `system_structure.md`, `data_models.md` (DTOs), `api_contracts.md` (Interfaces), `module_breakdown.md`.
3. **Scaffold:** `src/**/*`, `tests/**/*` (Skeletons only).
4. **Tasks:** `implementation_task_*.md`, `testing_task_*.md`.

---

## WORKFLOW STEPS

### 1. ANALYSIS & STACK
- Analyze `spec.md` for loose coupling opportunities.
- Define Tech Stack (Libs, Frameworks).
- **Out:** `technical_stack.md`.

### 2. CONTRACTS & TOPOLOGY (CRITICAL)
- **Data Models:** Define global DTOs/Types first. **Out:** `data_models.md`.
- **API Contracts:** Define Module Interfaces (signatures). **Out:** `api_contracts.md`.
- **Typology:** Map modules & dependencies. **Out:** `system_structure.md`.

### 3. SCAFFOLDING & MOCKS
- Generate folder structure `src/`, `tests/`.
- **Implement Types:** Write code for `data_models.md`.
- **Generate Mocks:** Create Mock implementations for ALL Interfaces in `api_contracts.md`.
- **Skeletons:** Create code shells with TODOs.

### 4. TASK GENERATION
- **Impl Tasks:** Create `implementation_task_<mod>.md`.
  - Content: Role=Coder, Context, Permissions, specific TODO mappings.
- **Test Tasks:** Create `testing_task_<mod>.md`.
  - Content: Role=Tester, Strategy=Mocked Unit Tests.

### 5. VERIFICATION
- Audit: Every TODO links to a Task File?
- Audit: Every Contract has a Mock?
- Run basic build/install check.

---

## COMPLETION CRITERIA
- Project runs.
- Tasks are self-contained (no cross-reading needed).
- All Mocks exist.