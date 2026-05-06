# Skill Validation Checklist

## Purpose

Use this checklist when adding or updating a Skill.

---

## File and registry

- Skill file is in the right category
- filename uses kebab-case
- registry entry points to the actual file
- Skill name is clear
- category is specific enough

---

## Required sections

Skill includes:

- Purpose
- Applies when
- Detection triggers
- Instructions
- Testing guidance
- Review checklist
- Anti-patterns

---

## Trigger quality

Triggers are:

- specific
- easy for an agent to detect
- not too broad
- based on task text, files, dependency files, imports, or symbols

---

## Safety

Skill does not:

- override human approval
- allow autonomous merge
- weaken secret handling
- bypass tests
- require unnecessary dependencies
- encourage unrelated refactors

---

## Execution quality

Instructions are:

- actionable
- concise
- technology-specific
- compatible with existing repository conventions

Testing guidance is:

- practical
- honest about commands
- clear about limitations

Review guidance is:

- focused on meaningful risks
- specific to the technology
- not style-only nitpicking

---

## Recommendation

Choose one:

- valid
- valid with notes
- rework required
- reject
