"""
🗄️  Meeting Vault — Local JSON-based storage for meeting analyses.

Saves each analysis as ``<timestamp>_<department>.json`` inside ``data/vault/``.
Provides helpers to list, load, group-by-department, and clear the vault.

Keyword-based auto-categorisation
----------------------------------
Each saved record includes a ``"detected_categories"`` list built by scanning
the transcript, summary, and decisions for department-related keywords.
When the sidebar groups history by department, it uses these detected
categories so a single meeting can appear under multiple stakeholder lenses.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default vault directory (relative to project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = _PROJECT_ROOT / "data" / "vault"


# ── Keyword dictionaries for auto-categorisation ──────────────────────
_DEPARTMENT_KEYWORDS: dict[str, list[str]] = {
    "Engineering": [
        "engineering", "engineer", "technical", "tech debt",
        "code", "codebase", "refactor", "bug", "debug",
        "deploy", "deployment", "architecture", "database", "db",
        "backend", "frontend", "infrastructure", "infra",
        "testing", "qa", "quality assurance", "sprint",
        "dev", "developer", "migration", "server",
        "microservice", "ci/cd", "pipeline", "repository",
        "git", "pull request", "merge", "api", "sdk",
        "latency", "performance", "monitoring", "incident",
        "devops", "kubernetes", "docker", "cloud",
        "auth", "oauth", "token", "endpoint",
        "staging", "production", "release branch",
    ],
    "Product": [
        "product", "roadmap", "feature", "customer",
        "user", "ux", "ui", "design", "release",
        "launch", "adoption", "metrics", "feedback",
        "onboarding", "requirements", "spec", "prd",
        "mvp", "beta", "a/b test", "conversion",
        "retention", "churn", "user story", "persona",
        "wireframe", "prototype", "usability",
        "market", "competitor", "pricing",
        "user experience", "user interface",
        "feature request", "backlog",
    ],
    "Management": [
        "management", "manager", "budget", "headcount",
        "resource", "deadline", "timeline", "risk",
        "escalation", "okr", "kpi", "leadership",
        "executive", "strategy", "allocation", "staffing",
        "vendor", "hiring", "quarterly", "annual",
        "review", "stakeholder", "forecast",
        "governance", "compliance", "audit",
        "cost", "revenue", "p&l", "roi",
        "board", "c-suite", "director",
        "capacity", "planning", "projection",
        "headcount projection", "budget review",
    ],
}

# Pre-compile a single regex per department for fast matching
_DEPT_PATTERNS: dict[str, re.Pattern[str]] = {}
for _dept, _kws in _DEPARTMENT_KEYWORDS.items():
    # Sort longest-first so multi-word phrases match before their parts
    _sorted = sorted(_kws, key=len, reverse=True)
    _pattern = "|".join(re.escape(kw) for kw in _sorted)
    _DEPT_PATTERNS[_dept] = re.compile(_pattern, re.IGNORECASE)


# ── helpers ────────────────────────────────────────────────────────────
def _ensure_vault() -> Path:
    """Create the vault directory if it doesn't exist and return its path."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    return VAULT_DIR


def detect_departments(text: str) -> list[str]:
    """
    Scan *text* for department-related keywords and return matching categories.

    Parameters
    ----------
    text : str
        The text to scan (typically the full transcript, summary, or both).

    Returns
    -------
    list[str]
        Sorted list of detected department names, e.g.
        ``["Engineering", "Management"]``.  May be empty.
    """
    detected: list[str] = []
    for dept, pattern in _DEPT_PATTERNS.items():
        if pattern.search(text):
            detected.append(dept)
    return sorted(detected)


# ── save ───────────────────────────────────────────────────────────────
def save_analysis(
    *,
    department: str,
    summary: str,
    decisions: list[str],
    action_items: list[dict[str, Any]],
    transcript_snippet: str,
    source: str = "transcript",
) -> Path:
    """
    Persist a meeting analysis to the local vault.

    The transcript snippet, summary, and decisions are scanned for
    department-related keywords.  The resulting ``detected_categories``
    list is stored alongside the record so the vault sidebar can show
    the meeting under every relevant stakeholder lens.

    Parameters
    ----------
    department : str
        Role / stakeholder lens (Engineering, Product, Management).
    summary : str
        The LLM-generated meeting summary.
    decisions : list[str]
        Key decisions extracted.
    action_items : list[dict]
        Action item dicts (task, owner, priority).
    transcript_snippet : str
        First ~500 chars of the original transcript for quick recall.
    source : str
        Either ``"transcript"`` or ``"media"``.

    Returns
    -------
    Path
        The path of the saved JSON file.
    """
    vault = _ensure_vault()

    now = datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    safe_dept = department.lower().replace(" ", "_")
    filename = f"{ts}_{safe_dept}.json"

    # ── Auto-detect categories from all available text ────────────
    scan_text = " ".join([
        transcript_snippet,
        summary,
        " ".join(decisions),
        " ".join(
            item.get("task", "") for item in action_items
        ),
    ])
    detected = detect_departments(scan_text)

    # Ensure the selected department is always included
    if department not in detected:
        detected.append(department)
        detected.sort()

    record: dict[str, Any] = {
        "timestamp": now.isoformat(),
        "department": department,
        "detected_categories": detected,
        "source": source,
        "summary": summary,
        "decisions": decisions,
        "action_items": action_items,
        "transcript_snippet": transcript_snippet[:500],
    }

    filepath = vault / filename
    filepath.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(
        "Saved analysis → %s  (detected categories: %s)", filepath, detected
    )
    return filepath


# ── load ───────────────────────────────────────────────────────────────
def load_analysis(filepath: str | Path) -> dict[str, Any]:
    """Load a single vault record and return it as a dict."""
    return json.loads(Path(filepath).read_text(encoding="utf-8"))


# ── list & group ───────────────────────────────────────────────────────
def list_all() -> list[Path]:
    """Return every ``.json`` file in the vault, newest first."""
    vault = _ensure_vault()
    files = sorted(vault.glob("*.json"), reverse=True)
    return files


def group_by_department() -> dict[str, list[dict[str, Any]]]:
    """
    Return vault entries grouped by department using auto-detected categories.

    Each meeting is placed under **every** department whose keywords were
    found in the transcript / summary.  This means a single meeting can
    appear under multiple lenses.

    For older records that lack ``detected_categories``, the function
    falls back to the original ``department`` field.

    Returns
    -------
    dict
        ``{"Engineering": [{...}, ...], "Product": [...], ...}``
        Each entry includes a ``"_filepath"`` key for later loading.
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    for fp in list_all():
        try:
            record = load_analysis(fp)
            record["_filepath"] = str(fp)

            # Use detected_categories if present; fall back to department
            categories = record.get("detected_categories")
            if not categories:
                categories = [record.get("department", "Unknown")]

            for dept in categories:
                groups.setdefault(dept, []).append(record)
        except Exception:
            logger.warning("Skipping corrupt vault file: %s", fp)
    return groups


# ── clear ──────────────────────────────────────────────────────────────
def clear_vault() -> int:
    """Delete all JSON files from the vault. Returns count of files removed."""
    vault = _ensure_vault()
    files = list(vault.glob("*.json"))
    for f in files:
        try:
            os.remove(f)
        except OSError:
            logger.warning("Could not remove %s", f)
    logger.info("Cleared %d file(s) from vault", len(files))
    return len(files)
