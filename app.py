import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from datetime import datetime
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED UI CONFIGURATION
st.set_page_config(page_title="NEXUS // SMART CAMPUS", page_icon="🏫", layout="wide")

# 2. PRISM DARK CSS (High-Contrast + SaaS Design)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, p, label { color: #f0f6fc !important; font-family: 'Inter', sans-serif; }
    
    /* PILL TOGGLE */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 40px !important; width: 80px !important;
        background-color: #21262d !important; border-radius: 40px !important;
        border: 2px solid #30363d !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #0070f3 !important;
    }

    .resource-card {
        background: rgba(0, 112, 243, 0.05);
        border: 1px solid rgba(0, 112, 243, 0.3);
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
    }
    .venue-badge {
        background: #238636; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DB CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION & STATE ---
if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 🛰️ NEXUS GATEWAY")
    is_free = st.checkbox("SIGNAL AVAILABILITY", key="gate_toggle")
    
    if is_free:
        st.markdown("<h1 style='color:#0070f3 !important;'>I AM FREE</h1>", unsafe_allow_html=True)
        if st.button("ACCESS SMART CAMPUS HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE RESOURCE HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        st.write("## 🆔 NODE INITIALIZATION")
        with st.form("id_form"):
            sid = st.text_input("ROLL NUMBER")
            name = st.text_input("NAME")
            if st.form_submit_button("CONNECT"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🪐 CAMPUS HUB // {user['name'].upper()}")

    # --- CAMPUS RESOURCE AVAILABILITY (Mock Timetable Data) ---
    st.divider()
    st.subheader("📍 Live Resource Availability")
    
    # In a real app, this would come from your Google Sheet
    venues = [
        {"name": "Computer Centre (Lab 1)", "status": "Empty", "capacity": "40 Seats", "suggested": "Project Work / ML Training"},
        {"name": "Lecture Hall 204", "status": "Empty", "capacity": "60 Seats", "suggested": "Study Group (Linear Algebra)"},
        {"name": "Central Library (Zone A)", "status": "Available", "capacity": "15 slots", "suggested": "Quiet Reading / DSA Prep"},
    ]

    cols = st.columns(3)
    for i, v in enumerate(venues):
        with cols[i]:
            st.markdown(f"""
            <div class="resource-card">
                <span class="venue-badge">{v['status']}</span>
                <h3>{v['name']}</h3>
                <p><b>Activity:</b> {v['suggested']}</p>
                <p style="font-size: 0.8em; color: #8b949e;">{v['capacity']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Book for {v['name'].split()[0]}", key=f"book_{i}"):
                st.toast(f"Slot reserved at {v['name']}!")

    # --- KNN PEER MATCHING ---
    st.divider()
    st.subheader("🤝 AI-Matched Peer Nodes")
    
    try:
        all_data = conn.read(ttl=0)
        all_data['interests'] = all_data['interests'].fillna("")
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        if not peers.empty:
            for _, p in peers.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{p['name']}**")
                    st.write(f"Focus: {p['interests']}")
                    if st.button(f"Link with {p['name']}", key=p['student_id']):
                        st.session_state.linked_peer = p['name']
                        st.session_state.page = 'success'
                        st.rerun()
        else:
            st.info("Searching for active peers...")
    except:
        st.error("Uplink failed.")

# --- PAGE 3: SUCCESS INTERFACE ---
elif st.session_state.page == 'success':
    st.success(f"## SUCCESS! Handshake with {st.session_state.linked_peer}")
    st.write("Your study session is now synchronized. Meet at the suggested venue!")
    if st.button("Return"):
        st.session_state.page = 'hub'
        st.rerun()