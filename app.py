import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED PAGE CONFIG
st.set_page_config(page_title="NEXUS // HYPER-CORE", page_icon="⚡", layout="wide")

# 2. CYBER-MODERN CSS
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #0d1117 0%, #050508 100%); }
    
    /* Neon Text Effects */
    h1, h2, h3 { 
        font-family: 'Orbitron', sans-serif;
        color: #00f2fe !important;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.5);
    }

    /* MASSIVE CUSTOM TOGGLE */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 45px !important;
        width: 85px !important;
        background-color: #1a1a2e !important;
        border: 2px solid #ff4b4b !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #00f2fe !important;
        border: 2px solid #00f2fe !important;
    }

    /* GLASSMORPHISM PEER CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 25px;
        padding: 30px;
        margin-bottom: 25px;
        transition: 0.4s;
    }
    .glass-card:hover {
        border-color: #00f2fe;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.2);
        transform: scale(1.02);
    }
    
    /* Custom Profile Details */
    .detail-tag {
        background: rgba(0, 242, 254, 0.1);
        color: #00f2fe;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.85em;
        margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNECTION & DATA UTILS
conn = st.connection("gsheets", type=GSheetsConnection)
all_possible_interests = ["Python", "DSA", "ML", "Linear Algebra", "Digital Electronics", "Math", "Signal Processing"]

def encode_interests(interest_list):
    return [1 if i in interest_list else 0 for i in all_possible_interests]

# --- SESSION & NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: HYPER-GATE (I AM FREE) ---
if st.session_state.page == 'gate':
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("⚡ NEXUS GATEWAY")
        st.write("### ACTIVATE YOUR NODE TO COMMENCE")
        
        # GIANT TOGGLE
        is_free = st.checkbox("Toggle to Signal Availability", key="free_gate")
        
        if is_free:
            st.markdown("<h1 style='color:#00f2fe; font-size: 60px;'>I AM FREE</h1>", unsafe_allow_html=True)
            if st.button("PROCEED TO CORE HUB"):
                with st.status("Initializing Neural Matching...", expanded=True) as s:
                    time.sleep(1)
                    s.update(label="Uplink Established", state="complete")
                st.session_state.page = 'dashboard'
                st.rerun()

# --- PAGE 2: CORE HUB (DASHBOARD) ---
elif st.session_state.page == 'dashboard':
    if 'user' not in st.session_state:
        st.title("🆔 REGISTER IDENTITY")
        with st.container(border=True):
            sid = st.text_input("NODE ID (Roll No)")
            name = st.text_input("NICKNAME/NAME")
            if st.button("SYNC IDENTITY"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.title(f"🛰️ HUB // {user['name'].upper()}")
    
    # Dashboard Controls
    with st.sidebar:
        st.write("### NODE CONFIG")
        my_focus = st.multiselect("YOUR FOCUS VECTORS:", all_possible_interests, default=["Python"])
        if st.button("DISCONNECT NODE"):
            st.session_state.page = 'gate'
            st.rerun()

    # SYNC & KNN MATCHING
    try:
        # Save to Google Sheets
        user_vector = encode_interests(my_focus)
        new_row = pd.DataFrame([{"student_id": user["id"], "name": user["name"], "interests": ",".join(my_focus), "is_active": True}])
        all_data = conn.read(ttl=0)
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        # KNN Computation
        active_peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        # --- UPDATED KNN ENGINE WITH DATA CLEANING ---
        if not active_peers.empty:
            # 1. Fill empty interest cells with an empty string to prevent 'float' errors
            active_peers['interests'] = active_peers['interests'].fillna("")
            
            # 2. Convert strings to vectors
            peer_vectors = [encode_interests(str(p).split(",")) for p in active_peers['interests']]
            
            # 3. Proceed with KNN Fit
            knn = NearestNeighbors(n_neighbors=min(len(peer_vectors), 4), metric='cosine')
            knn.fit(peer_vectors)
            distances, indices = knn.kneighbors([user_vector])
            
    # ... (Rest of your UI code) ...
        else:
            st.info("Scanning for compatible nodes in the IIIT Kota network...")

    except Exception as e:
        st.error(f"Hyper-Link Error: {e}")