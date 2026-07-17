"""Decorative walking-cow mascot that roams along the bottom of the page."""

import base64
from pathlib import Path

import streamlit as st

SPRITE_PATH = Path(__file__).resolve().parent.parent / "assets" / "cow_walk_small.png"


def render_walking_cow() -> None:
    if not SPRITE_PATH.exists():
        return

    encoded = base64.b64encode(SPRITE_PATH.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <style>
        @keyframes cow-walk-path {{
            0%   {{ left: -140px; transform: scaleX(1); }}
            46%  {{ left: 100%; transform: scaleX(1); }}
            50%  {{ left: 100%; transform: scaleX(-1); }}
            96%  {{ left: -140px; transform: scaleX(-1); }}
            100% {{ left: -140px; transform: scaleX(1); }}
        }}
        @keyframes cow-walk-frames {{
            from {{ background-position-x: 0%; }}
            to   {{ background-position-x: 100%; }}
        }}
        .walking-cow {{
            position: fixed;
            bottom: 8px;
            width: 118px;
            height: 122px;
            background-image: url('data:image/png;base64,{encoded}');
            background-repeat: no-repeat;
            background-size: 400% 100%;
            pointer-events: none;
            z-index: 999999;
            filter: drop-shadow(0 6px 5px rgba(11, 37, 69, 0.18));
            animation:
                cow-walk-path 26s linear infinite,
                cow-walk-frames 0.7s steps(3) infinite;
        }}
        </style>
        <div class="walking-cow"></div>
        """,
        unsafe_allow_html=True,
    )
