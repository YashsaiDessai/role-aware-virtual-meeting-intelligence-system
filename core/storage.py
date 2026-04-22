"""
🗄️  Meeting Vault — Local JSON-based storage for meeting analyses.

Saves each analysis as ``<timestamp>_<department>.json`` inside ``data/vault/``.
Provides helpers to list, load, group-by-department, and clear the vault.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default vault directory (relative to project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = _PROJECT_ROOT / "data" / "vault"


# ── helpers ────────────────────────────────────────────────────────────
def _ensure_vault() -> Path:
    """Create the vault directory if it doesn't exist and return its path."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    return VAULT_DIR


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

    record: dict[str, Any] = {
        "timestamp": now.isoformat(),
        "department": department,
        "source": source,
        "summary": summary,
        "decisions": decisions,
        "action_items": action_items,
        "transcript_snippet": transcript_snippet[:500],
    }

    filepath = vault / filename
    filepath.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved analysis → %s", filepath)
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
    Return vault entries grouped by department.

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
            dept = record.get("department", "Unknown")
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
