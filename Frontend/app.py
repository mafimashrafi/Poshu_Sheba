import streamlit as st

from components.badges import classify_severity, get_severity_accent, render_severity_badge
from components.header import render_header
from components.mascot import render_walking_cow
from components.saved_panel import render_saved_panel
from components.sidebar import render_sidebar
from utils import api_client, theme
from utils.icons import icon

st.set_page_config(page_title="vet.ai — পশু সেবা AI", page_icon="🐄", layout="wide")

INK = theme.NAVY
MUTED = theme.SLATE
TEAL = theme.PRIMARY
TEAL_HOVER = theme.PRIMARY_HOVER
TEAL_TINT = theme.PRIMARY_TINT
MINT = theme.MINT
BORDER = theme.BORDER
AMBER = theme.AMBER
AMBER_TINT = theme.AMBER_TINT
RED = theme.RED
RED_TINT = theme.RED_TINT
BG = theme.BG

# -----------------------------
# Intake form options
# -----------------------------
# Animal selector: Bengali label shown in the UI → English value the backend's
# knowledge-base filter understands (`animal_type` form field).
ANIMAL_OPTIONS = {
    "🐄 গরু": "cow",
    "🐐 ছাগল": "goat",
    "🐔 মুরগি": "chicken",
    "🦆 হাঁস": "duck",
}

# Fixed Bengali option sets for the mandatory intake fields. The wording is
# deliberately aligned with `Backend/data/disease_knowledge_base.json` symptom
# keywords (e.g. "জ্বর", "পাতলা পায়খানা", "রক্তমিশ্রিত পায়খানা") so the backend's
# substring-matching grounding step can pick them up.
FEVER_OPTIONS = [
    "স্বাভাবিক",
    "জ্বর আছে",
    "উচ্চ তাপমাত্রা",
    "শরীর ঠান্ডা / তাপমাত্রা কম",
    "জানি না",
]
STOOL_URINE_OPTIONS = [
    "স্বাভাবিক",
    "পাতলা পায়খানা / ডায়রিয়া",
    "রক্তমিশ্রিত পায়খানা",
    "কোষ্ঠকাঠিন্য",
    "প্রস্রাবে সমস্যা",
    "জানি না",
]

# One-tap example questions that fill the description box — worded so their
# symptoms also hit the backend knowledge-base keyword matcher.
EXAMPLE_PROMPTS = [
    "গরুর মুখে ঘা, লালা ঝরছে",
    "মুরগি ঝিমাচ্ছে, সবুজ পায়খানা করছে",
    "ছাগলের পেট ফুলে গেছে, খাচ্ছে না",
]

# -----------------------------
# Session state
# -----------------------------
_DEFAULTS = {
    "token": None,
    "phone_number": None,
    "display_name": None,
    "nav_page": "home",
    "chat_response": None,
    "chat_prompt": None,
    "chat_had_image": False,
    "chat_had_audio": False,
    "response_saved": False,
    "audio_version": 0,
    "sidebar_open": False,
}
for _key, _value in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value


def toggle_sidebar() -> None:
    st.session_state.sidebar_open = not st.session_state.sidebar_open


# -----------------------------
# Login / register modal
# -----------------------------
@st.dialog("লগ ইন করুন")
def login_dialog() -> None:
    tab_login, tab_register = st.tabs(["লগ ইন", "নতুন অ্যাকাউন্ট"])

    with tab_login:
        phone = st.text_input("ফোন নম্বর", placeholder="01xxxxxxxxx", key="login_phone")
        password = st.text_input("পাসওয়ার্ড", type="password", key="login_password")
        if st.button("লগ ইন করুন", key="login_submit", type="primary", use_container_width=True):
            if not phone or not password:
                st.error("ফোন নম্বর এবং পাসওয়ার্ড দিন।")
            else:
                try:
                    result = api_client.login(phone, password)
                    st.session_state.token = result["access_token"]
                    st.session_state.phone_number = phone
                    st.rerun()
                except api_client.ApiError as exc:
                    st.error(exc.message)

    with tab_register:
        name = st.text_input("নাম (ঐচ্ছিক)", key="register_name")
        phone_r = st.text_input("ফোন নম্বর", placeholder="01xxxxxxxxx", key="register_phone")
        address_r = st.text_input("ঠিকানা", placeholder="আপনার বর্তমান ঠিকানা লিখুন", key="register_address")
        password_r = st.text_input(
            "পাসওয়ার্ড", type="password", key="register_password", help="কমপক্ষে ৮ অক্ষর"
        )
        if st.button("অ্যাকাউন্ট তৈরি করুন", key="register_submit", type="primary", use_container_width=True):
            if not phone_r or not address_r or not password_r:
                st.error("ফোন নম্বর, ঠিকানা এবং পাসওয়ার্ড দিন।")
            elif len(password_r) < 8:
                st.error("পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।")
            else:
                try:
                    api_client.register(name or None, phone_r, address_r, password_r)
                    result = api_client.login(phone_r, password_r)
                    st.session_state.token = result["access_token"]
                    st.session_state.phone_number = phone_r
                    st.session_state.display_name = name or None
                    st.rerun()
                except api_client.ApiError as exc:
                    st.error(exc.message)


