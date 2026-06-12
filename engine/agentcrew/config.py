"""Project-level config loader — `.agentcrew/config.yaml`.

Schema mirrors the file `agentcrew init` writes. The loader is permissive:
unknown keys are kept (forwards-compat); missing keys fall back to None /
empty so the orchestrator can detect "no override".

The orchestrator calls `ProjectConfig.load(project_dir)` once at run start.
Three things the config drives at run time:

  1. Recipe → profile overrides:  routing.quality_profile may be replaced
     based on recipe_profiles.<recipe>.
  2. Required specialists by path glob: project files matching
     required_specialists[*].paths add those roles to routing.specialists.
  3. Per-role default models (and backend), so the CLI doesn't need to
     pass --developer-model, --tester-model, ... every time.

Per AgentCrew's safety design, the config does NOT widen safety. It can:
  - tighten profile (standard → strict)
  - add specialists
  - set models
It cannot:
  - skip a gate the classifier raised
  - remove a specialist the classifier picked
  - bypass the human gate
"""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_VALID_PROFILES = {"light", "standard", "strict", "regulated"}
_SCAN_PRUNE_DIRS = {
    ".agent-state",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}


@dataclass
class RequiredSpecialistRule:
    paths: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)


@dataclass
class BudgetConfig:
    daily_max_usd: float = 0.0           # 0 = no daily cap
    per_run_warn_usd: float = 0.50
    per_run_block_usd: float = 5.0       # 0 = no per-run cap


@dataclass
class ProjectConfig:
    project_name: str | None = None
    quality_profile: str | None = None   # override classifier's profile globally
    recipe_profiles: dict[str, str] = field(default_factory=dict)
    required_specialists: list[RequiredSpecialistRule] = field(default_factory=list)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    models: dict[str, str] = field(default_factory=dict)
    backend: str | None = None           # local | openai | anthropic | mock-demo
    telemetry_enabled: bool = False      # opt-in local anonymous metrics

    # Path the config was loaded from. Useful for diagnostics.
    source_path: Path | None = None

    @classmethod
    def load(cls, project_dir: Path) -> "ProjectConfig | None":
        """Load .agentcrew/config.yaml from project_dir. Returns None if not present."""
        project_dir = project_dir.resolve()
        path = project_dir / ".agentcrew" / "config.yaml"
        if not path.exists():
            return None
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover — exercised only without pyyaml
            raise ImportError(
                "Reading .agentcrew/config.yaml requires PyYAML. "
                "Install with: pip install pyyaml"
            ) from exc
        raw = yaml.safe_load(path.read_text()) or {}
        return cls._from_raw(raw, source_path=path)

    @classmethod
    def _from_raw(cls, raw: dict[str, Any], *, source_path: Path | None = None) -> "ProjectConfig":
        """Build a ProjectConfig from a parsed YAML dict.

        The schema is forgiving: any unknown top-level key is silently dropped
        and known keys with the wrong type are dropped rather than raising,
        so a slightly-broken config still lets the runtime start.
        """
        project = (raw.get("project") or {}) if isinstance(raw.get("project"), dict) else {}

        # quality_profile: validate against the enum; drop bad values.
        qp = raw.get("quality_profile")
        if not isinstance(qp, str) or qp.lower() not in _VALID_PROFILES:
            qp = None

        # recipe_profiles
        recipe_profiles: dict[str, str] = {}
        rp = raw.get("recipe_profiles") or {}
        if isinstance(rp, dict):
            for recipe, profile in rp.items():
                if isinstance(recipe, str) and isinstance(profile, str) and profile.lower() in _VALID_PROFILES:
                    recipe_profiles[recipe] = profile.lower()

        # required_specialists
        required = []
        for entry in raw.get("required_specialists") or []:
            if not isinstance(entry, dict):
                continue
            paths = entry.get("paths") or []
            roles = entry.get("roles") or []
            if not isinstance(paths, list) or not isinstance(roles, list):
                continue
            paths = [str(p) for p in paths if isinstance(p, str)]
            roles = [str(r) for r in roles if isinstance(r, str)]
            if paths and roles:
                required.append(RequiredSpecialistRule(paths=paths, roles=roles))

        # budget
        budget_raw = raw.get("budget") or {}
        budget = BudgetConfig(
            daily_max_usd=float(budget_raw.get("daily_max_usd", 0) or 0),
            per_run_warn_usd=float(budget_raw.get("per_run_warn_usd", 0.5) or 0.5),
            per_run_block_usd=float(budget_raw.get("per_run_block_usd", 5.0) or 5.0),
        )

        # models
        models = {}
        for role, model in (raw.get("models") or {}).items():
            if isinstance(role, str) and isinstance(model, str):
                models[role] = model

        # backend
        backend = raw.get("backend")
        if not isinstance(backend, str):
            backend = None

        # telemetry (opt-in)
        telemetry = raw.get("telemetry") or {}
        telemetry_enabled = bool(telemetry.get("enabled", False)) if isinstance(telemetry, dict) else False

        return cls(
            project_name=project.get("name") if isinstance(project.get("name"), str) else None,
            quality_profile=qp.lower() if qp else None,
            recipe_profiles=recipe_profiles,
            required_specialists=required,
            budget=budget,
            models=models,
            backend=backend,
            telemetry_enabled=telemetry_enabled,
            source_path=source_path,
        )

    # ----- Apply -----

    def profile_for_recipe(self, recipe: str, fallback: str) -> str:
        """Return the profile to use given the classifier's recipe.

        Resolution order: recipe-specific override → global override → fallback.
        """
        if recipe in self.recipe_profiles:
            return self.recipe_profiles[recipe]
        if self.quality_profile:
            return self.quality_profile
        return fallback

    def required_specialists_for_project(self, project_dir: Path) -> list[str]:
        """Return specialists that must run because the project has files
        matching any of the required-specialist glob rules.

        Order-preserving and deduped. Globs are matched against paths
        relative to the project root, not absolute.
        """
        project_dir = project_dir.resolve()
        seen: set[str] = set()
        ordered: list[str] = []

        # Pre-compute project file paths once, pruning generated/vendor state
        # so specialist rules reflect source structure rather than caches.
        all_files: list[str] = []
        for dirpath, dirnames, filenames in os.walk(project_dir):
            dirnames[:] = [d for d in dirnames if d not in _SCAN_PRUNE_DIRS]
            base = Path(dirpath)
            for filename in filenames:
                p = base / filename
                try:
                    rel = p.relative_to(project_dir)
                except ValueError:
                    continue
                all_files.append(str(rel))

        for rule in self.required_specialists:
            matched = False
            for pattern in rule.paths:
                for f in all_files:
                    if fnmatch.fnmatch(f, pattern):
                        matched = True
                        break
                if matched:
                    break
            if matched:
                for role in rule.roles:
                    if role not in seen:
                        seen.add(role)
                        ordered.append(role)
        return ordered
