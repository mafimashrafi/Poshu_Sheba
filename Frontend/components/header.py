"""Top header: brand lockup and account menu."""

from pathlib import Path
from typing import Callable

import streamlit as st

INK = "#0B2545"
MUTED = "#5B6B7B"

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo_icon.png"


def _mask_phone(phone: str) -> str:
    if not phone:
        return "ব্যবহারকারী"
    return phone[-4:].rjust(len(phone), "•")


def render_header(on_open_login: Callable[[], None]) -> None:
    logged_in = bool(st.session_state.get("token"))
    ratios = [3.2, 6.4, 1.6] if logged_in else [3.2, 5.2, 2.8]

    with st.container(key="app_header"):
        logo_col, _spacer_col, account_col = st.columns(ratios, vertical_alignment="center")

        with logo_col:
            with st.container(key="logo_brand"):
                brand_logo, brand_text = st.columns([1, 5], vertical_alignment="center")
                with brand_logo:
                    if LOGO_PATH.exists():
                        st.image(str(LOGO_PATH), width=42)
                with brand_text:
                    st.markdown(
                        f"""
                        <div style="line-height:1.15;">
                            <span style="font-size:1.4rem;font-weight:800;color:{INK};letter-spacing:-0.01em;">
                                vet<span style="color:#14B8A6;">.ai</span>
                            </span><br/>
                            <span style="font-size:0.6rem;letter-spacing:0.08em;color:{MUTED};font-weight:600;">
                                SMART CARE. HEALTHIER PETS.
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
