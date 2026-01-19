---
name: brainstorm
description: Structured thinking for ALL tasks: Coding, Debugging, Architecture, or Research.
---

# Brainstorming & Analysis Protocol

## Description
This skill acts as a cognitive framework for the agent. It forces a "Think before you act" pause. It guides the agent to explicitly identify its current Role (Architect, Coder, Debugger, etc.), analyze the User Request in deep context, and "brainstorm" the most effective plan of attack before writing any code. This is crucial for complex tasks to avoid backtracking.

## Prerequisites & Dependencies
- Access to `user_rules` (Memory).
- Access to `docs/context.md` (Project Context).
- Understanding of the agent's current toolset.

## Detailed Instructions

### 1. Role Alignment (Who am I right now?)
Based on the User's latest request and the `user_rules`, explicitly select your **Active Role**:
- **Requirements Analyst**: If the user is vague.
- **Solution Architect**: If creating new modules/structures.
- **Implementation (Coder)**: If writing logic/UI.
- **Debugger**: If fixing errors.
- **Reviewer**: If auditing/optimizing.

### 2. Requirement Audit (The "Missing Link" Check)
- **Domain Mapping:** Identify the implied domain (e.g., Auth, E-commerce, Data).
- **Base Knowledge Check:** What are the standard features this domain *requires* but user didn't mention?
    - *Example: User asked for "Login". Did they forget "Forgot Password", "Validation", "Error Handling"?*
- **Gap Action:**
    - If critical for stability: **Plan to implement silently** (as best practice).
    - If feature-level: **Add to "Clarification Questions"** list.

### 3. Contextual Deep Dive
1.  **Read `docs/context.md`**: What is the architectural truth?
2.  **Analyze Request**: identify hidden constraints (e.g., "Use vanilla CSS", "Performance critical").
3.  **Check Environment**: What files are open? What is the tech stack?

### 3. Impact & Risk Analysis (Crucial)
Before planning the "Happy Path", identify the risks:
- **Dependency Check**: If I modify File A, does it break File B? 
- **Destructive Actions**: Does this require deleting data/files? (Requires confirmation).
- **Unknowns & Research Strategy (ALL ROLES)**:
    - *Unknown Syntax/Error?* -> **Level 1**: Use `search_web`.
    - *Unknown API/Library?* -> **Level 2**: Use `read_url_content` (MANDATORY).
    - *Unknown UI/Behavior?* -> **Level 3**: Use `browser_subagent`.
- **Security**: Does this touch Auth, PII, or Secrets?

### 4. Brainstorming Execution (By Role)

#### If [Requirements Analyst]
- **Goal**: Convert ambiguity to clarity.
- **Checklist**:
    - [ ] **Research**: Have I checked similar apps/standards? (`search_web`).
    - [ ] Are the Acceptance Criteria independent and verifiable?
    - [ ] Are all edge cases defined (Empty states, Errors, Offline)?
    - [ ] **Outcome**: A list of clarifying questions or a formal Spec draft.

#### If [Solution Architect]
- **Goal**: Define robust structure.
- **Checklist**:
    - [ ] Does this fit the existing Design Patterns? (Don't invent new ones unnecessarily).
    - [ ] Are the Interface boundaries clear?
    - [ ] **Outcome**: A file tree draft, data models, and interface definitions.

#### If [Implementation (Coder)]
- **Goal**: Clean, working code.
- **Checklist**:
    - [ ] **Verification**: How will I verify this *works*? (Unit Test? Manual Check script?).
    - [ ] **Reuse**: Can I use existing utilities?
    - [ ] **Pseudocode**: Write the complex logic step-by-step in natural language first.
    - [ ] **Docs Check**: If using external lib, did I `read_url_content` the docs?
    - [ ] **Outcome**: A specific implementation plan (Step 1: Create file, Step 2: Add import...).

#### If [Debugger]
- **Goal**: Find root cause without guessing.
- **Checklist**:
    - [ ] **Reproduction**: Do I have a script to reproducible trigger the bug?
    - [ ] **Observability**: Do I have enough logs? If not, ADD LOGS FIRST.
    - [ ] **Hypothesis**: What is the mostly likely cause? (List top 3).
    - [ ] **Outcome**: A "Reproduction & Logging Plan".

### 5. Review & Output Plan
Before running tools, output a Thinking Block to the user.
**Self-Correction**: Ask yourself, "Is this plan the simplest way to achieve the goal?"

> **BRAINSTORMING**
> - **Role**: [Selected Role]
> - **Goal**: [Specific outcome]
> - **Impact Analysis**: [Dependencies/Risks]
> - **Unknowns**: [What needs investigation]
> - **Strategy**: [Step-by-step Plan]
> - **Verification**: [How success will be proven]

## Inputs
- **User Request**: The natural language task.
- **Current State**: Open files, active errors.

## Outputs
- **Structured Plan**: A clear roadmap in the chat response.
- **Context Update**: (Optional) Updates to `docs/context.md` if new facts emerge.

## Constraints & Rules
- **Never** skip the "Impact & Risk Analysis" step.
- **Always** define "Verification" before writing code.
- **Always** prefer investigation over assumption.
- **Always** use `docs/context.md` as the source of truth for architecture.

## Failure Handling
- If the plan is unclear, define a "Discovery Step" (e.g., "I need to read File X first").
- If the Role is ambiguous, ask the user: "Should I architect this first or just patch it?"

## FINAL CHECKLIST (BEFORE OUTPUT)
1. [ ] **Role:** Is it explicitly defined?
2. [ ] **Audit:** Did I check for missing requirements/edge cases?
3. [ ] **Research:** Did I select a Research Strategy (Level 1-3)?
4. [ ] **Risk:** Did I list potential failures?
