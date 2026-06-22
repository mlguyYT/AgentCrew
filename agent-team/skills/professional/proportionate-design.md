# Skill: Proportionate Design

## Purpose

Use this skill for diagrams, SVGs, documentation visuals, and other structured visual assets where alignment, spacing, hierarchy, and proportion affect readability.

This skill helps agents create visuals that look intentional instead of manually offset or uneven.

---

## Applies when

Use this skill when work involves:

- SVG diagrams
- README visuals
- architecture diagrams
- flow diagrams
- visual documentation assets
- box-and-arrow layouts
- alignment, spacing, or proportion fixes
- diagrams intended for GitHub rendering

---

## Detection triggers

Load this skill if the task or repo contains:

```yaml
triggers:
  text:
    - SVG
    - diagram
    - workflow graphic
    - visual asset
    - alignment
    - spacing
    - proportion
    - README visual
    - box layout
  files:
    - "*.svg"
    - "docs/assets/*.svg"
    - "README.md"
```

---

## Instructions

When creating or editing structured visuals:

- Establish a simple grid before placing elements.
- Use consistent margins, padding, box sizes, corner radius, and stroke widths.
- Center text inside boxes with `text-anchor="middle"` or a shared centering class.
- Prefer calculated center points over hand-tuned text offsets.
- Align related elements on common x/y axes.
- Keep arrows visually centered between source and target shapes.
- Give group containers enough padding around every child element.
- Use a clear hierarchy: title, explanatory text, group labels, item labels, metadata.
- Keep the visual readable at GitHub README size, not only at full resolution.
- Avoid one-off coordinates when a repeated pattern should be regular.

For SVGs, prefer reusable classes:

```svg
<style>
  .center { text-anchor: middle; dominant-baseline: middle; }
</style>
```

Use left alignment only for paragraph-like text or intentional section labels. Use centered alignment for labels inside cards, pills, nodes, and diagram boxes.

---

## Testing guidance

Validate visuals by checking:

- the SVG is valid enough for the browser and GitHub to render
- text stays inside its parent boxes
- grouped boxes fully contain their child elements
- repeated nodes share consistent dimensions or intentional variation
- arrows start and end with adequate spacing
- the asset remains readable at common README widths

Useful checks:

```bash
file docs/assets/example.svg
git diff --check
```

If a renderer is available, inspect a rasterized preview before shipping.

---

## Review checklist

Reviewers should check:

- text is centered or intentionally aligned
- no label appears manually drifted inside a box
- boxes have enough padding around text
- group containers include all child elements
- spacing between related elements is consistent
- visual hierarchy is understandable within a few seconds
- colors have enough contrast and do not create a one-note palette
- the asset supports the surrounding documentation instead of adding clutter

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - hand-tuning every text label independently
  - using different padding for visually equivalent boxes
  - letting group backgrounds clip or exclude child nodes
  - placing arrows off the centerline of connected shapes
  - relying on full-size viewing when the asset appears small in README
  - adding decorative complexity that reduces comprehension
  - using visual assets that imply a vendor-specific workflow unless intended
```

---

## Output note

If relevant, include:

```md
## Skills Applied
- proportionate-design
```
