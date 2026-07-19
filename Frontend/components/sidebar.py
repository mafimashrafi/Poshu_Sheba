"""Left navigation column: page nav, safety reminder card, footer."""

import streamlit as st

from utils import theme
from utils.icons import icon

INK = theme.NAVY

LINK_ITEMS = [
    ("saved", "সেভ করা উত্তরসমূহ", ":material/bookmark:"),
    ("guide", "ব্যবহার নির্দেশিকা", ":material/info:"),
]

_FARM_ILLUSTRATION = f"""
<svg viewBox="0 0 300 120" width="100%" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="300" height="120" rx="14" fill="{theme.MINT}"/>
  <rect x="0" y="92" width="300" height="28" fill="{theme.BORDER}"/>
  <ellipse cx="100" cy="78" rx="34" ry="22" fill="#FFFFFF" stroke="{theme.NAVY}" stroke-width="2"/>
  <ellipse cx="82" cy="72" rx="8" ry="6" fill="{theme.NAVY}"/>
  <ellipse cx="118" cy="80" rx="7" ry="5" fill="{theme.NAVY}"/>
  <circle cx="132" cy="58" r="16" fill="#FFFFFF" stroke="{theme.NAVY}" stroke-width="2"/>
  <circle cx="126" cy="55" r="1.6" fill="{theme.NAVY}"/>
  <circle cx="138" cy="55" r="1.6" fill="{theme.NAVY}"/>
  <line x1="90" y1="98" x2="90" y2="110" stroke="{theme.NAVY}" stroke-width="3"/>
  <line x1="112" y1="98" x2="112" y2="110" stroke="{theme.NAVY}" stroke-width="3"/>
  <ellipse cx="200" cy="82" rx="24" ry="16" fill="#C9A27A" stroke="#5B4636" stroke-width="2"/>
  <circle cx="228" cy="66" r="12" fill="#C9A27A" stroke="#5B4636" stroke-width="2"/>
  <polygon points="234,54 240,44 238,58" fill="#5B4636"/>
  <line x1="190" y1="96" x2="190" y2="108" stroke="#5B4636" stroke-width="3"/>
  <line x1="208" y1="96" x2="208" y2="108" stroke="#5B4636" stroke-width="3"/>
  <ellipse cx="255" cy="90" rx="16" ry="13" fill="#FFFFFF" stroke="#7A3B2E" stroke-width="2"/>
  <circle cx="270" cy="78" r="8" fill="#FFFFFF" stroke="#7A3B2E" stroke-width="2"/>
  <polygon points="270,70 268,64 274,66" fill="{theme.RED}"/>
  <polygon points="278,78 286,80 278,82" fill="{theme.AMBER}"/>
</svg>
"""


def render_sidebar() -> None:
    active = st.session_state.get("nav_page", "home")

    with st.container(key="sidebar_ask_cta"):
        if st.button(
            "নতুন প্রশ্ন করুন",
            key="sidebar_home",
            icon=":material/add_circle:",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.nav_page = "home"
            st.rerun()

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    with st.container(key="sidebar_nav"):
        for page_key, label, mat_icon in LINK_ITEMS:
            if st.button(
                label,
                key=f"sidebar_{page_key}",
                icon=mat_icon,
                type="primary" if active == page_key else "secondary",
                use_container_width=True,
            ):
                st.session_state.nav_page = page_key
                st.rerun()

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    with st.container(key="reminder_card"):
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
                {icon("shield-check", color=theme.PRIMARY, size=20)}
                <span style="font-weight:700;color:{INK};">মনে রাখবেন</span>
            </div>
            <p style="color:{theme.SLATE};font-size:0.85rem;line-height:1.5;margin-bottom:0.8rem;">
                AI সবসময় সঠিক নাও হতে পারে। প্রয়োজনে নিকটস্থ পশু চিকিৎসকের পরামর্শ নিন।
            </p>
            {_FARM_ILLUSTRATION}
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
    st.caption("© 2025 Poshu Sheba AI\n\nসকল অধিকার সংরক্ষিত")