@st.dialog("প্রোফাইল ও খামার আপডেট", width="large")
def profile_dialog() -> None:
    token = st.session_state.get("token")
    if not token:
        st.error("সেশন পাওয়া যায়নি। অনুগ্রহ করে আবার লগ ইন করুন।")
        return

    if "profile_data" not in st.session_state or st.session_state.get("profile_data_refetched") is not True:
        try:
            with st.spinner("প্রোফাইল লোড হচ্ছে..."):
                st.session_state.profile_data = api_client.get_profile(token)
                st.session_state.profile_data_refetched = True
        except api_client.ApiError as exc:
            st.error(exc.message)
            return

    profile = st.session_state.profile_data

    col_left, col_right = st.columns([3.5, 6.5], gap="large")

    with col_left:
        # Render circular avatar preview with object-fit: cover, border, and shadow
        avatar_url = profile.get("profile_picture_url")
        if avatar_url:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-bottom: 0.8rem;">
                    <img src="{avatar_url}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid white; box-shadow: 0 4px 12px rgba(15, 42, 61, 0.15);" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-bottom: 0.8rem;">
                    <div style="display: flex; align-items: center; justify-content: center; width: 140px; height: 140px; border-radius: 50%; background-color: {MINT}; color: {MUTED}; font-size: 3rem; font-weight: 700; border: 3px solid white; box-shadow: 0 4px 12px rgba(15, 42, 61, 0.15);">
                        👤
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Compact File uploader (label collapsed)
        uploaded_pic = st.file_uploader(
            "প্রোফাইল ছবি",
            type=["jpg", "jpeg", "png", "webp"],
            key="profile_pic_uploader",
            label_visibility="collapsed"
        )

        st.markdown(
            f"""<p style="text-align: center; color: {MUTED}; font-size: 0.78rem; margin-top: 0.4rem; line-height: 1.2;">
            JPG, PNG, WEBP<br>(সর্বোচ্চ ৫ মেগাবাইট)
            </p>""",
            unsafe_allow_html=True
        )

        # Upload handling logic (automatic upload on selection)
        if uploaded_pic is not None:
            last_uploaded_name = st.session_state.get("last_uploaded_profile_pic_name")
            if last_uploaded_name != uploaded_pic.name:
                try:
                    with st.spinner("ছবি আপলোড হচ্ছে..."):
                        res = api_client.upload_profile_picture(
                            token=token,
                            file_bytes=uploaded_pic.getvalue(),
                            filename=uploaded_pic.name,
                            mime_type=uploaded_pic.type
                        )
                    st.session_state.profile_data["profile_picture_url"] = res["profile_picture_url"]
                    st.session_state.last_uploaded_profile_pic_name = uploaded_pic.name
                    st.toast("প্রোফাইল ছবি আপলোড করা হয়েছে!", icon="📸")
                    st.rerun()
                except api_client.ApiError as exc:
                    st.error(exc.message)

    with col_right:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="color: {TEAL}; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                    👤 ব্যক্তিগত তথ্য
                </div>
                """,
                unsafe_allow_html=True
            )
            name = st.text_input("নাম", value=profile.get("name") or "", placeholder="আপনার নাম লিখুন")
            address = st.text_input("ঠিকানা", value=profile.get("address") or "", placeholder="আপনার ঠিকানা লিখুন")
            email = st.text_input("ইমেইল (ঐচ্ছিক)", value=profile.get("email") or "", placeholder="আপনার ইমেইল লিখুন")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="color: {TEAL}; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.4rem;">
                    🚜 খামারের তথ্য (ফসল ও পশুর বিবরণ)
                </div>
                """,
                unsafe_allow_html=True
            )

            farms = profile.get("farms") or []
            updated_farms = []

            for idx, farm in enumerate(farms):
                col_type, col_count, col_del = st.columns([5, 3, 2], vertical_alignment="bottom")
                with col_type:
                    animal_type = st.text_input(f"পশুর ধরণ #{idx+1}", value=farm.get("animal_type") or "", key=f"farm_type_{idx}")
                with col_count:
                    count = st.number_input(f"সংখ্যা #{idx+1}", value=int(farm.get("count") or 1), min_value=1, step=1, key=f"farm_count_{idx}")
                with col_del:
                    is_deleted = st.checkbox("মুছুন", key=f"farm_delete_{idx}")

                if not is_deleted and animal_type.strip():
                    updated_farms.append({"animal_type": animal_type.strip(), "count": count})

            st.markdown("---")
            st.markdown("**নতুন পশুর তথ্য যোগ করুন:**")
            new_col_type, new_col_count = st.columns([6, 4])
            with new_col_type:
                new_animal_type = st.text_input("পশুর ধরণ (যেমন: গরু, ছাগল)", key="new_farm_type_input")
            with new_col_count:
                new_count = st.number_input("সংখ্যা", value=1, min_value=1, step=1, key="new_farm_count_input")

        st.markdown("---")

        show_confirm = st.session_state.get("show_delete_confirm", False)

        if show_confirm:
            st.warning("আপনি কি নিশ্চিত যে আপনি আপনার অ্যাকাউন্ট এবং সমস্ত সেভ করা উত্তর মুছে ফেলতে চান? এটি আর ফেরত আনা যাবে না।")
            del_col1, del_col2 = st.columns(2)
            with del_col1:
                if st.button("হ্যাঁ, মুছে ফেলুন", key="confirm_delete_btn", type="primary", use_container_width=True):
                    try:
                        with st.spinner("অ্যাকাউন্ট মুছে ফেলা হচ্ছে..."):
                            api_client.delete_account(token)
                        st.session_state.token = None
                        st.session_state.phone_number = None
                        st.session_state.display_name = None
                        st.session_state.nav_page = "home"
                        st.session_state.show_delete_confirm = False
                        st.session_state.profile_data = None
                        st.session_state.profile_data_refetched = False
                        st.success("অ্যাকাউন্টটি মুছে ফেলা হয়েছে।")
                        st.rerun()
                    except api_client.ApiError as exc:
                        st.error(exc.message)
            with del_col2:
                if st.button("না, বাতিল করুন", key="cancel_delete_btn", use_container_width=True):
                    st.session_state.show_delete_confirm = False
                    # No st.rerun() here to keep the dialog open and go back to the profile form
        else:
            col_save, col_delete = st.columns([5.8, 4.2])
            with col_save:
                if st.button("তথ্য সংরক্ষণ করুন", key="profile_save_btn", type="primary", use_container_width=True):
                    payload = {
                        "name": name.strip() or None,
                        "address": address.strip(),
                        "email": email.strip() or None,
                        "profile_picture_url": profile.get("profile_picture_url"),
                        "farms": updated_farms
                    }

                    if new_animal_type.strip():
                        payload["farms"].append({"animal_type": new_animal_type.strip(), "count": int(new_count)})

                    if not payload["address"]:
                        st.error("ঠিকানা ফাঁকা রাখা যাবে না।")
                        return

                    try:
                        with st.spinner("সংরক্ষণ করা হচ্ছে..."):
                            api_client.update_profile(token, payload)
                        st.session_state.display_name = payload["name"] or None
                        st.session_state.profile_data_refetched = False
                        st.toast("প্রোফাইল সফলভাবে আপডেট করা হয়েছে!", icon="✅")
                        st.rerun()
                    except api_client.ApiError as exc:
                        st.error(exc.message)

            with col_delete:
                if st.button("অ্যাকাউন্ট মুছুন", key="profile_delete_btn", type="secondary", use_container_width=True):
                    st.session_state.show_delete_confirm = True
                    # No st.rerun() here to keep the dialog open and switch to confirmation view





