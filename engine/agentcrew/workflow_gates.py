"""Track approval boundaries by workflow position, including repeated roles."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from .routing import Routing, _is_human_step


@dataclass(frozen=True)
class HumanBoundary:
    step_index: int
    role_index: int
    label: str
    remaining_workflow: str


class WorkflowGates:
    """An approval is tied to a boundary, never merely to a role name."""

    def __init__(self, routing: Routing):
        self.routing = routing
        steps = routing.execution_steps()
        role_index = 0
        self.boundaries: list[HumanBoundary] = []
        for index, step in enumerate(steps):
            if _is_human_step(step):
                if index < len(steps) - 1:
                    self.boundaries.append(HumanBoundary(
                        index, role_index, step, " -> ".join(steps[index + 1:]),
                    ))
            else:
                role_index += 1
        self.acknowledged: set[int] = set()

    def before(
        self, role_index: int, role: str, accept: Callable[[Routing, str], bool],
    ) -> tuple[HumanBoundary | None, list[HumanBoundary]]:
        """Return the refused boundary and approvals newly obtained at this step."""

        approved: list[HumanBoundary] = []
        for boundary in self.boundaries:
            if boundary.role_index != role_index or boundary.step_index in self.acknowledged:
                continue
            decision_routing = replace(
                self.routing,
                human_decisions=[boundary.label, *self.routing.human_decisions],
            )
            if not accept(decision_routing, role):
                return boundary, approved
            self.acknowledged.add(boundary.step_index)
            approved.append(boundary)
        return None, approved
