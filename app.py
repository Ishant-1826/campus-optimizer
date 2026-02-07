import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
import time
from datetime import datetime

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="AI-LINK // SECTION-A", page_icon="決", layout="wide")

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
    h1, h2, h3 { font-family: 'Courier New', monospace; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'hub'
if 'offline_mode' not in st.session_state:
    st.session_state.offline_mode = False

# --- UTILITY FUNCTIONS ---
def get_current_day():
    return datetime.now().strftime("%a").upper()

# --- SIDEBAR DIAGNOSTICS ---
with st.sidebar:
    st.markdown("## 識 SYSTEM CONTROL")
    st.session_state.offline_mode = st.toggle("OFFLINE MODE (Bluetooth)", value=st.session_state.offline_mode)
    
    if st.session_state.offline_mode:
        st.warning("決 BLUETOOTH MESH ACTIVE\nData syncing locally.")
    else:
        st.success("決 SATELLITE LINK ACTIVE\nConnected to GSheets.")
    
    st.markdown("---")
    if st.button("MAIN HUB"): st.session_state.page = 'hub'
    if st.button("TIMETABLE"): st.session_state.page = 'timetable'

# --- PAGE 1: HUB (AI-LINK) ---
if st.session_state.page == 'hub':
    st.markdown("<h1>AI-LINK // <span style='color:#00f2fe;'>PROXIMITY NODES</span></h1>", unsafe_allow_html=True)
    
    if not st.session_state.offline_mode:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read()
            st.dataframe(df, use_container_width=True)
        except Exception:
            st.error("Connection Lost. Please switch to Offline Mode.")
    else:
        st.info("Scanning for nearby Bluetooth nodes in Section-A...")
        st.progress(65, text="Searching 2.4GHz spectrum...")
        # Placeholder for local discovery logic
        st.markdown("""
        <div class='node-card'>
            <p style='color:#8b949e;'>[BLUETOOTH VIRTUAL TERMINAL]</p>
            <code> > Peer detected: Node_ID_2488 (Dist: 2.4m)</code><br>
            <code> > Peer detected: Node_ID_1092 (Dist: 5.1m)</code>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 2: TIMETABLE PROTOCOL ---
elif st.session_state.page == 'timetable':
    current_day = get_current_day()
    st.markdown(f"<h1>IIIT KOTA // <span style='color:#00f2fe;'>SECTION-A SCHEDULE</span></h1>", unsafe_allow_html=True)
    
    # Timetable Data from your PDF
    tt_data = {
        "MON": ["09:00 - FDE (L)", "10:00 - DSA (L)", "11:00 - DSA (L)", "14:00 - DM (T)"],
        "TUE": ["09:00 - DM (L)", "10:00 - DLD (L)", "11:00 - DLD (L)", "15:00 - DM (T)"],
        "WED": ["09:00 - DLD (L)", "10:00 - DSA (L)", "11:00 - DSA (L)", "14:00 - MNGT (L)"],
        "THU": ["09:00 - DM (L)", "10:00 - FDE (L)", "11:00 - MNGT (L)", "15:00 - TW-LAB"],
        "FRI": ["10:00 - DSA-LAB", "11:00 - DSA-LAB", "14:00 - PY-LAB", "15:00 - PY-LAB"]
    }

    cols = st.columns(5)
    days = list(tt_data.keys())
    
    for i, col in enumerate(cols):
        day = days[i]
        is_today = (day == current_day)
        border_color = "#00f2fe" if is_today else "rgba(0, 242, 254, 0.2)"
        bg_alpha = "0.1" if is_today else "0.05"
        
        with col:
            st.markdown(f"""
                <div style='background: rgba(0, 242, 254, {bg_alpha}); border: 2px solid {border_color}; 
                padding: 12px; border-radius: 8px; text-align: center;'>
                    <strong style='color:{border_color};'>{"焚 " if is_today else ""}{day}</strong>
                </div>
            """, unsafe_allow_html=True)
            for slot in tt_data.get(day, ["OFF"]):
                st.caption(f"敵 {slot}")

    st.write("---")
    
    # Offline Info
    if st.session_state.offline_mode:
        st.caption("決 Schedule loaded from local cache. Bluetooth sync enabled for peer status.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class='node-card' style='border-left: 4px solid #00f2fe;'>
                <h4 style='color:#00f2fe;'>CORE SUBJECTS</h4>
                <p style='font-size: 0.85rem; color: #8b949e;'>
                    <b>CST102:</b> Data Structures & Algos<br>
                    <b>MAT102:</b> Discrete Mathematics<br>
                    <b>ECT102:</b> Digital Logic Design
                </p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='node-card' style='border-left: 4px solid #bc8cff;'>
                <h4 style='color:#bc8cff;'>LOCATION DATA</h4>
                <p style='font-size: 0.85rem; color: #8b949e;'>
                    <b>Lecture Hall:</b> Refer to IIITK Notice<br>
                    <b>Labs:</b> Computer Center 1 & 2<br>
                    <b>Tutorials:</b> Assigned Tutorial Rooms
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("AI-LINK V2.0 // DEVELOPED FOR IIIT KOTA SECTION-A // 2026")