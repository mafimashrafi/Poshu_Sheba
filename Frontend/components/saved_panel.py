"""Saved-responses panel: locked prompt for guests, saved responses list for members.

Rendered in two places at once when the sidebar is open (compact, in the
sidebar) and the user is on the full "saved" page (non-compact, in the main
area) — every Streamlit element key here is namespaced by `compact` so the
two instances never collide.
"""

from datetime import datetime
from typing import Callable

import streamlit as st

from utils import api_client, theme
from utils.icons import icon

INK = theme.NAVY
TEAL = theme.PRIMARY

WHY_LOGIN = [
    "আপনার উত্তরসমূহ সংরক্ষণ করুন",
    "যেকোনো সময় দেখতে/পুনরায় পড়তে পারবেন",
    "নিরাপদ এবং ব্যক্তিগত",
]


def _format_timestamp(raw: str) -> str:
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%d %b %Y, %I:%M %p")
    except (ValueError, AttributeError):
        return raw


def render_saved_panel(on_open_login: Callable[[], None], compact: bool = True) -> None:
    ns = "compact" if compact else "full"

    with st.container(key=f"saved_panel_{ns}"):
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
                {icon("bookmark", color=INK, size=20)}
                <span style="font-weight:700;color:{INK};font-size:1.05rem;">সেভ করা উত্তরসমূহ</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        token = st.session_state.get("token")
        if not token:
            _render_locked(on_open_login, ns)
            return

        try:
            responses = api_client.get_saved_responses(token)
        except api_client.SessionExpiredError as exc:
            st.session_state.token = None
            st.session_state.phone_number = None
            st.session_state.display_name = None
            st.warning(exc.message)
            _render_locked(on_open_login, ns)
            return
        except api_client.ApiError as exc:
            st.error(exc.message)
            return

        if not responses:
            st.caption("এখনো কোনো উত্তর সংরক্ষণ করা হয়নি।")
            return

        limit = 5 if compact else len(responses)
        preview_len = 70 if compact else 140
        for item in responses[:limit]:
            preview = item["response"].strip().replace("\n", " ")
            if len(preview) > preview_len:
                preview = preview[:preview_len].rstrip() + "…"
            with st.container(key=f"saved_item_{ns}_{item['response_id']}", border=True):
                st.markdown(f"<p style='color:{INK};font-size:0.88rem;margin:0;'>{preview}</p>", unsafe_allow_html=True)
                st.caption(_format_timestamp(item["created_at"]))

        if compact and len(responses) > limit:
            if st.button("সব দেখুন", key=f"saved_view_all_{ns}", use_container_width=True):
                st.session_state.nav_page = "saved"
                st.rerun()


def _render_locked(on_open_login: Callable[[], None], ns: str) -> None:
    with st.container(key=f"saved_locked_{ns}"):
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;margin:1.2rem 0 1rem;">
                <div style="width:64px;height:64px;border-radius:50%;background:{theme.PRIMARY_TINT};
                            display:flex;align-items:center;justify-content:center;">
                    {icon("lock", color=TEAL, size=28)}
                </div>
            </div>
            <p style="text-align:center;font-weight:700;color:{INK};font-size:0.95rem;line-height:1.5;">
                সেভ করা উত্তর দেখতে<br/>লগ ইন করুন
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            "লগ ইন করুন",
            key=f"saved_login_cta_{ns}",
            type="primary",
            use_container_width=True,
            on_click=on_open_login,
        )

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight:700;color:{INK};'>কেন লগ ইন করবেন?</p>", unsafe_allow_html=True)
        for reason in WHY_LOGIN:
            st.markdown(
                f"""
                <div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem;">
                    {icon("check-circle", color=theme.PRIMARY, size=16)}
                    <span style="color:{INK};font-size:0.88rem;">{reason}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
