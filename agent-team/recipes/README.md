# Workflow Recipes

## Purpose

Workflow recipes are lightweight routing presets for common product-building outcomes.

They help agents move from a plain request to the right workflow without making users name roles, lanes, Skills, gates, or templates.

Recipes do not override AgentCrew safety rules, quality profiles, specialist routing, or human approval.

---

## Available Recipes

```yaml
recipes:
  bug-fix: focused defect correction
  feature: new or changed product capability
  refactor: behavior-preserving structural improvement
  docs-update: documentation, examples, changelog, release notes
  review: code, PR, architecture, or quality review
	  validation: testing, QA, regression, acceptance validation
	  research: source-backed investigation or option comparison
	  portfolio-project: portfolio, resume, interview, case-study, or target-role project scope
	  release: release readiness, changelog, version, PR preparation
  incident: production issue, outage, urgent regression, rollback decision
  skill-change: AgentCrew Skill creation or update
```

---

## Loading Rule

Load only the selected recipe file after request routing.

For tiny work, the recipe can be mentioned in the compact route summary without loading the full file.
