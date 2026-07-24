"""Left sidebar: new-question CTA, saved conversation history, and the usage guide link."""

from typing import Callable

import streamlit as st

from components.saved_panel import render_saved_panel
from utils import theme

INK = theme.NAVY


def render_sidebar(on_open_login: Callable[[], None]) -> None:
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

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    render_saved_panel(on_open_login, compact=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    with st.container(key="sidebar_nav"):
        active_guide = st.session_state.get("nav_page") == "guide"
        if st.button(
            "ব্যবহার নির্দেশিকা",
            key="sidebar_guide",
            icon=":material/info:",
            type="primary" if active_guide else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav_page = "guide"
            st.rerun()

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.caption("© 2026 Poshu Sheba AI")
