import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. ARCHITECTURAL CONFIG
st.set_page_config(
    page_title="AI-LINK // Resource Optimizer", 
    page_icon="📡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CYBER-MODERN CSS INJECTION
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;500;800&family=Outfit:wght@300;600;900&display=swap');
    
    /* Background & Global Font */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #161b22 0%, #0d1117 100%);
        font-family: 'Outfit', sans-serif;
    }

    /* Neon Typography */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: -0.05em !important;
        background: linear-gradient(135deg, #00f2fe 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Tactical Card Styling */
    .cyber-card {
        background: rgba(22, 27, 34, 0.4);
        border: 1px solid rgba(48, 54, 61, 0.5);
        border-left: 4px solid #00f2fe;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    
    .cyber-card:hover {
        transform: scale(1.01) translateX(5px);
        background: rgba(30, 35, 45, 0.6);
        border-color: #bc8cff;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.1);
    }

    /* Advanced Buttons */
    .stButton > button {
        background: transparent !important;
        color: #00f2fe !important;
        border: 2px solid #00f2fe !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 15px 30px !important;
        transition: all 0.4s !important;
    }

    .stButton > button:hover {
        background: #00f2fe !important;
        color: #0d1117 !important;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.4);
    }

    /* Sidebar HUD */
    [data-testid="stSidebar"] {
        background-color: #090c10 !important;
        border-right: 1px solid #30363d;
    }

    /* Status Pulse */
    .pulse-dot {
        height: 10px;
        width: 10px;
        background-color: #00f2fe;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 10px #00f2fe;
        animation: pulse-animation 2s infinite;
    }

    @keyframes pulse-animation {
        0% { transform: scale(0.95); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.5; }
        100% { transform: scale(0.95); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CORE LOGIC
conn = st.connection("gsheets", type=GSheetsConnection)

if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY (Advanced Entry) ---
if st.session_state.page == 'gate':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
            <div style='text-align: center;'>
                <p style='color: #00f2fe; font-family: "JetBrains Mono"; letter-spacing: 5px;'>PROTOCOL: RESCHEDULE</p>
                <h1 style='font-size: 5rem; margin-bottom: 0;'>AI-LINK</h1>
                <p style='color: #8b949e; margin-bottom: 50px;'>Neural Campus Resource Distributor</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.write("### SYSTEM READINESS")
        is_ready = st.checkbox("ACTIVATE PERSONAL SIGNAL")
        if is_ready:
            if st.button("INITIALIZE UPLINK"):
                st.session_state.page = 'hub'
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE 2: THE HUB (Neural Grid) ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.write("## 👤 AUTHENTICATION")
            with st.form("auth_form"):
                sid = st.text_input("IDENTIFICATION NUMBER", placeholder="e.g. 2024IIITK01")
                nick = st.text_input("NICKNAME / ALIAS", placeholder="Ex: Shadow")
                if st.form_submit_button("CONNECT TO NEURAL GRID"):
                    df = conn.read(ttl=0)
                    df.columns = df.columns.str.strip().str.lower()
                    sid_str = str(sid)
                    if not df.empty and sid_str in df['student_id'].astype(str).values:
                        df.loc[df['student_id'].astype(str) == sid_str, 'is_active'] = "TRUE"
                    else:
                        new_user = pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": "Logic Labs"}])
                        df = pd.concat([df, new_user], ignore_index=True)
                    conn.update(data=df)
                    st.session_state.user = {"id": sid_str, "name": nick}
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # LOGGED IN INTERFACE
    user = st.session_state.user
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <h1>NODE: {user['name'].upper()}</h1>
            <p style='font-family: "JetBrains Mono"; color: #00f2fe;'>STATUS: CONNECTED</p>
        </div>
    """, unsafe_allow_html=True)

    # REFRESH ACTION
    if st.button("SYNCHRONIZE NETWORK"):
        st.cache_data.clear()
        st.rerun()

    # Campus Metrics
    st.markdown("### 📍 TACTICAL VENUE SUGGESTIONS")
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown('<div class="cyber-card"><h4 style="color:#00f2fe">Comp Centre</h4><p>Usage: 12%<br><b>OPEN FOR PROJECTS</b></p></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="cyber-card"><h4 style="color:#bc8cff">LH-3</h4><p>Usage: 45%<br><b>STUDY GROUP DETECTED</b></p></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="cyber-card"><h4 style="color:#8b949e">Library</h4><p>Usage: 88%<br><b>SILENCE PROTOCOL</b></p></div>', unsafe_allow_html=True)

    # ACTIVE PEER GRID
    st.markdown("### 🤖 ACTIVE PEER NODES")
    try:
        all_data = conn.read(ttl=0)
        all_data.columns = all_data.columns.str.strip().str.lower()
        
        peers = all_data[
            (all_data['student_id'].astype(str) != str(user['id'])) & 
            (all_data['is_active'].astype(str).str.upper() == "TRUE")
        ]

        if not peers.empty:
            p_cols = st.columns(2) # Modern 2-column grid
            for i, (_, row) in enumerate(peers.iterrows()):
                with p_cols[i % 2]:
                    st.markdown(f"""
                        <div class="cyber-card">
                            <div class="pulse-dot"></div>
                            <span style="font-size: 1.4rem; color: #f0f6fc; font-weight: 600;">{row['name']}</span>
                            <p style="color: #8b949e; margin-top: 10px;">
                                Primary Interest: {row['interests']}<br>
                                <span style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">ID: {row['student_id']}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"LINK WITH {row['name'].upper()}", key=f"link_{row['student_id']}"):
                        st.session_state.linked_peer = row['name']
                        st.session_state.page = 'success'
                        st.rerun()
        else:
            st.info("PROTOCOL IDLE: No other active nodes found in the current radius.")
                
    except Exception as e:
        st.error(f"NEURAL SYNC ERROR: {e}")

    # Sidebar HUD
    with st.sidebar:
        st.markdown("### HUD SETTINGS")
        st.write(f"Operator: **{user['name']}**")
        st.write(f"ID: `{user['id']}`")
        st.divider()
        if st.button("TERMINATE SESSION"):
            df = conn.read(ttl=0)
            df.columns = df.columns.str.strip().str.lower()
            df.loc[df['student_id'].astype(str) == str(user['id']), 'is_active'] = "FALSE"
            conn.update(data=df)
            st.session_state.clear()
            st.rerun()

# --- PAGE 3: SUCCESS (Meeting Protocol) ---
elif st.session_state.page == 'success':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
            <div class='cyber-card' style='text-align: center; border-left: none; border: 2px solid #00f2fe; padding: 60px;'>
                <h1 style='font-size: 4rem;'>LINK ESTABLISHED</h1>
                <p style='font-size: 1.5rem; color: #f0f6fc;'>You are now linked with <b>{st.session_state.linked_peer.upper()}</b></p>
                <div style='margin: 40px 0; padding: 20px; background: rgba(0, 242, 254, 0.1); border-radius: 8px;'>
                    <p style='color: #00f2fe; font-family: "JetBrains Mono"; margin: 0;'>RENDEZVOUS: Computer Centre - Node B</p>
                </div>
                <br>
            </div>
        """, unsafe_allow_html=True)
        if st.button("RETURN TO COMMAND HUB"):
            st.session_state.page = 'hub'
            st.rerun()