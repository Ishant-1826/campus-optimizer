import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. ADVANCED UI CONFIG
st.set_page_config(page_title="NEXUS // IIIT KOTA", layout="wide")

# 2. CUSTOM CSS: PILL TOGGLE & GLASSMORPHISM
st.markdown("""
    <style>
    .stApp { background-color: #050508; }
    h1, h2, h3, p, label { color: #00f2fe !important; text-align: center; }
    
    /* THE PILL TOGGLE (Large, blue when active) */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 45px !important; width: 90px !important;
        background-color: #333 !important; border-radius: 45px !important;
        border: 2px solid #4facfe !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #4facfe !important;
    }
    
    /* Redirect Animation Container */
    .loader {
        border: 4px solid #1a1a2e; border-top: 4px solid #00f2fe;
        border-radius: 50%; width: 50px; height: 50px;
        animation: spin 1s linear infinite; margin: auto;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. NAVIGATION LOGIC
if 'page' not in st.session_state:
    st.session_state.page = 'gateway'

# --- PAGE 1: THE GATEWAY (Entrance) ---
if st.session_state.page == 'gateway':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 NEXUS NETWORK")
    st.write("### AI & DATA ENGINEERING HUB")
    
    # Large Toggle
    is_free = st.checkbox("Toggle to Signal Availability", key="gate_toggle")
    
    if is_free:
        st.markdown("<h1 style='font-size: 50px;'>I AM FREE</h1>", unsafe_allow_html=True)
        # Advanced Redirect Animation
        st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
        st.write("Redirecting to Neural Hub...")
        time.sleep(1.5)
        st.session_state.page = 'dashboard'
        st.rerun()

# --- PAGE 2: THE ADVANCED DASHBOARD ---
elif st.session_state.page == 'dashboard':
    if 'user' not in st.session_state:
        st.write("## 🆔 NODE INITIALIZATION")
        with st.container(border=True):
            sid = st.text_input("ROLL NUMBER", placeholder="2025KUAD...")
            name = st.text_input("NAME", placeholder="Ishant Gupta")
            if st.button("AUTHORIZE"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🛰️ HUB // {user['name'].upper()}")
    
    # Sync & Search Logic
    my_focus = st.multiselect("DEFINE FOCUS:", ["Python", "DSA", "ML", "Math"], default=["Python"])
    
    try:
        # Pushing Data to Cloud
        new_row = pd.DataFrame([{
            "student_id": user["id"], "name": user["name"], 
            "interests": ",".join(my_focus), "is_active": True
        }])
        all_data = conn.read(ttl=0) # Read fresh
        
        # Clean data to avoid 'float' errors
        all_data['interests'] = all_data['interests'].fillna("")
        
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df) # Write back
        
        # Display Matches
        st.divider()
        st.write("### 🤝 COMPATIBLE NODES")
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        for _, p in peers.iterrows():
            with st.container(border=True):
                st.write(f"👤 **{p['name']}**")
                st.caption(f"Studying: {p['interests']}")
                st.button("⚡ LINK NODE", key=p['student_id'])
                
    except Exception as e:
        st.error(f"Uplink Error: {e}")
        st.info("Check Secrets: Spreadsheet URL and Service Account Permissions.")

    if st.sidebar.button("🚪 LOGOUT"):
        st.session_state.page = 'gateway'
        st.rerun()