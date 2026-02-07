import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. THEME MANAGEMENT
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# 2. SAAS UI CONFIGURATION
st.set_page_config(page_title="NEXUS // CORE", page_icon="🌐", layout="wide")

# 3. DYNAMIC CSS (Light/Dark Mode)
t = {
    'bg': '#ffffff' if st.session_state.theme == 'light' else '#050508',
    'card': '#f8f9fa' if st.session_state.theme == 'light' else 'rgba(255, 255, 255, 0.03)',
    'text': '#1a1a1a' if st.session_state.theme == 'light' else '#f0f6fc',
    'accent': '#0070f3' if st.session_state.theme == 'light' else '#00f2fe',
    'border': '#eaeaea' if st.session_state.theme == 'light' else 'rgba(255, 255, 255, 0.1)'
}

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {{ background-color: {t['bg']}; transition: 0.3s; }}
    
    h1, h2, h3, p, label, .stMarkdown {{ 
        color: {t['text']} !important; 
        font-family: 'Inter', sans-serif !important; 
    }}

    /* Professional SaaS "Pill" Toggle */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {{
        height: 34px !important; width: 64px !important;
        background-color: #e2e8f0 !important; border-radius: 20px !important;
        border: 2px solid {t['accent']} !important;
    }}
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {{
        background-color: {t['accent']} !important;
    }}

    /* SaaS Component Cards */
    .saas-card {{
        background: {t['card']};
        border: 1px solid {t['border']};
        padding: 24px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }}
    
    .stButton>button {{
        background-color: {t['accent']} !important;
        color: white !important; border-radius: 8px !important;
        width: 100%; border: none !important; padding: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# 5. NAVIGATION & TOP BAR
if 'page' not in st.session_state:
    st.session_state.page = 'gate'

with st.container():
    c1, c2 = st.columns([8, 2])
    with c2:
        st.button("🌓 Toggle Theme", on_click=toggle_theme)

# --- PAGE 1: ENTERPRISE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write(f"# 🛰️ NEXUS // {'SYSTEM' if st.session_state.theme == 'light' else 'NOVA'}")
    st.write("Professional Peer Network for IIIT Kota")
    
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown(f'<div class="saas-card">', unsafe_allow_html=True)
        is_free = st.checkbox("Signify Availability", key="saas_toggle")
        if is_free:
            st.write("### STATUS: I AM FREE")
            if st.button("Access Dashboard"):
                st.session_state.page = 'hub'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE 2: SAAS DASHBOARD ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        st.write("## Identity Verification")
        with st.form("verify"):
            sid = st.text_input("Student ID")
            name = st.text_input("Name")
            if st.form_submit_button("Verify Node"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"## Welcome back, {user['name']}")
    
    # Matching Logic
    try:
        all_data = conn.read(ttl=0)
        all_data['interests'] = all_data['interests'].fillna("")
        
        st.write("### Recommended Peer Matches")
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        grid = st.columns(2)
        for i, (_, p) in enumerate(peers.iterrows()):
            with grid[i % 2]:
                st.markdown(f"""
                <div class="saas-card">
                    <p style="font-size: 0.8em; color: {t['accent']};">PEER NODE</p>
                    <h3 style="margin:0;">{p['name']}</h3>
                    <p>Study Areas: {p['interests']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"Connect with {p['name'].split()[0]}", key=p['student_id'])
    except Exception as e:
        st.error(f"Uplink Failure: {e}")

    if st.sidebar.button("Sign Out"):
        st.session_state.page = 'gate'
        st.rerun()