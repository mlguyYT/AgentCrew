# Developer Execution Loop

## Purpose

Turn a routed task into a small, evidence-backed change without loading the
whole AgentCrew methodology.

Use this loop for implementation work. The selected recipe, Skills, project
instructions, and triggered gates refine it.

## Runtime Contract

1. **Contract:** identify the observable outcome, constraints, preserved
   behavior, and authoritative validation source.
2. **Preserve:** before opening or changing mutable evidence, data stores,
   generated state, or irreplaceable inputs, use a safe copy, snapshot, or
   read-only method.
3. **Baseline:** reproduce the defect or run the smallest relevant existing
   check before editing. If that is unsafe or unavailable, record why.
4. **Diagnose:** inspect callers, tests, contracts, and boundaries before
   choosing one bounded implementation hypothesis.
5. **Change:** make the smallest coherent edit that follows project
   conventions and preserves unrelated behavior.
6. **Verify:** run focused checks against behavior and acceptance criteria.
   Validate semantics, edge cases, and integration behavior when applicable;
   syntax or file shape alone is not enough.
7. **Audit:** inspect the final diff, changed paths, unexpected artifacts,
   failing checks, and triggered quality gates.
8. **Handoff:** report files changed, commands and outcomes, limitations,
   unresolved risks, and exactly one next action. If validation cannot run or
   does not apply, mark it `unavailable` or `not_applicable` and give the
   concrete limitation; do not imply that checks passed.

Do not claim completion after a failed check. Correct the diagnosed cause and
rerun the relevant check. After two unsuccessful correction loops, stop,
preserve the evidence, and report the blocker instead of making speculative
changes.

## Escalate

Escalate when scope, risk, public behavior, architecture, data handling, or
rollback difficulty becomes materially larger than the routed task.
