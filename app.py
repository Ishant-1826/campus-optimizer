import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED PAGE CONFIG
st.set_page_config(page_title="NEXUS // PRISM", page_icon="🎯", layout="wide")

# 2. THE "PRISM DARK" UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&display=swap');
    
    .stApp { background-color: #0d1117; }
    
    /* Typography Hierarchy */
    h1, h2, h3, label, .stMarkdown { 
        font-family: 'Inter', sans-serif !important; 
        color: #f0f6fc !important; 
    }
    .stMarkdown p { color: #8b949e !important; }

    /* THE PILL TOGGLE: Professional Blue */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 40px !important; width: 80px !important;
        background-color: #21262d !important; border-radius: 25px !important;
        border: 2px solid #30363d !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #0070f3 !important;
        border-color: #0070f3 !important;
        box-shadow: 0 0 15px rgba(0, 112, 243, 0.4);
    }

    /* Prism Peer Cards */
    .prism-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px; padding: 25px; margin-bottom: 20px;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .prism-card:hover {
        transform: translateY(-5px);
        border-color: #bc8cff; /* Soft Violet Accent */
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #0070f3 0%, #bc8cff 100%) !important;
        color: white !important; font-weight: 700 !important;
        border: none !important; border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 NEXUS // PRISM")
    st.write("### AI & DATA ENGINEERING STUDY NETWORK")
    
    _, col, _ = st.columns([1, 1, 1])
    with col:
        is_free = st.checkbox("Toggle to Signal Availability", key="gate_toggle")
        if is_free:
            st.markdown("<h1 style='color:#0070f3 !important;'>I AM FREE</h1>", unsafe_allow_html=True)
            if st.button("ENTER NEURAL HUB"):
                with st.status("Initializing Handshake...", expanded=True) as s:
                    time.sleep(1.2)
                    s.update(label="Uplink Verified", state="complete")
                st.session_state.page = 'hub'
                st.rerun()

# --- PAGE 2: THE NEURAL HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        st.write("## 🆔 INITIALIZE NODE")
        with st.container(border=True):
            sid = st.text_input("ROLL NUMBER", placeholder="e.g. 2025KUAD3005")
            name = st.text_input("FULL NAME", placeholder="Ishant Gupta")
            if st.button("CONNECT"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    
    # Header & Sign-Out (The Fix for the "Stuck" Peer issue)
    c1, c2 = st.columns([8, 2])
    with c1: st.write(f"# 🪐 HUB // {user['name'].upper()}")
    with c2: 
        if st.button("🔴 GO OFFLINE"):
            try:
                # Update status to False in Google Sheet
                df = conn.read(ttl=0)
                df.loc[df['student_id'] == user['id'], 'is_active'] = False
                conn.update(data=df)
                st.session_state.clear()
                st.rerun()
            except: st.error("Sign-out failed.")

    my_focus = st.multiselect("DEFINE FOCUS VECTORS:", 
                             ["Python", "DSA", "ML", "Math", "Linear Algebra", "Digital Electronics"], 
                             default=["Python"])

    # SYNC & KNN MATCHING
    try:
        new_row = pd.DataFrame([{"student_id": user["id"], "name": user["name"], "interests": ",".join(my_focus), "is_active": True}])
        all_data = conn.read(ttl=0)
        all_data['interests'] = all_data['interests'].fillna("")
        
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        st.divider()
        st.write("### 🤝 RECOMMENDED NODES (Common Interests)")
        
        # Filter: active only + not self
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        found = False
        grid = st.columns(2)
        for i, (_, p) in enumerate(peers.iterrows()):
            common = set(my_focus).intersection(set(p['interests'].split(',')))
            if common: # Matching Logic
                found = True
                with grid[i % 2]:
                    st.markdown(f"""
                    <div class="prism-card">
                        <p style="color:#bc8cff; font-size:0.8em; margin:0;">MATCH FOUND</p>
                        <h2 style="margin:5px 0;">👤 {p['name']}</h2>
                        <p>Focus: <b>{", ".join(common)}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button(f"⚡ LINK WITH {p['name'].split()[0]}", key=p['student_id'])
        
        if not found:
            st.info("Scanning... No matching active nodes found. Invite your team to toggle ON!")

    except Exception as e:
        st.error(f"Satellite Sync Error: {e}")