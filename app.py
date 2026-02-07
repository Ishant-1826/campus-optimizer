import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import socket

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="AI-LINK // SECTION-A", page_icon="📡", layout="wide")

# Inject Cyber-Grid CSS
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e6edf3; }
    .stButton>button {
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        color: black; border: none; border-radius: 5px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #00f2fe; }
    .node-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        padding: 20px; border-radius: 10px;
        margin-bottom: 10px;
    }
    code { color: #00f2fe; background: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'hub'
if 'offline_mode' not in st.session_state:
    st.session_state.offline_mode = False

# --- SYSTEM UTILITIES ---
def get_local_id():
    # Generates a unique ID from your local machine name for offline discovery
    return socket.gethostname().upper()

def get_current_day():
    return datetime.now().strftime("%a").upper()

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.markdown("## 🛠 SYSTEM CONTROL")
    st.session_state.offline_mode = st.toggle("OFFLINE MODE (Bluetooth)", value=st.session_state.offline_mode)
    
    st.markdown("---")
    if st.button("📡 MAIN HUB"): st.session_state.page = 'hub'
    if st.button("📅 TIMETABLE"): st.session_state.page = 'timetable'
    
    st.markdown("---")
    st.markdown(f"**LOCAL NODE:** `{get_local_id()}`")
    st.caption("Status: Discoverable via Mesh")

# --- PAGE 1: HUB (AI-LINK) ---
if st.session_state.page == 'hub':
    st.markdown("<h1>AI-LINK // <span style='color:#00f2fe;'>PROXIMITY NODES</span></h1>", unsafe_allow_html=True)
    
    if not st.session_state.offline_mode:
        st.subheader("Global Spreadsheet Link")
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read()
            st.dataframe(df, use_container_width=True)
            st.info("Note: If your ID is missing from the sheet, use Offline Mode to broadcast locally.")
        except Exception:
            st.warning("Spreadsheet Unreachable. Switching to Local Discovery.")
            st.session_state.offline_mode = True
            st.rerun()
    
    if st.session_state.offline_mode:
        st.subheader("Local Bluetooth Mesh (Offline)")
        st.info(f"Broadcasting Node ID: {get_local_id()}")
        
        # Simulated Peer Discovery Logic
        peers = [
            {"Node": "SEC-A-ALPHA", "Signal": "Strong", "Activity": "In DSA Lab"},
            {"Node": "SEC-A-BRAVO", "Signal": "Weak", "Activity": "Idle"},
            {"Node": get_local_id(), "Signal": "Self", "Activity": "Broadcasting"}
        ]
        
        for peer in peers:
            color = "#00f2fe" if peer['Node'] == get_local_id() else "#8b949e"
            st.markdown(f"""
                <div class='node-card' style='border-left: 4px solid {color};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span style='color:{color}; font-weight:bold;'>{peer['Node']}</span>
                        <span style='font-size: 0.8rem;'>Signal: {peer['Signal']}</span>
                    </div>
                    <div style='color: #8b949e; font-size: 0.9rem;'>Status: {peer['Activity']}</div>
                </div>
            """, unsafe_allow_html=True)

# --- PAGE 2: TIMETABLE PROTOCOL ---
elif st.session_state.page == 'timetable':
    current_day = get_current_day()
    st.markdown("<h1>IIIT KOTA // <span style='color:#00f2fe;'>SECTION-A SCHEDULE</span></h1>", unsafe_allow_html=True)
    
    # Official Schedule Mapping from your PDF
    tt_data = {
        "MON": ["09:00 - FDE (L)", "10:00 - DSA (L)", "11:00 - DSA (L)", "14:00 - DM (T)"],
        "TUE": ["09:00 - DM (L)", "10:00 - DLD (L)", "11:00 - DLD (L)", "15:00 - DM (T)"],
        "WED": ["09:00 - DLD (L)", "10:00 - DSA (L)", "11:00 - DSA (L)", "14:00 - MNGT (L)"],
        "THU": ["09:00 - DM (L)", "10:00 - FDE (L)", "11:00 - MNGT (L)", "15:00 - TW-LAB"],
        "FRI": ["10:00 - DSA-LAB", "11:00 - DSA-LAB", "14:00 - PY-LAB", "15:00 - PY-LAB"]
    }

    cols = st.columns(5)
    days = ["MON", "TUE", "WED", "THU", "FRI"]
    
    for i, col in enumerate(cols):
        day = days[i]
        is_today = (day == current_day)
        border = "2px solid #00f2fe" if is_today else "1px solid rgba(0, 242, 254, 0.2)"
        
        with col:
            st.markdown(f"""
                <div style='background: rgba(0, 242, 254, 0.05); border: {border}; 
                padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;'>
                    <strong style='color:#00f2fe;'>{day}</strong>
                </div>
            """, unsafe_allow_html=True)
            for slot in tt_data.get(day, []):
                st.caption(f"🕒 {slot}")

    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div class='node-card' style='border-left: 4px solid #00f2fe;'>
                <h4 style='color:#00f2fe;'>COURSE CODES</h4>
                <p style='font-size: 0.8rem;'>
                    <b>FDE:</b> Foundations of Data Engineering<br>
                    <b>DSA:</b> Data Structures & Algorithms<br>
                    <b>DM:</b> Discrete Mathematics<br>
                    <b>DLD:</b> Digital Logic Design
                </p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class='node-card' style='border-left: 4px solid #bc8cff;'>
                <h4 style='color:#bc8cff;'>LAB LOCATIONS</h4>
                <p style='font-size: 0.8rem;'>
                    <b>DSA & Python:</b> Computer Center (CC)<br>
                    <b>TW-LAB:</b> Technical Writing Center<br>
                    <b>Tutorials:</b> Check LH-1/LH-2
                </p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("BACK TO HUB"):
        st.session_state.page = 'hub'
        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("SYSTEM: ONLINE // ENCRYPTION: ACTIVE // SECTION-A PROTOCOL")