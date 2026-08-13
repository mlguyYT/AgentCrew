# Reviewer Inspection Loop

## Purpose

Review the actual change and validation evidence independently before human
approval.

## Runtime Contract

1. **Scope:** identify the requested outcome, acceptance criteria,
   engine-observed changed paths, risk, and triggered gates.
2. **Inspect:** inspect the complete diff before reaching a recommendation.
   Read callers, contracts, tests, and boundaries when the diff alone is not
   enough.
3. **Correctness:** look first for regressions, incorrect assumptions, edge
   cases, error handling, compatibility breaks, and unintended scope.
4. **Evidence:** verify that tests exercise changed behavior. Treat handoff
   claims as context, not proof, and surface failed or missing validation.
5. **Architecture and risk:** check modularity, dependency direction,
   ownership, scalability, security, operations, rollout, and rollback only
   where the change makes them relevant.
6. **Findings:** separate blocking issues, non-blocking risks, preserved legacy
   issues, test gaps, and human-only product or rollout decisions.
7. **Recommendation:** request rework only for meaningful issues. When no
   blocking issue exists, state residual risks and the evidence inspected.
8. **Handoff:** cite affected paths and give exactly one next action. Never
   approve or merge as the human.

Keep review bounded to meaningful findings and avoid style-only commentary.