# -----------------------------
# Styling
# -----------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"],
    *:not([data-testid="stIconMaterial"]), *::before, *::after {{
        font-family: 'Inter', 'Noto Sans Bengali', -apple-system, sans-serif !important;
    }}

    /* Fluid base size: every rem-based font in the app scales up a little
       and adapts to the viewport instead of staying fixed on mobile. */
    html {{ font-size: clamp(16px, 0.55vw + 15px, 18px); }}

    [data-testid="stAppViewContainer"] {{ background: {BG}; }}

    @media (max-width: 640px) {{
        .block-container {{ padding-left: 0.9rem !important; padding-right: 0.9rem !important; }}
        div.st-key-app_header {{ padding: 0.7rem 1rem !important; }}
    }}

    /* ---- Redesigned Profile Dialog Modals ----
       IMPORTANT: only scope sizing to the inner `[role="dialog"]` element.
       Streamlit's own full-viewport modal backdrop (`[data-testid="stDialog"]`,
       position:fixed;inset:0) also carries a class containing "stDialog", so a
       selector like `[class*="stDialog"]` matches the backdrop too — shrinking
       its width/margin turns the full-screen dim overlay into a narrow dark
       vertical band around the dialog card. Keeping the selector scoped to
       `[role="dialog"]` avoids resizing the backdrop. */
    div[role="dialog"],
    div[data-testid="stDialog"] div[role="dialog"] {{
        max-width: 780px !important;
        width: 90vw !important;
        margin: 0 auto !important;
    }}

    /* Soften the dialog card's default shadow to match the app's other soft,
       navy-tinted card shadows instead of the heavier default. */
    div[data-testid="stDialog"] > div {{
        box-shadow: 0 16px 40px rgba(15, 42, 61, 0.16) !important;
        border-radius: 20px !important;
    }}

    /* Hide popover dropdown body completely when the dialog is open in DOM */
    body:has(div[data-testid="stDialog"]) div[data-testid="stPopoverBody"],
    body:has(div[data-testid="stDialog"]) div[class*="stPopoverBody"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }}

    /* Popover Menu Dropdown Animation */
    @keyframes fadeSlideDown {{
        from {{
            opacity: 0;
            transform: translateY(-8px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    div[data-testid="stPopoverBody"],
    div[class*="stPopoverBody"] {{
        animation: fadeSlideDown 0.2s ease-out !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(15, 42, 61, 0.1) !important;
    }}

    /* Themed container cards inside the profile dialog */
    div[role="dialog"] div[data-testid="stVerticalBlockBorderContainer"] {{
        background-color: {MINT} !important;
        border: 1px solid {BORDER} !important;
        border-left: 4px solid {TEAL} !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 2px 8px rgba(15, 42, 61, 0.02) !important;
    }}

    /* Button and File Uploader animations */
    div[class*="st-key-profile_save_btn"] button {{
        background-color: {TEAL} !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-profile_save_btn"] button:hover {{
        background-color: {TEAL_HOVER} !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 12px {TEAL_TINT} !important;
    }}

    div[class*="st-key-profile_delete_btn"] button {{
        background-color: transparent !important;
        color: {RED} !important;
        border: 1px solid {RED} !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-profile_delete_btn"] button:hover {{
        background-color: {RED} !important;
        color: white !important;
        transform: scale(1.02) !important;
        filter: brightness(0.94) !important;
    }}

    div[class*="st-key-confirm_delete_btn"] button {{
        background-color: {RED} !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-confirm_delete_btn"] button:hover {{
        filter: brightness(0.88) !important;
        transform: scale(1.02) !important;
    }}

    div[class*="st-key-cancel_delete_btn"] button {{
        background-color: {BORDER} !important;
        color: {MUTED} !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-cancel_delete_btn"] button:hover {{
        filter: brightness(0.96) !important;
        transform: scale(1.02) !important;
    }}

    div[class*="st-key-profile_pic_uploader"] {{
        max-width: 100% !important;
    }}
    div[class*="st-key-profile_pic_uploader"] section {{
        padding: 0.5rem !important;
        background-color: {MINT} !important;
        border-radius: 8px !important;
        border: 1px dashed {BORDER} !important;
    }}
    div[class*="st-key-profile_pic_uploader"] label {{
        display: none !important;
    }}
    div[class*="st-key-profile_pic_uploader"] button {{
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-profile_pic_uploader"] button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 4px 12px rgba(15, 42, 61, 0.1) !important;
    }}

    /* Light pastel input styling for Profile Dialog inputs */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {{
        background-color: {MINT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.8rem !important;
        color: {TEAL} !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {{
        background-color: #FFFFFF !important;
        border-color: {TEAL} !important;
        color: {INK} !important;
        box-shadow: 0 0 0 3px {TEAL_TINT} !important;
    }}

    /* Number input stepper button hover state transition */
    div[role="dialog"] button[data-testid*="InputStep"] {{
        transition: all 0.18s ease-in-out !important;
    }}
    div[role="dialog"] button[data-testid*="InputStep"]:hover {{
        background-color: {MINT} !important;
        color: {TEAL} !important;
    }}

    #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}

    .block-container {{ padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1360px; }}


    h1, h2, h3 {{ color: {INK}; font-weight: 700; letter-spacing: -0.01em; }}

    ::selection {{ background: {TEAL_TINT}; }}

    .stButton > button {{ border-radius: 12px; font-weight: 600; transition: all 0.18s ease; box-shadow: none; }}
    .stButton > button:hover {{ transform: translateY(-1px); }}
    .stButton > button:active {{ transform: translateY(0); }}

    /* ---- Header ---- */
    div.st-key-app_header {{
        background: #FFFFFF; border-radius: 18px; padding: 0.8rem 1.4rem; margin-bottom: 1.8rem;
        box-shadow: 0 2px 16px rgba(15, 42, 61, 0.05); border: 1px solid {BORDER};
    }}
    div.st-key-sidebar_toggle_wrap button {{
        background: transparent !important; border: none !important; box-shadow: none !important;
        color: {INK} !important; border-radius: 10px !important; padding: 0.5rem !important;
        min-width: auto !important;
    }}
    div.st-key-sidebar_toggle_wrap button:hover {{ background: {MINT} !important; color: {TEAL} !important; transform: none !important; }}
    div.st-key-logo_brand {{ position: relative; }}
    div.st-key-logo_brand .st-key-logo_home_btn {{
        position: absolute !important; inset: 0 !important; width: 100% !important; height: 100% !important;
        z-index: 5;
    }}
    div.st-key-logo_brand .st-key-logo_home_btn > div,
    div.st-key-logo_brand .st-key-logo_home_btn [data-testid="stElementContainer"] {{
        width: 100% !important; height: 100% !important;
    }}
    div.st-key-logo_brand .st-key-logo_home_btn button {{
        width: 100%; height: 100%; min-height: 48px; opacity: 0; cursor: pointer; padding: 0;
    }}
    div.st-key-header_login button {{
        background: {TEAL}; border: none; border-radius: 999px; color: white;
        box-shadow: 0 6px 16px {TEAL_TINT};
    }}
    div.st-key-header_login button:hover {{ background: {TEAL_HOVER}; box-shadow: 0 8px 20px {TEAL_TINT}; }}

    /* ---- Sidebar: "Ask a new question" primary CTA ---- */
    div.st-key-sidebar_ask_cta button {{
        background: {TEAL}; border: none; border-radius: 999px; color: white;
        font-weight: 700; padding: 0.8rem 1rem; box-shadow: 0 6px 16px {TEAL_TINT};
    }}
    div.st-key-sidebar_ask_cta button:hover {{ background: {TEAL_HOVER}; box-shadow: 0 8px 20px {TEAL_TINT}; }}

    /* ---- Sidebar links ("saved answers" / "usage guide") ---- */
    div.st-key-sidebar_nav .stButton > button {{
        background: transparent; border: none; text-align: left; justify-content: flex-start;
        color: {MUTED}; font-weight: 500; padding: 0.6rem 0.9rem; border-radius: 11px;
    }}
    div.st-key-sidebar_nav .stButton > button:hover {{ background: {MINT}; color: {TEAL}; transform: none; }}
    div.st-key-sidebar_nav button[kind="primary"] {{
        background: {MINT}; color: {TEAL}; font-weight: 700; box-shadow: none;
        border-left: 3px solid {TEAL};
    }}

    /* ---- Cards ---- */
    div[class*="st-key-saved_panel_"], div.st-key-card_image, div.st-key-card_audio,
    div.st-key-response_card {{
        background: {MINT}; border-radius: 18px; padding: 1.35rem 1.25rem;
        box-shadow: 0 2px 16px rgba(15, 42, 61, 0.05); border: 1px solid {BORDER};
    }}
    div.st-key-card_image, div.st-key-card_audio {{
        text-align: center; transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}
    div.st-key-card_image:hover, div.st-key-card_audio:hover {{
        box-shadow: 0 8px 24px rgba(15, 42, 61, 0.09); transform: translateY(-2px);
    }}
    div[class*="st-key-saved_locked_"] {{ background: #FFFFFF; border-radius: 14px; padding: 1rem 1rem 1.4rem; margin-top: 0.4rem; }}

    .upload-icon-circle {{
        width: 54px; height: 54px; border-radius: 50%; background: #FFFFFF;
        display: flex; align-items: center; justify-content: center; margin: 0 auto 0.65rem;
    }}
    .upload-card-title {{ font-weight: 700; color: {INK}; margin-bottom: 0.2rem; }}
    .upload-card-sub {{ color: {MUTED}; font-size: 0.82rem; margin-bottom: 0.8rem; }}

    .or-divider {{
        display: flex; align-items: center; gap: 0.9rem; color: {MUTED}; font-size: 0.88rem; margin: 1.6rem 0 1.1rem;
    }}
    .or-divider::before, .or-divider::after {{ content: ""; flex: 1; height: 1px; background: {BORDER}; }}

    .info-bar {{
        display: flex; align-items: center; justify-content: center; gap: 0.5rem;
        color: {MUTED}; font-size: 0.84rem; margin-top: 1.5rem;
    }}

    /* ---- Animal type pills ---- */
    div.st-key-animal_pills [data-testid="stPills"] {{ justify-content: center; gap: 0.5rem; }}
    div.st-key-animal_pills button {{
        border-radius: 999px !important; border: 1.5px solid {BORDER} !important;
        background: #FFFFFF !important; color: {MUTED} !important; font-weight: 600 !important;
        padding: 0.45rem 1.15rem !important; transition: all 0.18s ease !important;
        box-shadow: 0 2px 8px rgba(15, 42, 61, 0.04) !important;
    }}
    div.st-key-animal_pills button:hover {{
        border-color: {TEAL} !important; color: {TEAL} !important; transform: translateY(-1px);
    }}
    div.st-key-animal_pills button[aria-checked="true"],
    div.st-key-animal_pills button[aria-checked="true"]:hover {{
        background: {TEAL} !important; border-color: {TEAL} !important; color: #FFFFFF !important;
        box-shadow: 0 6px 16px {TEAL_TINT} !important;
    }}
    div.st-key-animal_pills button p {{ color: inherit !important; }}
    div.st-key-animal_pills button[aria-checked="true"] p {{ color: #FFFFFF !important; }}

    /* ---- Mandatory intake card (age / fever / stool-urine) ---- */
    div.st-key-intake_card {{
        background: #FFFFFF; border-radius: 18px; padding: 1.15rem 1.25rem 0.9rem;
        box-shadow: 0 2px 16px rgba(15, 42, 61, 0.05); border: 1px solid {BORDER};
        border-left: 4px solid {TEAL};
    }}
    div.st-key-intake_card label p {{ color: {MUTED} !important; font-weight: 600 !important; font-size: 0.85rem !important; }}
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background-color: {MINT} !important; border: 1px solid {BORDER} !important;
        border-radius: 8px !important; transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {{
        background-color: #FFFFFF !important; border-color: {TEAL} !important;
        box-shadow: 0 0 0 3px {TEAL_TINT} !important;
    }}

    /* ---- Live input-summary chips ---- */
    .form-section-label {{
        text-align: center; color: {INK}; font-weight: 700; font-size: 0.95rem;
        margin: 1.1rem 0 0.55rem;
    }}
    .input-chips {{
        display: flex; flex-wrap: wrap; gap: 0.45rem; justify-content: center;
        margin: 0.9rem 0 0.3rem;
    }}
    .input-chip {{
        background: {MINT}; color: {TEAL}; border: 1px solid {BORDER};
        border-radius: 999px; padding: 0.22rem 0.75rem; font-size: 0.8rem; font-weight: 600;
        animation: fadeSlideDown 0.2s ease-out;
    }}
    .input-chip.chip-missing {{ background: {AMBER_TINT}; color: {AMBER}; border-color: {AMBER}; }}

    /* ---- Ask form controls ---- */
    /* The main question box styled as a soft rounded "pill" CTA — the
       primary way farmers start a request. */
    div.st-key-ask_text_wrap .stTextArea textarea {{
        border-radius: 24px !important; border: 1.5px solid {BORDER} !important;
        background: #FFFFFF !important; padding: 1.1rem 1.4rem !important;
        box-shadow: 0 2px 12px rgba(15, 42, 61, 0.04) !important; font-size: 1rem !important;
    }}
    div.st-key-ask_text_wrap .stTextArea textarea:focus {{
        border-color: {TEAL} !important; box-shadow: 0 0 0 3px {TEAL_TINT} !important;
    }}
    div.st-key-ask_submit button {{
        background: {TEAL}; border: none; border-radius: 999px; color: white;
        box-shadow: 0 6px 16px {TEAL_TINT};
    }}
    div.st-key-ask_submit button:hover {{ background: {TEAL_HOVER}; box-shadow: 0 8px 20px {TEAL_TINT}; }}
    div.st-key-save_response_btn button {{ border-radius: 999px; background: {TEAL}; border: none; }}
    div.st-key-save_response_btn button:hover {{ background: {TEAL_HOVER}; }}
    div.st-key-remove_audio_btn button {{
        background: transparent; border: none; color: {RED}; font-weight: 500;
        font-size: 0.82rem; padding: 0.3rem; margin-top: 0.3rem; box-shadow: none;
    }}
    div.st-key-remove_audio_btn button:hover {{ background: {RED_TINT}; transform: none; }}
    .stTextArea textarea {{ border-radius: 14px; }}
    [data-testid="stFileUploaderDropzone"] {{ border-radius: 12px; }}

    /* ---- Saved response items ---- */
    div[class*="st-key-saved_item_"] {{
        border-radius: 12px !important; margin-bottom: 0.6rem !important; padding: 0.85rem !important;
        background: #FFFFFF !important; border-color: {BORDER} !important;
        transition: box-shadow 0.15s ease;
    }}
    div[class*="st-key-saved_item_"]:hover {{ box-shadow: 0 3px 12px rgba(15, 42, 61, 0.08); }}

    /* ---- Response card severity accent ---- */
    div.st-key-response_card {{ border-left-width: 4px !important; border-left-style: solid !important; transition: border-color 0.2s ease; }}

    /* ---- Footer ---- */
    .app-footer {{
        margin-top: 2.2rem; padding-top: 1.4rem;
        border-top: 1px solid {BORDER};
    }}
    .app-footer-brand {{ display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.6rem; }}
    .app-footer-dot {{ width: 6px; height: 6px; border-radius: 50%; background: {TEAL}; display: inline-block; }}
    .app-footer-links {{
        display: flex; align-items: center; justify-content: center; gap: 0.9rem;
        color: {MUTED}; font-size: 0.85rem; flex-wrap: wrap;
    }}
    .app-footer-links a {{ color: {MUTED}; text-decoration: none; transition: color 0.15s ease; }}
    .app-footer-links a:hover {{ color: {TEAL}; }}
    .app-footer-sep {{ color: {BORDER}; }}
    .app-footer-meta {{
        text-align: center; color: {MUTED}; font-size: 0.76rem; margin-top: 0.6rem; opacity: 0.85;
    }}

    /* ================= UI polish ================= */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to   {{ opacity: 1; transform: none; }}
    }}

    /* Soft ambient gradient washes over the flat page background */
    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(1100px 520px at 12% -12%, {TEAL_TINT}, transparent 60%),
            radial-gradient(900px 440px at 88% -6%, {AMBER_TINT}, transparent 55%),
            {BG};
    }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {TEAL}; }}

    /* ---- Hero ---- */
    .hero-wrap {{ text-align: center; margin-bottom: 0.9rem; animation: fadeInUp 0.5s ease-out; }}
    .hero-badge {{
        display: inline-flex; align-items: center; gap: 0.45rem;
        background: #FFFFFF; border: 1px solid {BORDER}; color: {TEAL};
        font-weight: 700; font-size: 0.78rem; letter-spacing: 0.02em;
        padding: 0.32rem 0.95rem; border-radius: 999px;
        box-shadow: 0 2px 12px rgba(15, 42, 61, 0.06); margin-bottom: 1rem;
    }}
    .hero-title {{
        margin: 0 0 0.4rem; line-height: 1.28; font-size: 2.15rem;
        font-weight: 800; color: {INK}; letter-spacing: -0.015em;
    }}
    .hero-title .accent {{
        background: linear-gradient(100deg, {TEAL} 0%, {TEAL_HOVER} 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent;
    }}
    .hero-sub {{ color: {MUTED}; font-size: 1.02rem; margin: 0 auto; max-width: 34rem; }}
    .hero-features {{
        display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; margin-top: 1.05rem;
    }}
    .hero-feature {{
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: {MINT}; border: 1px solid {BORDER}; border-radius: 999px;
        color: {INK}; font-size: 0.8rem; font-weight: 600; padding: 0.3rem 0.85rem;
    }}
    @media (max-width: 640px) {{
        .hero-title {{ font-size: 1.6rem; }}
    }}

    /* ---- Numbered section labels ---- */
    .form-section-label {{ display: flex; align-items: center; justify-content: center; gap: 0.5rem; }}
    .step-chip {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 22px; height: 22px; border-radius: 50%; flex: 0 0 auto;
        background: {TEAL}; color: #FFFFFF; font-size: 0.72rem; font-weight: 700;
        box-shadow: 0 3px 8px {TEAL_TINT};
    }}

    /* ---- "অথবা" divider pill ---- */
    .or-divider > span {{
        background: #FFFFFF; border: 1px solid {BORDER}; border-radius: 999px;
        padding: 0.22rem 0.95rem; font-weight: 600; font-size: 0.82rem;
        box-shadow: 0 2px 8px rgba(15, 42, 61, 0.05);
    }}

    /* ---- Upload cards ---- */
    .upload-icon-circle {{
        border: 1px solid {BORDER}; box-shadow: 0 0 0 6px {TEAL_TINT};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    div.st-key-card_image:hover .upload-icon-circle,
    div.st-key-card_audio:hover .upload-icon-circle {{
        transform: scale(1.07); box-shadow: 0 0 0 10px {TEAL_TINT};
    }}
    [data-testid="stFileUploaderDropzone"] {{
        border: 1.5px dashed {BORDER} !important; background: #FFFFFF !important;
        transition: border-color 0.2s ease, background 0.2s ease;
    }}
    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {TEAL} !important; background: {TEAL_TINT} !important;
    }}

    /* ---- Example prompt chips ---- */
    .examples-label {{
        text-align: center; color: {MUTED}; font-size: 0.8rem;
        margin: 0.7rem 0 0.35rem; font-weight: 600;
    }}
    div.st-key-example_chips .stButton > button {{
        background: #FFFFFF; border: 1px solid {BORDER}; border-radius: 999px;
        color: {MUTED}; font-size: 0.82rem; font-weight: 500; padding: 0.4rem 0.8rem;
        box-shadow: none; white-space: normal; line-height: 1.35; min-height: 2.5rem;
    }}
    div.st-key-example_chips .stButton > button:hover {{
        border-color: {TEAL}; color: {TEAL}; background: {MINT}; transform: translateY(-1px);
    }}

    /* ---- Submit CTA ---- */
    div.st-key-ask_submit button {{
        background: linear-gradient(135deg, {TEAL} 0%, {TEAL_HOVER} 100%) !important;
        padding: 0.8rem 1rem !important; font-size: 1.02rem !important;
        font-weight: 700 !important; letter-spacing: 0.01em !important;
    }}
    div.st-key-ask_submit button:hover {{
        transform: translateY(-2px); box-shadow: 0 12px 28px {TEAL_TINT} !important;
    }}

    /* ---- Response card ---- */
    div.st-key-response_card {{
        animation: fadeInUp 0.45s ease-out;
        background: linear-gradient(180deg, #FFFFFF 0%, {MINT} 170%) !important;
    }}
    .response-title-lockup {{ display: flex; align-items: center; gap: 0.55rem; }}
    .response-title-icon {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 10px; background: {TEAL_TINT}; flex: 0 0 auto;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def open_login_dialog() -> None:
    login_dialog()


def open_profile_dialog() -> None:
    # Clear delete confirm flag when opening the dialog
    st.session_state.show_delete_confirm = False
    profile_dialog()


# -----------------------------
# Header
# -----------------------------
render_header(
    on_open_login=open_login_dialog,
    on_open_profile=open_profile_dialog,
    on_toggle_sidebar=toggle_sidebar,
    sidebar_open=st.session_state.sidebar_open,
)

if st.session_state.get("show_profile_dialog"):
    st.session_state.show_profile_dialog = False
    open_profile_dialog()

render_walking_cow()

# -----------------------------
# Body layout
# -----------------------------
nav_page = st.session_state.nav_page


def render_main_content() -> None:
    if nav_page == "home":
        # An example chip was tapped on the previous run: fill the question box
        # before the text_area widget is instantiated.
        pending_example = st.session_state.pop("pending_example", None)
        if pending_example:
            st.session_state.ask_text = pending_example

        st.markdown(
            f"""
            <div class="hero-wrap">
                <div class="hero-badge">{icon("leaf", color=TEAL, size=14)} AI পশু স্বাস্থ্য সহকারী</div>
                <h1 class="hero-title">পশু সেবা AI এ <span class="accent">আপনাকে স্বাগতম</span></h1>
                <p class="hero-sub">
                    আপনার পশুর সমস্যা লিখুন, ছবি দিন বা কথা বলুন — আমাদের AI সহকারী দ্রুত পরামর্শ দেবে।
                </p>
                <div class="hero-features">
                    <span class="hero-feature">{icon("camera", color=TEAL, size=14)} ছবি বিশ্লেষণ</span>
                    <span class="hero-feature">{icon("mic", color=TEAL, size=14)} বাংলা অডিও</span>
                    <span class="hero-feature">{icon("shield-check", color=TEAL, size=14)} রোগ তথ্যভান্ডারে যাচাই</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="form-section-label"><span class="step-chip">১</span>কোন পশুর সমস্যা?</p>',
            unsafe_allow_html=True,
        )
        with st.container(key="animal_pills"):
            st.pills(
                "পশুর ধরন",
                options=list(ANIMAL_OPTIONS),
                key="ask_animal",
                label_visibility="collapsed",
            )

        st.markdown(
            '<p class="form-section-label"><span class="step-chip">২</span>পশুর প্রাথমিক তথ্য <span style="color:'
            f'{RED};">*</span></p>',
            unsafe_allow_html=True,
        )
        with st.container(key="intake_card", border=True):
            col_age, col_fever, col_stool = st.columns(3)
            with col_age:
                st.number_input(
                    "বয়স (বছর)",
                    min_value=0.0,
                    max_value=40.0,
                    value=None,
                    step=0.5,
                    format="%g",
                    placeholder="যেমন: ২",
                    key="ask_age",
                )
            with col_fever:
                st.selectbox(
                    "জ্বর / শরীরের তাপমাত্রা",
                    FEVER_OPTIONS,
                    index=None,
                    placeholder="বেছে নিন",
                    key="ask_fever",
                )
            with col_stool:
                st.selectbox(
                    "পায়খানা / প্রস্রাবের অবস্থা",
                    STOOL_URINE_OPTIONS,
                    index=None,
                    placeholder="বেছে নিন",
                    key="ask_stool",
                )

        st.markdown(
            '<p class="form-section-label"><span class="step-chip">৩</span>সমস্যার বিবরণ দিন</p>',
            unsafe_allow_html=True,
        )
        with st.container(key="ask_text_wrap"):
            st.text_area(
                "প্রশ্ন",
                placeholder="এখানে আপনার পশুর সমস্যাটি লিখুন...",
                key="ask_text",
                height=130,
                label_visibility="collapsed",
            )

        st.markdown('<p class="examples-label">উদাহরণ — চেপে দেখুন:</p>', unsafe_allow_html=True)
        with st.container(key="example_chips"):
            example_cols = st.columns(len(EXAMPLE_PROMPTS))
            for i, (example_col, example) in enumerate(zip(example_cols, EXAMPLE_PROMPTS)):
                with example_col:
                    if st.button(example, key=f"example_chip_{i}", use_container_width=True):
                        st.session_state.pending_example = example
                        st.rerun()

        st.markdown('<div class="or-divider"><span>অথবা</span></div>', unsafe_allow_html=True)

        img_col, audio_col = st.columns(2)
        with img_col:
            with st.container(key="card_image", border=True):
                st.markdown(
                    f"""
                    <div class="upload-icon-circle">{icon("camera", color=TEAL, size=26)}</div>
                    <p class="upload-card-title">ছবি যোগ করুন</p>
                    <p class="upload-card-sub">পশুর সমস্যা বা রোগের ছবি দিন</p>
                    """,
                    unsafe_allow_html=True,
                )
                st.file_uploader(
                    "ছবি",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key="ask_images",
                    label_visibility="collapsed",
                )
        with audio_col:
            with st.container(key="card_audio", border=True):
                st.markdown(
                    f"""
                    <div class="upload-icon-circle">{icon("mic", color=TEAL, size=26)}</div>
                    <p class="upload-card-title">অডিও রেকর্ড করুন</p>
                    <p class="upload-card-sub">বাংলায় সমস্যার বিবরণ দিন</p>
                    """,
                    unsafe_allow_html=True,
                )
                audio_key = f"ask_audio_{st.session_state.audio_version}"
                st.audio_input("অডিও", key=audio_key, label_visibility="collapsed")
                if st.session_state.get(audio_key) is not None:
                    if st.button(
                        "অডিও সরিয়ে ফেলুন",
                        key="remove_audio_btn",
                        icon=":material/close:",
                        use_container_width=True,
                    ):
                        st.session_state.audio_version += 1
                        st.rerun()

        # Live summary of everything that will be sent — Streamlit reruns on each
        # widget change, so these chips update as the farmer fills the form.
        age_val = st.session_state.get("ask_age")
        fever_val = st.session_state.get("ask_fever")
        stool_val = st.session_state.get("ask_stool")
        animal_label = st.session_state.get("ask_animal")
        text_now = (st.session_state.get("ask_text") or "").strip()
        images_now = st.session_state.get("ask_images") or []
        audio_now = st.session_state.get(audio_key)

        chips = []
        if animal_label:
            chips.append(f'<span class="input-chip">{animal_label}</span>')
        chips.append(
            f'<span class="input-chip">বয়স: {age_val:g} বছর</span>'
            if age_val is not None
            else '<span class="input-chip chip-missing">বয়স দিন</span>'
        )
        chips.append(
            f'<span class="input-chip">জ্বর: {fever_val}</span>'
            if fever_val
            else '<span class="input-chip chip-missing">জ্বরের অবস্থা বেছে নিন</span>'
        )
        chips.append(
            f'<span class="input-chip">পায়খানা/প্রস্রাব: {stool_val}</span>'
            if stool_val
            else '<span class="input-chip chip-missing">পায়খানা/প্রস্রাবের অবস্থা বেছে নিন</span>'
        )
        if text_now:
            chips.append('<span class="input-chip">লিখিত বিবরণ ✓</span>')
        if images_now:
            chips.append(f'<span class="input-chip">ছবি: {len(images_now)}টি</span>')
        if audio_now is not None:
            chips.append('<span class="input-chip">অডিও ✓</span>')
        st.markdown(f'<div class="input-chips">{"".join(chips)}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        submitted = st.button(
            "জমা দিন", key="ask_submit", icon=":material/send:", type="primary", use_container_width=True
        )

        st.markdown(
            f'<div class="info-bar">{icon("info", color=MUTED, size=15)} মনে রাখবেন, AI ভুল করতে পারে</div>',
            unsafe_allow_html=True,
        )

        if submitted:
            missing = []
            if age_val is None:
                missing.append("পশুর বয়স")
            if not fever_val:
                missing.append("জ্বরের অবস্থা")
            if not stool_val:
                missing.append("পায়খানা/প্রস্রাবের অবস্থা")

            if missing:
                st.error("অনুগ্রহ করে এই তথ্যগুলো দিন: " + ", ".join(missing))
            elif not text_now and not images_now and audio_now is None:
                st.error("লিখিত তথ্য, ছবি অথবা অডিও এর থেকে কমপক্ষে একটি দিন।")
            else:
                # The backend expects `age` as a JSON number; send whole years
                # as an int so the prompt reads "age: 3" rather than "age: 3.0".
                age_json = int(age_val) if float(age_val).is_integer() else age_val
                info = {"age": age_json, "fever": fever_val, "stool_urine": stool_val}
                animal_value = ANIMAL_OPTIONS.get(animal_label) if animal_label else None
                try:
                    with st.spinner("AI উত্তর তৈরি করছে..."):
                        response_text = api_client.generate(
                            info, text_now, images_now, audio_now, animal_type=animal_value
                        )
                    prompt_parts = [p for p in (animal_label, f"বয়স: {age_json} বছর", f"জ্বর: {fever_val}", f"পায়খানা/প্রস্রাব: {stool_val}", text_now) if p]
                    st.session_state.chat_response = response_text
                    st.session_state.chat_prompt = " | ".join(prompt_parts) or None
                    st.session_state.chat_had_image = bool(images_now)
                    st.session_state.chat_had_audio = audio_now is not None
                    st.session_state.response_saved = False
                except api_client.ApiError as exc:
                    st.session_state.chat_response = None
                    st.error(exc.message)

        if st.session_state.get("chat_response"):
            st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
            with st.container(key="response_card", border=True):
                severity = classify_severity(st.session_state.chat_response)
                st.markdown(
                    f"<style>div.st-key-response_card {{ border-left-color: {get_severity_accent(severity)} !important; }}</style>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                gap:0.6rem;margin-bottom:0.8rem;flex-wrap:wrap;">
                        <div class="response-title-lockup">
                            <span class="response-title-icon">{icon("chat", color=TEAL, size=17)}</span>
                            <div style="line-height:1.3;">
                                <p style="font-weight:700;color:{INK};margin:0;">AI-এর পরামর্শ</p>
                                <p style="color:{MUTED};font-size:0.74rem;margin:0;">প্রাথমিক পরামর্শ — চূড়ান্ত রোগ নির্ণয় নয়</p>
                            </div>
                        </div>
                        {render_severity_badge(severity)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(st.session_state.chat_response)
                st.divider()
                if st.session_state.get("response_saved"):
                    st.success("উত্তরটি সংরক্ষণ করা হয়েছে।")
                elif st.button(
                    "সংরক্ষণ করুন", key="save_response_btn", icon=":material/bookmark_added:", type="primary"
                ):
                    token = st.session_state.get("token")
                    if not token:
                        open_login_dialog()
                    else:
                        try:
                            api_client.save_response(
                                token,
                                st.session_state.chat_response,
                                prompt=st.session_state.chat_prompt,
                                had_image=st.session_state.chat_had_image,
                                had_audio=st.session_state.chat_had_audio,
                            )
                            st.session_state.response_saved = True
                            st.rerun()
                        except api_client.SessionExpiredError as exc:
                            st.session_state.token = None
                            st.session_state.phone_number = None
                            st.session_state.display_name = None
                            st.warning(exc.message)
                        except api_client.ApiError as exc:
                            st.error(exc.message)

    elif nav_page == "saved":
        st.markdown(f"<h2>সেভ করা উত্তরসমূহ</h2>", unsafe_allow_html=True)
        render_saved_panel(open_login_dialog, compact=False)

    elif nav_page == "guide":
        st.markdown("<h2>ব্যবহার নির্দেশিকা</h2>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <ol style="color:{INK};font-size:0.98rem;line-height:2;">
                <li>উপরের ডান দিক থেকে লগ ইন করুন অথবা নতুন অ্যাকাউন্ট খুলুন (ঐচ্ছিক)।</li>
                <li>"নতুন প্রশ্ন করুন" পাতায় পশুর ধরন বেছে নিন এবং বয়স, জ্বর ও পায়খানা/প্রস্রাবের অবস্থা দিন।</li>
                <li>এরপর পশুর সমস্যা লিখুন, ছবি দিন অথবা অডিও রেকর্ড করুন।</li>
                <li>"জমা দিন" চাপুন এবং AI-এর পরামর্শ পড়ুন।</li>
                <li>উত্তর ভালো লাগলে "সংরক্ষণ করুন" চেপে ভবিষ্যতের জন্য সংরক্ষণ করুন।</li>
                <li>"সেভ করা উত্তরসমূহ" পাতায় গিয়ে যেকোনো সময় পুরনো উত্তর দেখুন।</li>
            </ol>
            <p style="color:{MUTED};">
                মনে রাখবেন: AI সবসময় সঠিক নাও হতে পারে। জরুরি অবস্থায় নিকটস্থ পশু চিকিৎসকের সাথে যোগাযোগ করুন।
            </p>
            """,
            unsafe_allow_html=True,
        )

if st.session_state.sidebar_open:
    sidebar_col, main_col = st.columns([1.1, 3.5], gap="large")
    with sidebar_col:
        render_sidebar(open_login_dialog)
    with main_col:
        render_main_content()
else:
    # No sidebar: center the chat column instead of letting it stretch to the
    # full block-container width, keeping the focused, ChatGPT-like feel.
    _left_pad, centered_col, _right_pad = st.columns([1, 6, 1])
    with centered_col:
        render_main_content()

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    f"""
    <div class="app-footer">
        <div class="app-footer-brand">
            <span style="font-weight:800;color:{INK};font-size:0.95rem;">vet<span style="color:{TEAL};">.ai</span></span>
            <span class="app-footer-dot"></span>
            <span style="color:{MUTED};font-size:0.8rem;">পশু সেবা AI</span>
        </div>
        <div class="app-footer-links">
            <a href="#">গোপনীয়তা নীতি</a>
            <span class="app-footer-sep">•</span>
            <a href="#">শর্তাবলী</a>
            <span class="app-footer-sep">•</span>
            <a href="#">যোগাযোগ করুন</a>
        </div>
        <p class="app-footer-meta">© 2026 Poshu Sheba AI</p>
    </div>
    """,
    unsafe_allow_html=True,
)