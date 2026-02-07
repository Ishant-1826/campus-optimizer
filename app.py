import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from datetime import datetime

# 1. UI CONFIGURATION
st.set_page_config(page_title="NEXUS // AI-LINK", page_icon="🔗", layout="wide")

# 2. PRISM DARK CSS (Black Font + High Contrast)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #0d1117; }
    h1, h2, h3, label { font-family: 'Inter', sans-serif !important; color: #f0f6fc !important; font-weight: 800 !important; }
    
    /* PRISM BUTTONS: Black Font for Hackathon Visibility */
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #bc8cff 100%) !important;
        color: #000000 !important; font-weight: 800 !important;
        text-transform: uppercase; border: none !important; border-radius: 10px !important;
    }

    /* BLUE PILL TOGGLE */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 38px !important; width: 75px !important;
        background-color: #21262d !important; border-radius: 40px !important;
        border: 2px solid #30363d !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #00f2fe !important;
    }
    .prism-card { background: rgba(22, 27, 34, 0.6); border: 1px solid rgba(48, 54, 61, 0.8); border-radius: 16px; padding: 25px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: GATEWAY (Sign-In) ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 NEXUS GATEWAY")
    is_free = st.checkbox("SIGNAL AVAILABILITY", key="gate_toggle")
    if is_free:
        st.markdown("<h1 style='color:#00f2fe !important; font-size: 60px;'>I AM FREE</h1>", unsafe_allow_html=True)
        if st.button("PROCEED TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB (Active-Only Logic) ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("identity"):
            sid = st.text_input("ROLL NUMBER")
            name = st.text_input("NICKNAME")
            if st.form_submit_button("CONNECT"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🪐 HUB // {user['name'].upper()}")

    # 4. DATA SYNC & CLEAN FILTERING
    try:
        all_data = conn.read(ttl=0)
        
        # TIMETABLE / RESOURCE SUGGESTIONS
        st.write("### 📍 Empty Venues & Suggestions")
        v1, v2 = st.columns(2)
        with v1: st.markdown('<div class="prism-card"><h3>Computer Centre</h3><p>Status: <b>Empty</b><br>Activity: Project Work</p></div>', unsafe_allow_html=True)
        with v2: st.markdown('<div class="prism-card"><h3>Lecture Hall 3</h3><p>Status: <b>No Class</b><br>Activity: Study Group</p></div>', unsafe_allow_html=True)

        # Update current user to Active in DB
        new_row = pd.DataFrame([{"student_id": user["id"], "name": user["name"], "is_active": True, "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}])
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        # THE FILTER: Only show users where is_active is True
        active_peers = all_data[(all_data['is_active'] == True) & (all_data['student_id'] != user['id'])]
        
        st.divider()
        st.write("### 🤖 ACTIVE PEER NODES")
        if not active_peers.empty:
            for _, p in active_peers.iterrows():
                with st.container():
                    st.markdown(f'<div class="prism-card">👤 {p["name"]}</div>', unsafe_allow_html=True)
                    if st.button(f"⚡ LINK WITH {p['name'].split()[0]}", key=p['student_id']):
                        st.session_state.linked_peer = p['name']
                        st.session_state.page = 'success'
                        st.rerun()
        else:
            st.info("No other active nodes found. Ensure your friend has clicked 'I AM FREE'.")

    except Exception as e:
        st.error(f"Sync Error: {e}")

    # LOGOUT: This is what removes the name from the list!
    if st.sidebar.button("🚪 GO OFFLINE"):
        try:
            df = conn.read(ttl=0)
            df.loc[df['student_id'] == user['id'], 'is_active'] = False
            conn.update(data=df)
            st.session_state.clear()
            st.rerun()
        except: st.error("Sign-out failed.")

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown(f"""
        <div style="text-align: center; border: 2px solid #00f2fe; padding: 50px; border-radius: 30px;">
            <h1 style="color:#00f2fe !important;">🚀 LINKED!</h1>
            <h2>Handshake with {st.session_state.linked_peer.upper()}</h2>
            <p>Venue: <b>Computer Centre</b> | Activity: <b>Project Work</b></p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("RETURN TO HUB"):
        st.session_state.page = 'hub'
        st.rerun()