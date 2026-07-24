"""Top header: brand lockup and account menu."""

from pathlib import Path
from typing import Callable

import streamlit as st

from utils import theme

INK = theme.NAVY
MUTED = theme.SLATE

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo_icon.png"


def _mask_phone(phone: str) -> str:
    if not phone:
        return "ব্যবহারকারী"
    return phone[-4:].rjust(len(phone), "•")


def render_header(
    on_open_login: Callable[[], None],
    on_open_profile: Callable[[], None],
    on_toggle_sidebar: Callable[[], None],
    sidebar_open: bool = False,
) -> None:
    logged_in = bool(st.session_state.get("token"))
    ratios = [0.5, 3.0, 6.0, 1.6] if logged_in else [0.5, 3.0, 4.7, 2.8]

    with st.container(key="app_header"):
        toggle_col, logo_col, _spacer_col, account_col = st.columns(ratios, vertical_alignment="center")

        with toggle_col:
            with st.container(key="sidebar_toggle_wrap"):
                st.button(
                    "",
                    key="sidebar_toggle_btn",
                    icon=":material/menu_open:" if sidebar_open else ":material/menu:",
                    help="ইতিহাস সাইডবার দেখান/লুকান",
                    on_click=on_toggle_sidebar,
                )

        with logo_col:
            with st.container(key="logo_brand"):
                brand_logo, brand_text = st.columns([1, 5], vertical_alignment="center")
                with brand_logo:
                    if LOGO_PATH.exists():
                        st.image(str(LOGO_PATH), width=56)
                with brand_text:
                    st.markdown(
                        f"""
                        <div style="line-height:1.25;">
                            <span style="font-size:1.4rem;font-weight:800;color:{INK};letter-spacing:-0.01em;">
                                vet<span style="color:{theme.PRIMARY};">.ai</span>
                            </span><br/>
                            <span style="font-size:0.72rem;letter-spacing:0.01em;color:{MUTED};font-weight:600;">
                                পশু স্বাস্থ্য সেবা AI
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                if st.button(" ", key="logo_home_btn", help="হোম পেজে যান", use_container_width=True):
                    st.session_state.nav_page = "home"
                    st.rerun()

        with account_col:
            if logged_in:
                label = st.session_state.get("display_name") or _mask_phone(
                    st.session_state.get("phone_number", "")
                )
                with st.popover(label, icon=":material/account_circle:", use_container_width=True):
                    st.caption(st.session_state.get("phone_number", ""))
                    if st.button(
                        "প্রোফাইল আপডেট",
                        key="header_profile",
                        icon=":material/manage_accounts:",
                        use_container_width=True,
                    ):
                        st.session_state.show_profile_dialog = True
                        st.rerun()
                    if st.button(
                        "লগ আউট",
                        key="header_logout",
                        icon=":material/logout:",
                        use_container_width=True,
                    ):
                        st.session_state.token = None
                        st.session_state.phone_number = None
                        st.session_state.display_name = None
                        st.session_state.nav_page = "home"
                        st.rerun()
            else:
                st.button(
                    "লগ ইন অথবা নতুন অ্যাকাউন্ট খুলুন",
                    key="header_login",
                    icon=":material/login:",
                    use_container_width=True,
                    type="primary",
                    on_click=on_open_login,
                )
