"""
🗂️  Vault Sidebar — Shared sidebar component for the Meeting Vault.

Renders a styled sidebar with department-grouped past analyses
and a "Clear History" button. Used by both Transcript and Media pages.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from core.storage import clear_vault, group_by_department, load_analysis


# Department display config
_DEPT_ICONS: dict[str, str] = {
    "Engineering": "🔧",
    "Product": "📦",
    "Management": "📊",
}


def _format_timestamp(iso: str) -> str:
    """Pretty-print an ISO timestamp."""
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%b %d, %Y  %H:%M")
    except Exception:
        return iso[:16]


def inject_sidebar_css() -> None:
    """Inject custom cyberpunk CSS for the sidebar."""
    st.markdown(
        """
        <style>
        /* ── Show sidebar on analyzer pages ──────────────────────────── */
        section[data-testid="stSidebar"] {
            display: block !important;
            background: rgba(8, 8, 16, 0.95) !important;
            border-right: 1px solid rgba(0, 240, 255, 0.12) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background: transparent !important;
        }

        /* ── Vault header ──────────────────────────────────────────── */
        .vault-header {
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: #00f0ff;
            text-align: center;
            margin-bottom: 0.4rem;
            padding: 0.8rem 0 0.2rem;
        }

        .vault-divider {
            border: none;
            border-top: 1px solid rgba(0, 240, 255, 0.15);
            margin: 0.5rem 0 1rem 0;
        }

        .vault-empty {
            text-align: center;
            font-size: 0.72rem;
            color: #6b7394;
            letter-spacing: 1px;
            padding: 1.5rem 0;
        }

        /* ── Meeting entry cards ───────────────────────────────────── */
        .vault-entry {
            background: rgba(0, 240, 255, 0.03);
            border: 1px solid rgba(0, 240, 255, 0.1);
            border-radius: 8px;
            padding: 0.6rem 0.8rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .vault-entry:hover {
            border-color: #00ffd4;
            background: rgba(0, 255, 212, 0.05);
            box-shadow: 0 0 12px rgba(0, 255, 212, 0.1);
        }

        .vault-entry-time {
            font-size: 0.6rem;
            color: #6b7394;
            letter-spacing: 1px;
        }

        .vault-entry-snippet {
            font-size: 0.68rem;
            color: #e0e6f0;
            line-height: 1.4;
            margin-top: 0.2rem;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        .vault-source-badge {
            display: inline-block;
            font-size: 0.5rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            background: rgba(139, 0, 255, 0.15);
            color: #8b00ff;
            margin-left: 0.4rem;
        }

        /* ── Detected-category tags ───────────────────────────────── */
        .vault-cat-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem;
            margin-top: 0.3rem;
        }
        .vault-cat-tag {
            display: inline-block;
            font-size: 0.45rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 0.1rem 0.35rem;
            border-radius: 3px;
            border: 1px solid rgba(0, 240, 255, 0.2);
            color: #6b7394;
        }
        .vault-cat-tag.active {
            background: rgba(0, 240, 255, 0.12);
            border-color: rgba(0, 240, 255, 0.4);
            color: #00f0ff;
        }

        /* ── Department badge buttons ─────────────────────────────── */
        .dept-badge-row {
            display: flex;
            justify-content: center;
            gap: 0.4rem;
            margin: 0.3rem 0 0.6rem 0;
        }

        /* Override sidebar button defaults for badge buttons */
        section[data-testid="stSidebar"] .dept-badge-wrap .stButton > button {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 500;
            font-size: 0.58rem !important;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            padding: 0.35rem 0.7rem !important;
            border-radius: 20px !important;
            min-height: 0 !important;
            width: auto !important;
            white-space: nowrap;
            transition: all 0.3s ease !important;
            color: #6b7394 !important;
            background: rgba(0, 240, 255, 0.04) !important;
            border: 1px solid rgba(0, 240, 255, 0.12) !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .dept-badge-wrap .stButton > button:hover {
            color: #e0e6f0 !important;
            border-color: rgba(0, 240, 255, 0.35) !important;
            background: rgba(0, 240, 255, 0.08) !important;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.12) !important;
            transform: none !important;
        }

        /* Active badge — bright glow */
        section[data-testid="stSidebar"] .dept-badge-active .stButton > button {
            color: #00f0ff !important;
            background: rgba(0, 240, 255, 0.12) !important;
            border: 1px solid rgba(0, 240, 255, 0.5) !important;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.25),
                        0 0 24px rgba(0, 240, 255, 0.08) !important;
        }
        section[data-testid="stSidebar"] .dept-badge-active .stButton > button:hover {
            box-shadow: 0 0 18px rgba(0, 240, 255, 0.35),
                        0 0 30px rgba(0, 240, 255, 0.12) !important;
        }

        /* ── Sidebar expander styling ──────────────────────────────── */
        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            border: 1px solid rgba(0, 240, 255, 0.1) !important;
            border-radius: 8px !important;
            background: rgba(10, 10, 18, 0.4) !important;
            margin-bottom: 0.5rem !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
            color: #e0e6f0 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.72rem !important;
            letter-spacing: 1px !important;
        }

        /* ── Clear button ──────────────────────────────────────────── */
        section[data-testid="stSidebar"] .vault-clear-wrap .stButton > button {
            width: 100%;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 500;
            font-size: 0.68rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #ff4466 !important;
            background: rgba(255, 68, 102, 0.08) !important;
            border: 1px solid rgba(255, 68, 102, 0.25) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .vault-clear-wrap .stButton > button:hover {
            background: rgba(255, 68, 102, 0.18) !important;
            border-color: rgba(255, 68, 102, 0.5) !important;
            box-shadow: 0 0 15px rgba(255, 68, 102, 0.15) !important;
            transform: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_vault_sidebar(current_role: str = "Engineering") -> dict[str, Any] | None:
    """
    Render the Meeting Vault sidebar, filtered to the active stakeholder lens.

    Parameters
    ----------
    current_role : str
        The currently selected department / stakeholder lens.
        Only entries matching this role are displayed.

    Returns
    -------
    dict | None
        The selected archived record if the user clicked one, else ``None``.
    """
    inject_sidebar_css()

    selected_record: dict[str, Any] | None = None
    icon = _DEPT_ICONS.get(current_role, "📁")

    with st.sidebar:
        st.markdown('<div class="vault-header">🗄️ Meeting Vault</div>', unsafe_allow_html=True)

        # ── Interactive department badges ─────────────────────────
        badge_cols = st.columns(3)
        all_departments = ["Engineering", "Product", "Management"]
        for col, dept in zip(badge_cols, all_departments):
            dept_icon = _DEPT_ICONS.get(dept, "📁")
            is_active = dept == current_role
            css_class = "dept-badge-active" if is_active else "dept-badge-wrap"
            with col:
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                if st.button(
                    f"{dept_icon} {dept}",
                    key=f"badge_{dept}",
                    use_container_width=True,
                ):
                    if dept != current_role:
                        st.session_state.analyzer_role = dept
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr class="vault-divider">', unsafe_allow_html=True)

        # Show which lens is active
        st.markdown(
            f'<div style="text-align:center; font-size:0.6rem; color:#6b7394; '
            f'letter-spacing:2px; text-transform:uppercase; margin-bottom:0.3rem;">'
            f'{icon} {current_role} Lens Active</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="vault-divider">', unsafe_allow_html=True)

        groups = group_by_department()
        entries = groups.get(current_role, [])

        if not entries:
            st.markdown(
                f'<div class="vault-empty">No {current_role}-related meetings yet.<br>'
                f'Meetings containing {current_role.lower()} keywords<br>'
                f'will appear here automatically.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="font-size:0.65rem; color:#00f0ff; letter-spacing:1px; '
                f'margin-bottom:0.6rem;">{icon} {len(entries)} '
                f'{"meeting" if len(entries) == 1 else "meetings"} archived</div>',
                unsafe_allow_html=True,
            )

            for i, entry in enumerate(entries):
                ts_label = _format_timestamp(entry.get("timestamp", ""))
                snippet = entry.get("summary", "")[:80]
                source = entry.get("source", "transcript")
                source_badge = "🎙️" if source == "media" else "📝"

                btn_key = f"vault_{current_role}_{i}"
                if st.button(
                    f"{source_badge} {ts_label}\n{snippet}…",
                    key=btn_key,
                    use_container_width=True,
                ):
                    filepath = entry.get("_filepath")
                    if filepath:
                        selected_record = load_analysis(filepath)

                # Show detected-category tags below each entry
                detected = entry.get("detected_categories", [])
                if detected and len(detected) > 1:
                    tags_html = '<div class="vault-cat-row">'
                    for cat in detected:
                        cat_icon = _DEPT_ICONS.get(cat, "📁")
                        active = " active" if cat == current_role else ""
                        tags_html += (
                            f'<span class="vault-cat-tag{active}">'
                            f'{cat_icon} {cat}</span>'
                        )
                    tags_html += '</div>'
                    st.markdown(tags_html, unsafe_allow_html=True)

        # ── Other departments — compact counts row ─────────────────
        other_depts = [d for d in ["Engineering", "Product", "Management"] if d != current_role]
        other_counts = {d: len(groups.get(d, [])) for d in other_depts if groups.get(d)}

        if other_counts:
            st.markdown('<hr class="vault-divider">', unsafe_allow_html=True)
            counts_html = '<div style="text-align:center; font-size:0.55rem; color:#4a5068; letter-spacing:1px;">'
            parts = []
            for dept, count in other_counts.items():
                dept_icon = _DEPT_ICONS.get(dept, "📁")
                parts.append(f'{dept_icon} {dept}: {count}')
            counts_html += ' &nbsp;·&nbsp; '.join(parts)
            counts_html += '</div>'
            st.markdown(counts_html, unsafe_allow_html=True)

        # ── Clear History ──────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="vault-clear-wrap">', unsafe_allow_html=True)
        if st.button("🗑️  Clear History", key="vault_clear"):
            count = clear_vault()
            st.toast(f"Cleared {count} meeting(s) from vault", icon="🗑️")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    return selected_record
