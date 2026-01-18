---
name: shadow_clone
description: Advanced Multi-Agent Orchestration skill. Allows the main agent to 'spawn' specialized sub-agents (Shadow Clones) with isolated prompts and restricted roles to solve complex tasks sequentially.
---

# Shadow Clone Protocol (Multi-Agent Orchestration)

## Description
This skill simulates a multi-agent system. Instead of trying to be "everything at once", the Main Agent creates ephemeral "Shadow Clones" (Sub-agents) to handle specific sub-tasks. Each Clone has a strict Persona, Goal, and Constraint set. The Main Agent acts as the Orchestrator, synthesizing the outputs.

## Prerequisites
- Complex task requiring multiple distinct mindsets (e.g., Creative Writer + Strict Auditor).

## Detailed Instructions

### 1. Orchestration Phase (The Setup)
- **Role:** Orchestrator.
- **Goal:** Break the user request into isolated sub-tasks.
- **Action:** Define the "Squad" of agents needed.
    - *Example:* "I need a `Researcher` to find APIs, then a `Coder` to implement, then a `Security_Auditor` to check."

### 2. Execution Phase (The Loop)
For each defined Agent, execute the following block STRICTLY:

#### [START SHADOW CLONE: <Agent_Name>]
> **SYSTEM PROMPT OVERRIDE:**
> You are NOW `<Agent_Name>`.
> **Goal:** `<Specific Goal>`
> **Constraints:** `<e.g., Read-Only, No assumptions, Output structured JSON only>`
> **Task:** `<Input from Orchestrator>`

**(Execute the task using tools. Do not reference the Main Agent's broad context unless necessary. Focus ONLY on the sub-task.)**

> **OUTPUT REPORT:**
> (Structured summary of findings/code to pass back to Orchestrator).
#### [END SHADOW CLONE: <Agent_Name>]

### 3. Synthesis Phase (The Collapse)
- **Role:** Orchestrator.
- **Action:** Read the **OUTPUT REPORT** from each clone.
- **Logic:**
    - If `Security_Auditor` failed -> Loop back to `Coder`.
    - If all green -> Combine outputs into final response for the User.

## Inputs
- **Complex Task:** A request requiring multi-stage reasoning.

## Outputs
- **Final Result:** A synthesized answer derived from sub-agent reports.

## Constraints & Rules
- **Isolation:** Clones should act as if they are experts in *only* their domain.
- **Reporting:** Clones must produce a "Handover Artifact" (Report/Code Block).
- **No Leaking:** Do not let a `Tester` clone start writing new features.

## Failure Handling
- If a Clone gets stuck, the Orchestrator must intervene, re-prompt, or spawn a `Debugger` clone.
