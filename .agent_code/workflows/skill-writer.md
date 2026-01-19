---
description: SKILL WRITER WORKFLOW
---

# SKILL WRITER WORKFLOW

## PURPOSE
Generate high-quality, executable `SKILL.md` files in `.gemini/antigravity/skills/<skill_name>/`.

## 1. INPUT COLLECTION
- Define: Purpose, Tools, Environment, Constraints.
- **Rule:** If input missing -> STOP & Ask.

## 2. OUTPUT LOCATION (RULE)
1. **Target:** `.gemini/antigravity/skills/<skill_name>/`
2. **Action:** Create directory and `SKILL.md`.

## 3. FILE TEMPLATE (MANDATORY)
File MUST start with YAML frontmatter:

```markdown
---
name: <snake_case_name>
description: <One-line summary>
---

# <Human Readable Name>

## Description
<What/Why/When>

## Prerequisites
- <Tools/Dependencies>

## Detailed Instructions
<Step-by-step logic>

## Inputs
- <Name>: <Type> - <Desc>

## Outputs
- <Name>: <Type> - <Desc>

## Constraints
- <Must/Must Not>

## Failure Handling
- <Recovery steps>
```

## 4. VALIDATION CHECKLIST
- [ ] YAML Frontmatter valid?
- [ ] Folder created correctly?
- [ ] No vague "marketing" language?
- [ ] Tested/demonstrable?

**CORRECTION:** If validation fails -> Refactor -> Re-check.