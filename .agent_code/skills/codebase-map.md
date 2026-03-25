---
name: codebase-map
description: Explore an unfamiliar repository, identify major modules or components, their edit surfaces, and how they interact, then write or update a concise Markdown operating map for future coding, debugging, and review work. Use when asked to understand a codebase, map modules, document system structure, explain component relationships, or create or refresh a repo overview document.
---

# Codebase Map

## Goal
Create or refresh `docs/codebase-map.md` as a compact operating map for later coding work.

The document should help a future agent answer:
- what the repo does
- which modules matter
- where to edit for common changes
- what depends on what
- how to validate a change
- which areas are risky or still unclear

Only write the requested summary file unless the user asks for more.

## Output Path
- Use the path the user gives, if any.
- Otherwise write to `docs/codebase-map.md`.
- Create `docs/` if needed.
- If the file exists, update it in place.

## Workflow
1. Identify repo scope, entrypoints, stack, and top-level layout.
2. Group the codebase into major modules, services, packages, or subsystems.
3. For each important module, capture:
   - responsibility
   - key files
   - common edit points
   - main dependencies
   - main consumers
   - nearby tests or checks
4. Trace the important edges:
   - request flow
   - data flow
   - external integrations
   - background jobs or schedulers
   - config and environment loading
5. Record cross-cutting concerns:
   - auth
   - persistence
   - testing
   - build and deploy
   - hotspots or fragile coupling
6. Write the Markdown file with concise file-backed claims.

## Rules
- Prefer module-level summaries over file-by-file narration.
- Merge low-signal folders into broader modules.
- Anchor important claims with concrete file references.
- Mark uncertain relationships as `Inference:` or `Unknowns`.
- Optimize for future implementation, debugging, and review work.
- Keep the document dense and skimmable.

## Default Shape

```md
# Codebase Map

## Snapshot
- Purpose:
- Primary stack:
- Main runtimes:
- Entry points:

## Top-Level Layout
- `path/`: role

## Module Map
| Module | Role | Key files | Edit here when | Depends on | Used by |
| --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | ... |

## Interaction Map
- Request flow:
- Data flow:
- External integrations:
- Background work:

## Change Guide
- If changing ...
- If adding ...
- If debugging ...

## Validation Guide
- Main test or check commands:
- Fastest suites or files:
- Regression attention:

## Cross-Cutting Concerns
- Config and env:
- Auth:
- Persistence:
- Testing:
- Build and deploy:
- Hotspots:

## Unknowns
- ...
```

## Failure Handling
- If the repo is too large, document the explored scope and what is still uncovered.
- If module boundaries are unclear, keep the summary at folder level and say so.
- If the architecture is inconsistent, document the inconsistency instead of forcing a neat story.
