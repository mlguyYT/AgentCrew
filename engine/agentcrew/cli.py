"""agentcrew-engine — Python engine for the AgentCrew methodology.

The methodology lives in agent-team/ (roles, playbooks, templates, classifier).
The engine executes that methodology against an LLM.

Subcommands:
  route   Show what the classifier would route this task to (no execution).
  run     Classify, human-gate the routing, execute the workflow.
  doctor  Verify the methodology link works (root resolves, classifier runs).
  models  Show recommended local models per role.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from .agentcrew_root import AVAILABLE_ROLES, find_agentcrew_root
from .routing import Routing, classify, render_markdown as render_routing_md


def _emit(event: dict) -> None:
    """Emit one JSON line to stdout. Used by --from-agent mode so host agents
    can parse and render events inline."""
    sys.stdout.write(json.dumps(event, separators=(",", ":"), default=str) + "\n")
    sys.stdout.flush()


def _run_from_agent(*, task, project, root, provider, models, routing_approver) -> int:
    """Execute a run and emit a stream of JSON-lines events the host agent
    can parse and render in its chat surface.

    Event schema (every event has `event` and `ts` (UNIX seconds)):
      {"event": "routing", "lane": "...", "risk": "...", "recipe": "...",
        "workflow": "...", "acting_roles": [...], "specialists": [...],
        "gates": [...], "task": "..."}
      {"event": "routing_rejected"} | {"event": "routing_approved"}
      {"event": "role_started", "role": "Developer"}
      {"event": "role_finished", "role": "Developer", "decision": "ready_for_test",
        "next_action": "..."}
      {"event": "done", "final_decision": "...", "run_dir": "...",
        "handoffs": [{"sender":..., "receiver":..., "decision":...}, ...]}
      {"event": "error", "message": "..."}
    """
    # Pre-flight classification — emit before we hit the orchestrator so the
    # host agent can show the routing immediately.
    try:
        r = classify(root, task=task, project=str(project.resolve()))
    except Exception as exc:  # noqa: BLE001
        _emit({"event": "error", "ts": time.time(), "message": str(exc)})
        return 2

    # Apply project config so the emitted routing matches what will actually run.
    project_config = None
    cfg_path = project.resolve() / ".agentcrew" / "config.yaml"
    if cfg_path.exists():
        from .config import ProjectConfig
        from .orchestrator import _apply_project_config

        project_config = ProjectConfig.load(project.resolve())
        if project_config is not None:
            _apply_project_config(r, project_config, project.resolve(), models)

    _emit(
        {
            "event": "routing",
            "ts": time.time(),
            "task": task,
            "lane": r.lane,
            "risk": r.risk,
            "recipe": r.recipe,
            "quality_profile": r.quality_profile,
            "intent": r.intent,
            "workflow": r.workflow,
            "starting_role": r.starting_role,
            "acting_roles": r.acting_roles_in_order(),
            "specialists": r.specialists,
            "gates": r.gates,
            "human_decisions": r.human_decisions,
            "has_mid_workflow_gate": r.has_mid_workflow_human_gate(),
        }
    )

    if not routing_approver(r):
        _emit({"event": "routing_rejected", "ts": time.time()})
        return 1
    _emit({"event": "routing_approved", "ts": time.time()})

    # Emit a cost preview event so the host agent can surface it before any
    # tokens are spent. The orchestrator will recompute internally; this is
    # purely informational — the cost gate still runs there.
    from .cost import (
        decide_cost_gate as _decide,
        estimate_run as _estimate,
        load_daily_so_far as _load_daily,
    )
    from .gates import load_gates_for_role, render_gate_section

    role_chars = {}
    gate_chars = {}
    max_t = {}
    acting_now = r.acting_roles_in_order()
    for role in acting_now:
        try:
            role_chars[role] = len(root.role_file(role).read_text())
        except FileNotFoundError:
            role_chars[role] = 2000
        gate_chars[role] = len(render_gate_section(load_gates_for_role(root, role, r.gates)))
        max_t[role] = 8192
    est = _estimate(
        routing=r,
        acting_roles=acting_now,
        model_for_role=models,
        role_file_chars=role_chars,
        gate_section_chars_for_role=gate_chars,
        max_tokens_per_role=max_t,
    )
    cap = project_config.budget.daily_max_usd if project_config else 0.0
    budget = _load_daily(project.resolve(), daily_cap_usd=cap)
    gate = _decide(
        est,
        budget,
        per_run_warn_usd=(project_config.budget.per_run_warn_usd if project_config else 0.0),
        per_run_block_usd=(project_config.budget.per_run_block_usd if project_config else 0.0),
    )
    _emit({
        "event": "cost_preview",
        "ts": time.time(),
        "per_role": est.to_dict()["per_role"],
        "estimated_total_usd": round(est.total_usd, 4),
        "daily_so_far_usd": round(budget.daily_so_far_usd, 4),
        "daily_cap_usd": round(budget.daily_cap_usd, 2),
        "warn": gate.warn,
        "block": gate.block,
        "reason": gate.reason,
    })
    if est.total_usd > 0 or gate.warn or gate.block:
        _emit({
            "event": "cost_approval_required",
            "ts": time.time(),
            "estimated_total_usd": round(est.total_usd, 4),
            "warn": gate.warn,
            "block": gate.block,
            "reason": gate.reason or "Host agent must get human cost approval before execution.",
        })
        return 1

    # Now run the team. We need to interleave role events with the loop, so we
    # wrap the provider to emit role_started/role_finished from inside.
    from .provider import AgentRun
    from .agents import build_agent

    started_for: set[str] = set()
    orig_run_agent = provider.run_agent

    def _instrumented_run_agent(*, role, **kwargs):
        if role not in started_for:
            _emit({"event": "role_started", "ts": time.time(), "role": role})
            started_for.add(role)
        result = orig_run_agent(role=role, **kwargs)
        if result.submission is not None:
            sub = result.submission
            _emit(
                {
                    "event": "role_finished",
                    "ts": time.time(),
                    "role": role,
                    "decision": sub.get("decision", ""),
                    "next_action": sub.get("next_action", ""),
                    "files_touched": sub.get("files_touched", sub.get("files", [])),
                }
            )
        else:
            _emit(
                {
                    "event": "role_finished",
                    "ts": time.time(),
                    "role": role,
                    "decision": "(no submission — protocol failure)",
                    "next_action": "",
                    "files_touched": [],
                }
            )
        return result

    provider.run_agent = _instrumented_run_agent  # type: ignore[assignment]

    def _from_agent_risk_acceptor(routing, role):
        _emit({
            "event": "human_decision_required",
            "ts": time.time(),
            "decision": "accept critical risk before implementation",
            "role_about_to_run": role,
            "risk": routing.risk,
            "lane": routing.lane,
            "human_decisions": routing.human_decisions,
        })
        return False

    from .orchestrator import auto_approve, run as run_team

    result = run_team(
        task=task,
        project_dir=project,
        root=root,
        provider=provider,
        model_for_role=models,
        routing_approver=auto_approve,  # already approved above
        risk_acceptor=_from_agent_risk_acceptor,
        cwd_for_classifier=str(project.resolve()),
    )

    _emit(
        {
            "event": "done",
            "ts": time.time(),
            "final_decision": result.final_decision,
            "next_owner": result.next_owner,
            "run_dir": str(result.run_dir),
            "estimated_cost_usd": round(result.cost_estimate.total_usd, 4) if result.cost_estimate else 0,
            "actual_cost_usd": round(result.actual_cost_usd, 4),
            "handoffs": [
                {"sender": h.sender, "receiver": h.receiver, "decision": h.decision}
                for h in result.handoffs
            ],
        }
    )
    return 0 if result.next_owner == "human" and not result.final_decision.startswith("protocol_") else 1


def _interactive_cost_approver(gate) -> bool:
    """Interactive cost gate: print the table + reason + prompt the user."""
    sys.stdout.write("\n" + "-" * 70 + "\n")
    sys.stdout.write("Cost estimate for this run:\n\n")
    sys.stdout.write(gate.estimate.render_table())
    sys.stdout.write("\n\n")
    if gate.budget.daily_cap_usd > 0:
        sys.stdout.write(
            f"Daily so far: ${gate.budget.daily_so_far_usd:.4f} of ${gate.budget.daily_cap_usd:.2f} cap "
            f"(${gate.budget.remaining_usd:.4f} remaining)\n\n"
        )
    if gate.block:
        sys.stdout.write(f"⛔ BLOCKED: {gate.reason}\n")
    elif gate.warn:
        sys.stdout.write(f"⚠  WARNING: {gate.reason}\n")
    sys.stdout.write("-" * 70 + "\n")
    while True:
        try:
            answer = input("\nProceed with this run? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n(no input — declining)")
            return False
        if answer in ("y", "yes"):
            return True
        if answer in ("", "n", "no"):
            return False
        print("Please answer y or n.")


def _interactive_routing_approver(routing: Routing) -> bool:
    print("\n" + "=" * 60)
    print(render_routing_md(routing))
    print("=" * 60)
    while True:
        try:
            answer = input("\nApprove this routing and execute the workflow? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n(no input — declining)")
            return False
        if answer in ("y", "yes"):
            return True
        if answer in ("", "n", "no"):
            return False
        print("Please answer y or n.")


def _interactive_risk_acceptor(routing: Routing, role: str) -> bool:
    print("\n" + "!" * 60)
    print("Human-only risk decision required before execution continues.")
    print(f"Risk: {routing.risk}")
    print(f"Lane: {routing.lane}")
    print(f"Next role if accepted: {role}")
    if routing.human_decisions:
        print("Required decisions:")
        for decision in routing.human_decisions:
            print(f"  - {decision}")
    print("!" * 60)
    while True:
        try:
            answer = input("\nDo you accept this critical risk and continue? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n(no input — declining)")
            return False
        if answer in ("y", "yes"):
            return True
        if answer in ("", "n", "no"):
            return False
        print("Please answer y or n.")


def _resolve_models(args) -> dict[str, str]:
    """Build a {role: model} dict from CLI flags + env vars + default."""
    default = os.environ.get("AGENTCREW_MODEL")
    out: dict[str, str] = {}
    for role in AVAILABLE_ROLES:
        slug = role.upper().replace(" / ", "_").replace(" ", "_")
        # Flag form: --developer-model, --security-reviewer-model, etc.
        flag_attr = role.lower().replace(" / ", "_").replace(" ", "_") + "_model"
        flag = getattr(args, flag_attr, None)
        env = os.environ.get(f"AGENTCREW_{slug}_MODEL")
        chosen = flag or env or default
        if chosen:
            out[role] = chosen
    return out


def _add_per_role_model_flags(p: argparse.ArgumentParser) -> None:
    for role in AVAILABLE_ROLES:
        slug = role.lower().replace(" / ", "_").replace(" ", "_")
        p.add_argument(f"--{slug.replace('_', '-')}-model", dest=f"{slug}_model", default=None)


def _make_provider(args):
    if args.backend == "mock-demo":
        from .demo_script import demo_provider

        return demo_provider()
    if args.backend == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
            sys.exit(2)
        from .provider_anthropic import AnthropicProvider

        return AnthropicProvider()
    if args.backend == "openai":
        from .provider_openai import OpenAICompatibleProvider

        return OpenAICompatibleProvider(base_url=args.base_url)
    if args.backend == "local":
        from .provider_local import LocalProvider

        try:
            return LocalProvider(base_url=args.base_url)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(2)
    print(f"ERROR: unknown backend {args.backend!r}", file=sys.stderr)
    sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agentcrew-engine", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--agentcrew-root", type=Path, default=None, help="Path to the AgentCrew methodology root. Default: AGENTCREW_ROOT env var or sibling check.")

    route = sub.add_parser("route", parents=[common], help="Preview the routing the classifier would emit")
    route.add_argument("--task", required=True)
    route.add_argument("--project", type=Path, default=Path("."))

    run = sub.add_parser("run", parents=[common], help="Classify and execute the workflow")
    run.add_argument("--task", required=True)
    run.add_argument("--project", type=Path, required=True)
    run.add_argument("--backend", choices=["local", "openai", "anthropic", "mock-demo"], default="mock-demo")
    run.add_argument("--base-url", default=None)
    run.add_argument("--auto-approve-routing", action="store_true")
    run.add_argument(
        "--from-agent",
        action="store_true",
        help=(
            "Emit JSON-lines events on stdout (one per line) instead of human prose. "
            "Use this when a host agent invokes the engine "
            "and wants to render progress inline."
        ),
    )
    _add_per_role_model_flags(run)

    doc = sub.add_parser("doctor", parents=[common], help="Verify the methodology link")
    sub.add_parser("models", help="Recommended local models per role")
    sub.add_parser("backends", help="Available provider plugins")

    show = sub.add_parser("show", parents=[common], help="Show the latest run as a one-screen summary")
    show.add_argument("--project", type=Path, default=Path("."))
    show.add_argument("--run", type=str, default=None, help="Specific run id (default: latest)")

    audit = sub.add_parser("audit", parents=[common], help="Cross-run report (lanes, gates, specialists, cost)")
    audit.add_argument("--project", type=Path, default=Path("."))
    audit.add_argument("--since", type=str, default=None, help="ISO date YYYY-MM-DD")
    audit.add_argument("--until", type=str, default=None, help="ISO date YYYY-MM-DD")

    dec = sub.add_parser("decisions", parents=[common], help="View or append the team decisions log")
    dec.add_argument("--project", type=Path, default=Path("."))
    dec_sub = dec.add_subparsers(dest="dec_cmd", required=False)
    dec_add = dec_sub.add_parser("add", help="Append a new decision")
    dec_add.add_argument("--title", required=True)
    dec_add.add_argument("--by", action="append", default=[], help="Decided by (repeat for multiple)")
    dec_add.add_argument("--rationale", default="")

    args = parser.parse_args(argv)

    if args.cmd == "models":
        try:
            from .provider_local import recommended_models_for_code

            for role, models in recommended_models_for_code().items():
                print(f"{role}:")
                for m in models:
                    print(f"  - {m}")
                print()
        except ImportError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        return 0

    if args.cmd == "backends":
        print("AgentCrew engine backends (pick one):\n")
        print("  --backend mock-demo  bundled scripted demo; no provider key")
        print("  --backend local      Ollama-first; pip install -e \".[openai]\"")
        print("  --backend openai     any OpenAI-compatible endpoint")
        print("  --backend anthropic  optional Anthropic backend; pip install -e \".[anthropic]\"")
        return 0

    try:
        root = find_agentcrew_root(args.agentcrew_root if hasattr(args, "agentcrew_root") else None)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.cmd == "doctor":
        print(f"AgentCrew root: {root.path}")
        print(f"classifier: {root.classifier}  ({'exists' if root.classifier.exists() else 'MISSING'})")
        try:
            sample = classify(root, task="placeholder", project=str(root.path))
            print(f"classifier round-trip: OK (sample lane={sample.lane!r})")
        except Exception as exc:  # noqa: BLE001
            print(f"classifier round-trip: FAILED — {exc}", file=sys.stderr)
            return 1
        return 0

    if args.cmd == "show":
        from .show import find_latest_run, render_latest, render_run

        if args.run:
            run_dir = args.project.resolve() / ".agent-state" / "runs" / args.run
            if not run_dir.exists():
                print(f"ERROR: run not found: {run_dir}", file=sys.stderr)
                return 2
            print(render_run(run_dir))
        else:
            print(render_latest(args.project.resolve()))
        return 0

    if args.cmd == "audit":
        from .audit import collect, render

        report = collect(args.project.resolve(), since=args.since, until=args.until)
        print(render(report))
        return 0

    if args.cmd == "decisions":
        from .decisions import load_recent, record_decision
        from .state import build_layout

        layout = build_layout(args.project.resolve())
        if args.dec_cmd == "add":
            record_decision(
                layout.decisions,
                title=args.title,
                decided_by=args.by,
                rationale=args.rationale,
            )
            print(f"Recorded decision in {layout.decisions}")
        else:
            text = load_recent(layout.decisions, limit=20)
            if text:
                print(text)
            else:
                print(f"No decisions recorded. Add one with:\n  agentcrew decisions add --title \"...\"")
        return 0

    if args.cmd == "route":
        try:
            r = classify(root, task=args.task, project=str(args.project.resolve()))
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        # Apply .agentcrew/config.yaml so the preview matches what `run` will
        # actually execute. The config can only tighten (escalate profile, add
        # specialists), never widen.
        cfg_path = args.project.resolve() / ".agentcrew" / "config.yaml"
        if cfg_path.exists():
            try:
                from .config import ProjectConfig
                from .orchestrator import _apply_project_config
            except ImportError as exc:
                print(
                    f"WARN: skipping project config in route preview ({exc}). "
                    "Install engine dependencies for config-aware routing.",
                    file=sys.stderr,
                )
            else:
                cfg = ProjectConfig.load(args.project.resolve())
                if cfg is not None:
                    _apply_project_config(r, cfg, args.project.resolve(), {})
        print(render_routing_md(r))
        return 0

    if args.cmd == "run":
        # Project config can set default backend and per-role models, so the
        # user doesn't have to pass --backend, --developer-model, ... every time.
        from .config import ProjectConfig

        project_config = ProjectConfig.load(args.project.resolve())
        if project_config:
            # CLI's default is "mock-demo"; if user didn't explicitly pass --backend
            # and config has one, use the config value.
            if args.backend == "mock-demo" and project_config.backend:
                args.backend = project_config.backend

        provider = _make_provider(args)
        models = _resolve_models(args)
        if project_config:
            for role, model in project_config.models.items():
                if role not in models:
                    models[role] = model
        if args.backend == "mock-demo":
            for role in AVAILABLE_ROLES:
                models.setdefault(role, f"mock-{role.lower().replace(' / ', '-').replace(' ', '-')}")
        from .orchestrator import auto_approve, auto_approve_cost, run as run_team

        approver = auto_approve if (args.auto_approve_routing or args.from_agent) else _interactive_routing_approver

        cost_approver = auto_approve_cost if args.from_agent else _interactive_cost_approver

        if args.from_agent:
            return _run_from_agent(
                task=args.task,
                project=args.project,
                root=root,
                provider=provider,
                models=models,
                routing_approver=approver,
            )

        result = run_team(
            task=args.task,
            project_dir=args.project,
            root=root,
            provider=provider,
            model_for_role=models,
            routing_approver=approver,
            cost_approver=cost_approver,
            risk_acceptor=_interactive_risk_acceptor,
            cwd_for_classifier=str(args.project.resolve()),
        )
        if result.direct_answer:
            print(result.direct_answer)
            return 0
        print(result.summary())
        print()
        print(f"Artifacts written to: {result.run_dir}")
        return 0 if result.next_owner == "human" and not result.final_decision.startswith("protocol_") else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
