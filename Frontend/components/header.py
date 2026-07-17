"""Top header: brand lockup, saved-data shortcut, notifications, account menu."""

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
    ratios = [3.2, 4.8, 1.9, 0.6, 1.6] if logged_in else [3.2, 3.6, 1.9, 0.6, 2.8]

    with st.container(key="app_header"):
        logo_col, _spacer_col, saved_col, bell_col, account_col = st.columns(
            ratios, vertical_alignment="center"
        )

        with logo_col:
            brand_logo, brand_text = st.columns([1, 5], vertical_alignment="center")
            with brand_logo:
                if LOGO_PATH.exists():
                    st.image(str(LOGO_PATH), width=42)
            with brand_text:
                st.markdown(
                    f"""
                    <div style="line-height:1.15;">
                        <span style="font-size:1.35rem;font-weight:800;color:{INK};">
                            vet<span style="color:#14B8A6;">.ai</span>
                        </span><br/>
                        <span style="font-size:0.6rem;letter-spacing:0.07em;color:{MUTED};font-weight:600;">
                            SMART CARE. HEALTHIER PETS.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with saved_col:
            if st.button(
                "পুরনো সংরক্ষিত তথ্য দেখুন",
                key="header_saved",
                icon=":material/bookmark:",
                use_container_width=True,
            ):
                st.session_state.nav_page = "saved"
                st.rerun()

        with bell_col:
            with st.popover(" ", icon=":material/notifications:", use_container_width=True):
                st.caption("কোনো নতুন বিজ্ঞপ্তি নেই।")

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
