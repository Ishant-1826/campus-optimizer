import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED PAGE CONFIG
st.set_page_config(page_title="NEXUS // NOVA", page_icon="🌌", layout="wide")

# 2. ULTRA-MODERN CSS: ANIMATED BACKGROUND & PILL TOGGLE
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* 1. Refined Background: Deep Space Polish */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0d1117 0%, #050508 100%);
        background-attachment: fixed;
    }

    /* 2. Typography: Improved Hierarchy */
    h1, h2, h3, label, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: #f0f6fc !important; /* Soft white for readability */
        letter-spacing: -0.02em;
    }

    h1 { font-weight: 800 !important; font-size: 3.5rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-weight: 600 !important; color: #00f2fe !important; } /* Cyan for key headers */
    
    /* Reduced glow to prevent eye strain */
    .stMarkdown p { 
        color: #8b949e !important; 
        font-weight: 400 !important; 
        text-shadow: none !important;
        font-size: 1.1rem;
    }

    /* 3. The "Neural Switch" Toggle: Modern Pill Style */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 34px !important; 
        width: 65px !important;
        background-color: #21262d !important; 
        border-radius: 20px !important;
        border: 2px solid #30363d !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #00f2fe !important;
        border-color: #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
    }

    /* 4. Glassmorphism 2.0: Subtle Depth */
    .glass-card {
        background: rgba(22, 27, 34, 0.6) !important;
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .glass-card:hover {
        transform: translateY(-4px);
        border-color: #bc8cff; /* Soft Violet accent on hover */
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
    }

    /* 5. Buttons: Smooth Kinetic Feedback */
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #050508 !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.6) !important;
        transform: scale(1.02);
    }

    /* 6. Sidebar & Inputs Polish */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
    }

    .stMultiSelect div[data-baseweb="select"] {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
    }

    /* 7. Status & Toasts */
    div[data-testid="stStatusWidget"] {
        background-color: #161b22 !important;
        border: 1px solid #00f2fe !important;
    }
</style>""", unsafe_allow_html=True)

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