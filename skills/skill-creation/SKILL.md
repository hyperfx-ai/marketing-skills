---
name: skill-creation
description: Create user skills with proper folder structure and YAML frontmatter. Use when the user wants to create a custom skill, document a repeatable workflow as a skill, or fix a skill's structure and metadata.
use_cases:
  - Create custom workflow guides
  - Document repeatable processes
  - Build skill folders with SKILL.md
triggers:
  - create skill
  - make skill
  - new skill
  - skill guide
  - build skill
requires_toolkits: []
suggested_toolkits: []
always_include: true
---

# Creating User Skills

Skills are **folders** (not single files) with a required structure.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Skills system (built into Hyper)** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Required Folder Structure

```
/skills/my-skill-name/           <- Folder name must be slug format (lowercase, hyphens)
├── SKILL.md                     <- REQUIRED: Main instructions with YAML frontmatter
├── REFERENCE.md                 <- Optional: Additional reference documentation
├── references/                   <- Optional: Folder for multiple reference docs
│   ├── api-docs.md
│   └── examples.md
└── scripts/                     <- Optional: Executable scripts
    └── helper.py
```

## SKILL.md Format (Required)

```markdown
---
name: my-skill-name
description: Brief description of what this skill does (required, max 1024 chars)
use_cases:
  - Use case 1
  - Use case 2
triggers:
  - keyword1
  - keyword2
requires_toolkits:
  - toolkit_id
suggested_toolkits:
  - optional_toolkit_id
---

# Skill Guide Title

Your step-by-step instructions here...
```

## Creating a Skill (Recommended: Use skills_create Tool)

The `skills_create` tool is the most reliable way to create skills:

```python
# Create a new skill using the skills_create tool
skills_create(
    name="my-skill-name",
    description="Brief description of what this skill does",
    triggers=["keyword1", "keyword2"],
    content="""# My Skill Guide

Step-by-step instructions here...

## Section 1
Details...

## Section 2
More details...
"""
)
```

The tool automatically:
- Creates the folder structure
- Generates proper YAML frontmatter
- Validates the skill name (slug format)
- Sets up semantic search indexing

## Alternative: Using Heredoc Syntax

Heredocs now work for VFS paths:

```python
shell("""cat > /skills/my-skill-name/SKILL.md << 'EOF'
---
name: my-skill-name
description: Brief description of what this skill does
use_cases:
  - Use case 1
triggers:
  - keyword1
---

# My Skill Guide

Step-by-step instructions...
EOF""")
```

## Other Skill Tools

```python
# List all your skills
skills_list()

# Update a specific field on a skill
skills_update(skill_id="skill_...", field="description", value="New description")

# Delete a skill
skills_delete(skill_id="skill_...")
```

## Critical Rules

1. **Slug format required**: Skill folder names MUST use lowercase letters, numbers, hyphens only (e.g., `my-skill-name`)
2. **Name field must match**: The `name` field in SKILL.md frontmatter must also be slug format
3. **Description required**: The `description` field is required and cannot be empty
4. **Folders only**: Do NOT create flat files like `/skills/my-skill.md` - skills must be folders with `SKILL.md` inside
5. **Curated is read-only**: Skills in `/skills/_hyper/` are read-only and cannot be modified

## Copying a Curated Skill to Customize

```python
# Copy entire skill folder to user space
shell("cp -r /skills/_hyper/example-skill /skills/my-custom-skill")

# Review current content
shell("cat /skills/my-custom-skill/SKILL.md")

# Update with your customizations using the skills_update tool or heredoc
```

## Skill Discovery Commands

```python
# List all your skills
skills_list()

# Browse all curated skills
shell("ls /skills/_hyper/")

# Browse a skill folder
shell("ls /skills/_hyper/skill-name/")

# Read a skill
shell("cat /skills/_hyper/skill-name/SKILL.md")

# Search skills by topic
shell("hyper-search 'topic' /skills/")
```
