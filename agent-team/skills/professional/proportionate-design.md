# Skill: Proportionate Design

## Purpose

Use this skill when creating, reviewing, or fixing SVG diagrams for documentation, GitHub READMEs, technical explainers, social previews, architecture diagrams, workflow diagrams, before/after diagrams, and product visuals.

The goal is to produce diagrams that are visually professional, readable, aligned, GitHub-safe, and exportable to crisp PNG previews.

---

## Applies when

Use this skill when work involves:

- SVG diagrams
- README visuals
- architecture diagrams
- workflow diagrams
- before/after diagrams
- social preview graphics
- technical explainer visuals
- product visuals
- alignment, spacing, hierarchy, or proportion fixes
- GitHub-safe SVG rendering
- PNG preview export from SVG

---

## Detection triggers

Load this skill if the task or repo contains:

```yaml
triggers:
  text:
    - SVG
    - diagram
    - workflow graphic
    - before and after
    - social preview
    - README visual
    - visual asset
    - alignment
    - spacing
    - proportion
    - GitHub rendering
    - PNG preview
  files:
    - "*.svg"
    - "docs/assets/*.svg"
    - "docs/assets/*.png"
    - "README.md"
```

---

## Instructions

Act as an expert SVG designer, professional diagram designer, and technical visual editor.

When given an SVG, screenshot, rough diagram, or design request:

- Identify layout, alignment, spacing, hierarchy, and rendering issues.
- Improve text readability, contrast, sizing, and visual hierarchy.
- Fix SVG rendering inconsistencies across GitHub, browsers, and documentation sites.
- Keep the diagram clean, professional, minimal, and easy to understand.
- Preserve the original meaning while improving visual quality.
- Produce a corrected SVG and, when possible, PNG previews at 1x and 2x.

Use these design principles:

- Strong visual hierarchy: title, subtitle, section labels, card labels, and helper text should be clearly distinct.
- Consistent spacing: align cards, arrows, labels, and groups to a clean grid.
- High readability: text must remain readable in GitHub README and documentation views.
- Balanced composition: avoid elements that feel floating, crowded, or uneven.
- Clear flow: arrows should start and end at logical anchor points.
- Compact but not cramped: preserve whitespace around text and between objects.
- Professional color system: use soft backgrounds, strong text, subtle borders, and restrained accents.
- Predictable geometry: use consistent corner radius, stroke width, card sizes, and arrow styles.

### SVG rendering rules

For text:

- Avoid relying on `dominant-baseline: middle`; it can render inconsistently.
- Prefer explicit `x` and `y` positioning for text.
- For centered labels, use `text-anchor="middle"` and carefully adjusted `y` values.
- Use standard font weights such as `400`, `500`, `600`, `700`, and `800`.
- Avoid nonstandard weights like `720` or `750`.
- Use GitHub-safe font stacks:

```css
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
```

- Make primary labels dark and bold.
- Make helper text darker than usual muted gray if the diagram will appear small.
- Prefer these text colors:

```css
.ink { fill: #0f172a; }
.muted { fill: #334155; }
.softMuted { fill: #475569; }
```

For layout:

- Use a fixed `viewBox`.
- Align major elements to a grid.
- Center groups mathematically, not by visual guessing.
- Give text enough padding inside cards.
- Keep arrows centered relative to their source and target shapes.
- For multi-step flows, keep all horizontal arrows on the same baseline unless intentionally changing lanes.
- When routing from one large group to another, use clean elbow connectors instead of awkward diagonal or off-center arrows.

For arrows:

- Use consistent arrow stroke width.
- Use `markerUnits="userSpaceOnUse"` for stable arrowhead rendering.
- Keep arrowheads from overlapping cards.
- Start and end arrows with a small gap between shapes.
- Use elbow paths for complex routing.
- Prefer this marker pattern:

```svg
<marker id="arrowhead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse">
  <path d="M2,2 L10,6 L2,10 Z" fill="#64748b"/>
</marker>
```

For shapes:

- Use consistent card radii, usually `rx="10"` or `rx="12"`.
- Use subtle strokes instead of heavy borders.
- Avoid pure black borders unless needed.
- Prefer light fills with clear contrast.
- Use calm, readable palettes such as:

```css
.bg { fill: #ffffff; }
.band { fill: #f8fafc; }
.card { fill: #ffffff; stroke: #cbd5e1; stroke-width: 2; }
.blue { fill: #eff6ff; stroke: #93c5fd; stroke-width: 2; }
.green { fill: #f0fdf4; stroke: #86efac; stroke-width: 2; }
.yellow { fill: #fffbeb; stroke: #fbbf24; stroke-width: 2; }
.arrow { stroke: #64748b; stroke-width: 3.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
```

Preferred working process:

1. Inspect the supplied SVG or image.
2. Identify alignment, typography, contrast, and rendering issues.
3. Rewrite the SVG cleanly rather than applying messy patch fixes.
4. Use consistent classes and reusable styles.
5. Render the SVG to PNG to visually verify it.
6. Adjust text positions manually if needed.
7. Export final files.

---

## Testing guidance

Validate visuals by checking:

- the SVG parses as XML
- the SVG is valid enough for browser and GitHub rendering
- text stays inside its parent boxes
- grouped boxes fully contain their child elements
- repeated nodes share consistent dimensions or intentional variation
- arrows start and end with adequate spacing
- the asset remains readable at common README widths
- the exported PNG matches the SVG layout

Useful checks:

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/assets/example.svg')"
file docs/assets/example.svg
git diff --check
```

When a renderer is available, export and inspect a PNG preview. For social previews, export at the target platform size.

---

## Review checklist

Before finalizing any SVG, check:

- all cards align consistently
- arrows are centered on the objects they connect
- title is readable at small preview sizes
- helper text is readable on GitHub
- text labels are vertically positioned consistently
- every card has enough padding around text
- flow direction feels obvious
- border widths, corner radii, and colors are consistent
- SVG avoids `dominant-baseline` alignment issues
- font weights are standard
- diagram still works if the preferred font is unavailable
- exported PNG matches the SVG layout
- final diagram feels calm, modern, readable, precise, and trustworthy

---

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - relying_on_dominant_baseline_for_centering
  - using_nonstandard_font_weights
  - hand_tuning_every_text_label_without_a_grid
  - using_different_padding_for_equivalent_boxes
  - letting_group_backgrounds_clip_or_exclude_child_nodes
  - placing_arrows_off_the_centerline_of_connected_shapes
  - letting_arrowheads_touch_or_overlap_boxes
  - relying_on_full_size_viewing_when_the_asset_appears_small_in_readme
  - adding_decorative_complexity_that_reduces_comprehension
  - using_visual_assets_that_imply_a_vendor_specific_workflow_unless_intended
```

Common fixes:

- Replace `dominant-baseline: middle` with explicit `y` positioning.
- Increase muted text contrast.
- Increase small text size for documentation diagrams.
- Replace nonstandard font weights with standard weights.
- Align all boxes to a consistent grid.
- Use elbow arrows for multi-level flows.
- Widen boxes when labels feel cramped.
- Add more internal padding around text.
- Ensure arrowheads do not touch or overlap boxes.
- Export larger PNG previews for social previews and README images.

---

## Output note

When fixing or creating a diagram, provide:

- corrected `.svg` file
- `.png` preview
- `2x` PNG preview when possible
- short summary of what improved

If relevant, include:

```md
## Skills Applied
- proportionate-design
```
