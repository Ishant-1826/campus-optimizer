import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED PAGE CONFIG
st.set_page_config(page_title="NEXUS // NOVA", page_icon="🌌", layout="wide")

# 2. ULTRA-MODERN CSS: ANIMATED BACKGROUND & PILL TOGGLE
st.markdown("""
    <style>
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #050508, #0a0a2e, #001f3f, #050508);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* High-Contrast Neon Text */
    h1, h2, h3, p, label, span, .stMarkdown { 
        color: #00f2fe !important; 
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
    }

    /* THE PILL TOGGLE (Large & Blue) */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 50px !important; width: 100px !important;
        background-color: #1a1a1a !important; border-radius: 50px !important;
        border: 3px solid #4facfe !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #4facfe !important;
        box-shadow: 0 0 20px #4facfe;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 30px;
        padding: 40px;
        margin-bottom: 25px;
        transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .glass-card:hover {
        transform: scale(1.03);
        border-color: #00f2fe;
        box-shadow: 0 0 40px rgba(0, 242, 254, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION & STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'entrance'

# --- PAGE 1: ENTRANCE GATEWAY ---
if st.session_state.page == 'entrance':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.write("# 🛰️ NEXUS // NOVA")
    st.write("### IIIT KOTA AI & DATA ENGINEERING")
    
    _, col, _ = st.columns([1, 1, 1])
    with col:
        is_free = st.checkbox("SIGNAL AVAILABILITY", key="nova_toggle")
        
    if is_free:
        st.markdown("<h1 style='color:#4facfe !important; font-size: 70px;'>I AM FREE</h1>", unsafe_allow_html=True)
        with st.status("Syncing Student Vectors...", expanded=True) as s:
            time.sleep(1.5)
            s.update(label="Handshake Successful", state="complete")
        st.session_state.page = 'hub'
        st.rerun()

# --- PAGE 2: THE HUB (DASHBOARD) ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        st.write("## 🆔 NODE INITIALIZATION")
        with st.container(border=True):
            sid = st.text_input("NODE ID")
            name = st.text_input("NICKNAME")
            if st.button("CONNECT TO HUB"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🪐 HUB // {user['name'].upper()}")

    # Interest Selection
    all_interests = ["Python", "DSA", "ML", "Linear Algebra", "Digital Electronics", "Math"]
    my_focus = st.multiselect("DEFINE FOCUS VECTORS:", all_interests, default=["Python"])

    # SYNC & KNN MATCHING
    try:
        new_row = pd.DataFrame([{
            "student_id": user["id"], "name": user["name"], 
            "interests": ",".join(my_focus), "is_active": True
        }])
        
        # Fresh Data Sync
        all_data = conn.read(ttl=0)
        all_data['interests'] = all_data['interests'].fillna("") # Fix 'float' error
        
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        # KNN Computation
        st.write("### 🤝 COMPATIBLE NEURAL NODES")
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        if not peers.empty:
            grid = st.columns(2)
            for i, (_, p) in enumerate(peers.iterrows()):
                # Only show common interest matches
                common = set(my_focus).intersection(set(p['interests'].split(',')))
                if common:
                    with grid[i % 2]:
                        st.markdown(f"""
                        <div class="glass-card">
                            <h2 style="margin:0;">👤 {p['name']}</h2>
                            <p style="margin-top:10px;">Common Focus: <b>{", ".join(common)}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.button(f"⚡ LINK WITH {p['name']}", key=p['student_id'])
        else:
            st.info("Searching for nodes with similar study vectors in the Kota network...")

    except Exception as e:
        st.error(f"Uplink Error: {e}")

    if st.sidebar.button("🚪 DISCONNECT"):
        st.session_state.page = 'entrance'
        st.rerun()