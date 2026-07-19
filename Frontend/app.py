import streamlit as st

from components.header import render_header
from components.mascot import render_walking_cow
from components.saved_panel import render_saved_panel
from components.sidebar import render_sidebar
from utils import api_client
from utils.icons import icon

st.set_page_config(page_title="vet.ai — পশু সেবা AI", page_icon="🐄", layout="wide")

INK = "#0B2545"
MUTED = "#5B6B7B"
TEAL = "#14B8A6"
TEAL_TINT = "rgba(20, 184, 166, 0.10)"
BG = "#F4F7FA"

# -----------------------------
# Session state
# -----------------------------
_DEFAULTS = {
    "token": None,
    "phone_number": None,
    "display_name": None,
    "nav_page": "home",
    "chat_response": None,
    "response_saved": False,
    "audio_version": 0,
}
for _key, _value in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value


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


@st.dialog("প্রোফাইল ও খামার আপডেট")
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
                    <img src="{avatar_url}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid white; box-shadow: 0 4px 12px rgba(11, 37, 69, 0.15);" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="display: flex; justify-content: center; margin-bottom: 0.8rem;">
                    <div style="display: flex; align-items: center; justify-content: center; width: 140px; height: 140px; border-radius: 50%; background-color: #E2E8F0; color: #718096; font-size: 3rem; font-weight: 700; border: 3px solid white; box-shadow: 0 4px 12px rgba(11, 37, 69, 0.15);">
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
            """<p style="text-align: center; color: #64748B; font-size: 0.78rem; margin-top: 0.4rem; line-height: 1.2;">
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
        name = st.text_input("নাম", value=profile.get("name") or "", placeholder="আপনার নাম লিখুন")
        address = st.text_input("ঠিকানা", value=profile.get("address") or "", placeholder="আপনার ঠিকানা লিখুন")
        email = st.text_input("ইমেইল (ঐচ্ছিক)", value=profile.get("email") or "", placeholder="আপনার ইমেইল লিখুন")

        st.markdown("### খামারের তথ্য (ফসল ও পশুর বিবরণ)")

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

    [data-testid="stAppViewContainer"] {{ background: {BG}; }}

    /* ---- Redesigned Profile Dialog Modals ---- */
    div[data-testid="stDialog"] div[role="dialog"],
    div[data-testid="stDialog"] div[class*="stDialog"],
    div[role="dialog"] {{
        max-width: 880px !important;
        width: 880px !important;
    }}

    div[class*="st-key-profile_save_btn"] button {{
        background-color: #14B8A6 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-profile_save_btn"] button:hover {{
        background-color: #0D9488 !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3) !important;
    }}

    div[class*="st-key-profile_delete_btn"] button {{
        background-color: transparent !important;
        color: #EF4444 !important;
        border: 1px solid #EF4444 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-profile_delete_btn"] button:hover {{
        background-color: #EF4444 !important;
        color: white !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }}

    div[class*="st-key-confirm_delete_btn"] button {{
        background-color: #EF4444 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-confirm_delete_btn"] button:hover {{
        background-color: #DC2626 !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }}

    div[class*="st-key-cancel_delete_btn"] button {{
        background-color: #E2E8F0 !important;
        color: #475569 !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[class*="st-key-cancel_delete_btn"] button:hover {{
        background-color: #CBD5E1 !important;
        transform: scale(1.02) !important;
    }}

    div[class*="st-key-profile_pic_uploader"] {{
        max-width: 100% !important;
    }}
    div[class*="st-key-profile_pic_uploader"] section {{
        padding: 0.5rem !important;
        background-color: #F8FAFC !important;
        border-radius: 8px !important;
        border: 1px dashed #CBD5E1 !important;
    }}
    div[class*="st-key-profile_pic_uploader"] label {{
        display: none !important;
    }}

    /* Light pastel input styling for Profile Dialog inputs */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input {{
        background-color: #F0FDFA !important;
        border: 1px solid #CCFBF1 !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.8rem !important;
        color: #0F766E !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stTextInput"] input:focus, 
    div[data-testid="stNumberInput"] input:focus {{
        background-color: #FFFFFF !important;
        border-color: #14B8A6 !important;
        color: #0F2942 !important;
        box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.15) !important;
    }}

    #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}

    .block-container {{ padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1360px; }}


    h1, h2, h3 {{ color: {INK}; font-weight: 700; letter-spacing: -0.01em; }}

    ::selection {{ background: rgba(20, 184, 166, 0.25); }}

    .stButton > button {{ border-radius: 12px; font-weight: 600; transition: all 0.18s ease; box-shadow: none; }}
    .stButton > button:hover {{ transform: translateY(-1px); }}
    .stButton > button:active {{ transform: translateY(0); }}

    /* ---- Header ---- */
    div.st-key-app_header {{
        background: #FFFFFF; border-radius: 18px; padding: 0.8rem 1.4rem; margin-bottom: 1.8rem;
        box-shadow: 0 2px 16px rgba(11, 37, 69, 0.05); border: 1px solid rgba(11, 37, 69, 0.04);
    }}
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
        background: linear-gradient(135deg, #14B8A6, #0D9488); border: none; border-radius: 999px;
        box-shadow: 0 6px 16px rgba(20, 184, 166, 0.32);
    }}
    div.st-key-header_login button:hover {{ box-shadow: 0 8px 20px rgba(20, 184, 166, 0.42); }}

    /* ---- Sidebar nav pills ---- */
    div.st-key-sidebar_nav .stButton > button {{
        background: transparent; border: none; text-align: left; justify-content: flex-start;
        color: {MUTED}; font-weight: 500; padding: 0.6rem 0.9rem; border-radius: 11px;
    }}
    div.st-key-sidebar_nav .stButton > button:hover {{ background: {TEAL_TINT}; color: {TEAL}; transform: none; }}
    div.st-key-sidebar_nav button[kind="primary"] {{
        background: {TEAL_TINT}; color: {TEAL}; font-weight: 700; box-shadow: none;
        border-left: 3px solid {TEAL};
    }}

    /* ---- Cards ---- */
    div.st-key-reminder_card, div.st-key-saved_panel, div.st-key-card_image, div.st-key-card_audio,
    div.st-key-response_card {{
        background: #FFFFFF; border-radius: 18px; padding: 1.35rem 1.25rem;
        box-shadow: 0 2px 16px rgba(11, 37, 69, 0.055); border: 1px solid rgba(11, 37, 69, 0.045);
    }}
    div.st-key-card_image, div.st-key-card_audio {{
        text-align: center; transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}
    div.st-key-card_image:hover, div.st-key-card_audio:hover {{
        box-shadow: 0 8px 24px rgba(11, 37, 69, 0.09); transform: translateY(-2px);
    }}
    div.st-key-saved_locked {{ background: #FAFBFC; border-radius: 14px; padding: 1rem 1rem 1.4rem; margin-top: 0.4rem; }}

    .upload-icon-circle {{
        width: 54px; height: 54px; border-radius: 50%; background: {TEAL_TINT};
        display: flex; align-items: center; justify-content: center; margin: 0 auto 0.65rem;
    }}
    .upload-card-title {{ font-weight: 700; color: {INK}; margin-bottom: 0.2rem; }}
    .upload-card-sub {{ color: {MUTED}; font-size: 0.82rem; margin-bottom: 0.8rem; }}

    .section-divider {{
        background: {TEAL_TINT}; color: {TEAL}; text-align: center; padding: 0.7rem;
        border-radius: 11px; font-weight: 700; margin: 1.4rem 0 1.2rem; letter-spacing: 0.01em;
    }}
    .or-divider {{
        display: flex; align-items: center; gap: 0.9rem; color: {MUTED}; font-size: 0.88rem; margin: 1.6rem 0 1.1rem;
    }}
    .or-divider::before, .or-divider::after {{ content: ""; flex: 1; height: 1px; background: rgba(11,37,69,0.1); }}

    .info-bar {{
        display: flex; align-items: center; justify-content: center; gap: 0.5rem;
        color: {MUTED}; font-size: 0.84rem; margin-top: 1.5rem;
    }}

    /* ---- Ask form controls ---- */
    div.st-key-ask_submit button {{
        background: linear-gradient(135deg, #14B8A6, #0D9488); border: none; border-radius: 999px;
        box-shadow: 0 6px 16px rgba(20, 184, 166, 0.32);
    }}
    div.st-key-ask_submit button:hover {{ box-shadow: 0 8px 20px rgba(20, 184, 166, 0.42); }}
    div.st-key-quick_image_hint button, div.st-key-quick_audio_hint button {{
        background: {BG}; border: 1px solid rgba(11, 37, 69, 0.08); border-radius: 50%;
        width: 42px; height: 42px; padding: 0;
    }}
    div.st-key-quick_image_hint button:hover, div.st-key-quick_audio_hint button:hover {{
        background: {TEAL_TINT}; border-color: {TEAL};
    }}
    div.st-key-save_response_btn button {{ border-radius: 999px; }}
    div.st-key-remove_audio_btn button {{
        background: transparent; border: none; color: #C0392B; font-weight: 500;
        font-size: 0.82rem; padding: 0.3rem; margin-top: 0.3rem; box-shadow: none;
    }}
    div.st-key-remove_audio_btn button:hover {{ background: rgba(192, 57, 43, 0.08); transform: none; }}
    .stTextArea textarea {{ border-radius: 14px; }}
    [data-testid="stFileUploaderDropzone"] {{ border-radius: 12px; }}

    /* ---- Saved response items ---- */
    div[class*="st-key-saved_item_"] {{
        border-radius: 12px !important; margin-bottom: 0.6rem !important; padding: 0.85rem !important;
        transition: box-shadow 0.15s ease;
    }}
    div[class*="st-key-saved_item_"]:hover {{ box-shadow: 0 3px 12px rgba(11, 37, 69, 0.08); }}

    /* ---- Footer ---- */
    .app-footer {{ color: {MUTED}; }}
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
render_header(on_open_login=open_login_dialog, on_open_profile=open_profile_dialog)

if st.session_state.get("show_profile_dialog"):
    st.session_state.show_profile_dialog = False
    open_profile_dialog()

render_walking_cow()

# -----------------------------
# Body layout
# -----------------------------
nav_page = st.session_state.nav_page
sidebar_col, main_col, saved_col = st.columns([1.05, 3.0, 1.15], gap="large")

with sidebar_col:
    render_sidebar()

with main_col:
    if nav_page == "home":
        leaf = icon("leaf", color=TEAL, size=22)
        st.markdown(
            f"""
            <div style="text-align:center;margin-bottom:0.6rem;">
                <h1 style="margin-bottom:0.2rem;line-height:1.3;">
                    {leaf}&nbsp;পশু সেবা AI এ<br/>
                    <span style="color:{TEAL};">আপনাকে স্বাগতম</span>&nbsp;{leaf}
                </h1>
                <p style="color:{MUTED};font-size:1.02rem;">
                    আপনার পশুর সমস্যা লিখুন, ছবি দিন বা কথা বলুন — আমাদের AI সহকারী দ্রুত পরামর্শ দেবে।
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-divider">লিখিত তথ্য দিন</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="or-divider">অথবা লিখিতভাবে জানান</div>', unsafe_allow_html=True)

        st.text_area(
            "প্রশ্ন",
            placeholder="এখানে আপনার প্রশ্ন লিখুন...",
            key="ask_text",
            height=130,
            label_visibility="collapsed",
        )

        icon_col1, icon_col2, _spacer_col, submit_col = st.columns([0.7, 0.7, 4.2, 1.8])
        with icon_col1:
            if st.button(" ", key="quick_image_hint", icon=":material/photo_camera:", help="ছবি যোগ করুন"):
                st.toast("উপরের 'ছবি যোগ করুন' কার্ড ব্যবহার করুন।", icon="📷")
        with icon_col2:
            if st.button(" ", key="quick_audio_hint", icon=":material/mic:", help="অডিও রেকর্ড করুন"):
                st.toast("উপরের 'অডিও রেকর্ড করুন' কার্ড ব্যবহার করুন।", icon="🎙️")
        with submit_col:
            submitted = st.button(
                "জমা দিন", key="ask_submit", icon=":material/send:", type="primary", use_container_width=True
            )

        st.markdown(
            f'<div class="info-bar">{icon("info", color=MUTED, size=15)} আরেকটি মনে রাখবেন যে AI ভুল করতে পারে</div>',
            unsafe_allow_html=True,
        )

        if submitted:
            text_val = (st.session_state.get("ask_text") or "").strip()
            images_val = st.session_state.get("ask_images") or []
            audio_val = st.session_state.get(f"ask_audio_{st.session_state.audio_version}")
            try:
                with st.spinner("AI উত্তর তৈরি করছে..."):
                    response_text = api_client.generate(text_val, images_val, audio_val)
                st.session_state.chat_response = response_text
                st.session_state.response_saved = False
            except api_client.ApiError as exc:
                st.session_state.chat_response = None
                st.error(exc.message)

        if st.session_state.get("chat_response"):
            st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
            with st.container(key="response_card", border=True):
                st.markdown(
                    f"<p style='font-weight:700;color:{INK};margin-bottom:0.6rem;'>AI-এর পরামর্শ</p>",
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
                            api_client.save_response(token, st.session_state.chat_response)
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
                <li>"নতুন প্রশ্ন করুন" পাতায় পশুর সমস্যা লিখুন, ছবি দিন অথবা অডিও রেকর্ড করুন।</li>
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

with saved_col:
    if nav_page == "home":
        render_saved_panel(open_login_dialog, compact=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
footer_links_col, footer_version_col = st.columns([5, 1])
with footer_links_col:
    st.markdown(
        f"""<p style="text-align:center;color:{MUTED};font-size:0.85rem;">
        গোপনীয়তা নীতি&nbsp;&nbsp;|&nbsp;&nbsp;শর্তাবলী&nbsp;&nbsp;|&nbsp;&nbsp;যোগাযোগ করুন
        </p>""",
        unsafe_allow_html=True,
    )
with footer_version_col:
    st.markdown(f"<p style='color:{MUTED};font-size:0.85rem;text-align:right;'>v1.0.0</p>", unsafe_allow_html=True)
