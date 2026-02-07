import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. PAGE CONFIG
st.set_page_config(page_title="NEXUS // CONNECT", page_icon="🤝", layout="wide")

# 2. PRISM DARK CSS (Black Font Buttons + Pill Toggle)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, label { color: #f0f6fc !important; font-family: 'Inter', sans-serif; font-weight: 800 !important; }
    p, .stMarkdown { color: #8b949e !important; }

    /* Buttons with Black Font for Hackathon Readability */
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #bc8cff 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }

    /* Modern Blue Pill Toggle */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 34px !important; width: 65px !important;
        background-color: #21262d !important; border-radius: 20px !important;
        border: 2px solid #30363d !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #00f2fe !important;
    }

    .prism-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px; padding: 25px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'linked_peer' not in st.session_state: st.session_state.linked_peer = None

# --- PAGE 1: GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 NEXUS GATEWAY")
    is_free = st.checkbox("SIGNAL AVAILABILITY", key="gate_toggle")
    if is_free:
        st.markdown("<h1 style='color:#00f2fe !important; font-size: 60px;'>I AM FREE</h1>", unsafe_allow_html=True)
        if st.button("PROCEED TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB (WITH MESSAGING LOGIC) ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("id"):
            sid = st.text_input("ROLL NUMBER")
            name = st.text_input("NICKNAME")
            if st.form_submit_button("CONNECT"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🪐 HUB // {user['name'].upper()}")

    # 4. DATA SYNC & INCOMING MESSAGE CHECK
    try:
        all_data = conn.read(ttl=0)
        
        # Check if anyone has messaged the current user
        # We look for rows where "linked_with" matches the current user's ID
        messages = all_data[all_data['linked_with'] == user['id']]
        if not messages.empty:
            partner_name = messages.iloc[0]['name']
            st.toast(f"📩 CONNECTION REQUEST FROM {partner_name.upper()}!")
            st.info(f"Notification: {partner_name} wants to link at the Computer Centre.")

        # Display Venues (Timetable Logic)
        st.write("### 📍 Empty Venues & Activities")
        c1, c2 = st.columns(2)
        with c1: st.markdown('<div class="prism-card"><b>Computer Centre</b><br>Activity: Project Work</div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="prism-card"><b>Lecture Hall 1</b><br>Activity: Study Group</div>', unsafe_allow_html=True)

        # KNN Peer Matching
        st.divider()
        st.write("### 🤖 AI-MATCHED PEERS")
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        for _, p in peers.iterrows():
            with st.container():
                st.markdown(f'<div class="prism-card">👤 {p["name"]}</div>', unsafe_allow_html=True)
                # SEND MESSAGE ACTION
                if st.button(f"⚡ LINK WITH {p['name'].split()[0]}", key=p['student_id']):
                    # Update the Google Sheet to set the message/link target
                    all_data.loc[all_data['student_id'] == user['id'], 'linked_with'] = p['student_id']
                    conn.update(data=all_data)
                    st.session_state.linked_peer = p['name']
                    st.session_state.page = 'success'
                    st.rerun()

    except Exception as e: st.error(f"Sync Error: {e}")

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; border: 2px solid #00f2fe; padding: 40px; border-radius: 20px;">
            <h1 style="color:#00f2fe !important;">🚀 MESSAGE SENT!</h1>
            <h2>Uplink request transmitted to {st.session_state.linked_peer.upper()}</h2>
            <p>They will receive a notification on their dashboard immediately.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("RETURN TO HUB"):
        st.session_state.page = 'hub'
        st.rerun()