import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. PAGE SETUP (Advanced UI Theme)
st.set_page_config(
    page_title="Reschedule // AI-LINK", 
    page_icon="藤", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ADVANCED CYBER-GRID CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    
    /* Core App Styling */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1c2c 0%, #0d1117 100%);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Neon Text */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        background: linear-gradient(to right, #00f2fe, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }

    /* Modern Glassmorphism Card */
    .prism-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    
    .prism-card:hover {
        transform: translateY(-5px);
        border-color: #00f2fe;
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
    }

    /* Advanced Animated Button */
    .stButton > button {
        background: linear-gradient(90deg, #00f2fe, #bc8cff, #00f2fe);
        background-size: 200% auto;
        color: #000 !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.5s;
        width: 100%;
    }

    .stButton > button:hover {
        background-position: right center;
        box-shadow: 0 0 15px #00f2fe;
        transform: scale(1.02);
    }

    /* Success Overlay */
    .success-panel {
        background: rgba(0, 242, 254, 0.05);
        border: 2px solid #00f2fe;
        border-radius: 30px;
        padding: 60px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(0, 242, 254, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 242, 254, 0); }
    }
    
    /* Sidebar Cleanup */
    [data-testid="stSidebar"] {
        background-color: rgba(13, 17, 23, 0.8);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNECTION (Back-end unchanged)
conn = st.connection("gsheets", type=GSheetsConnection)

if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center;'>
                <h1 style='font-size: 4rem;'>藤 AI-LINK</h1>
                <p style='color: #8b949e; font-size: 1.2rem;'>Campus Intelligence Protocol</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='prism-card'>", unsafe_allow_html=True)
        is_free = st.checkbox("藤 SIGNAL STATUS: AVAILABLE")
        if is_free:
            st.markdown("<h2 style='color:#00f2fe !important; text-align: center;'>NODE BROADCAST ACTIVE</h2>", unsafe_allow_html=True)
            if st.button("ENTER HUB"):
                st.session_state.page = 'hub'
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE 2: HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.write("## 抄 IDENTITY VERIFICATION")
            with st.form("login"):
                sid = st.text_input("ROLL NUMBER", placeholder="e.g. 2024BCS001")
                nick = st.text_input("NICKNAME", placeholder="How should peers see you?")
                if st.form_submit_button("INITIALIZE UPLINK"):
                    df = conn.read(ttl=0)
                    df.columns = df.columns.str.strip().str.lower()
                    sid_str = str(sid)
                    if not df.empty and sid_str in df['student_id'].astype(str).values:
                        df.loc[df['student_id'].astype(str) == sid_str, 'is_active'] = "TRUE"
                    else:
                        new_data = pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": "General"}])
                        df = pd.concat([df, new_data], ignore_index=True)
                    conn.update(data=df)
                    st.session_state.user = {"id": sid_str, "name": nick}
                    st.rerun()
        st.stop()

    # LOGGED IN
    user = st.session_state.user
    
    # Header Area
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.write(f"# ｪ SYSTEM HUB // {user['name'].upper()}")
    with hcol2:
        if st.button("売 REFRESH NODES"):
            st.cache_data.clear()
            st.rerun()

    try:
        all_data = conn.read(ttl=0)
        all_data.columns = all_data.columns.str.strip().str.lower()
        
        # Dashboard Content
        st.markdown("### 📍 CAMPUS HOTSPOTS")
        v1, v2, v3 = st.columns(3)
        with v1: st.markdown('<div class="prism-card"><h4>Computer Centre</h4><p style="color:#00f2fe;">Status: HIGH VACANCY</p></div>', unsafe_allow_html=True)
        with v2: st.markdown('<div class="prism-card"><h4>Lecture Hall 3</h4><p style="color:#bc8cff;">Status: STUDY GROUP ACTIVE</p></div>', unsafe_allow_html=True)
        with v3: st.markdown('<div class="prism-card"><h4>Main Library</h4><p style="color:#8b949e;">Status: QUIET ZONE</p></div>', unsafe_allow_html=True)

        st.markdown("### 🤖 ACTIVE PEER NODES")
        if not all_data.empty:
            others = all_data[
                (all_data['student_id'].astype(str) != str(user['id'])) & 
                (all_data['is_active'].astype(str).str.upper() == "TRUE")
            ]

            if not others.empty:
                # Use a multi-column grid for peers
                p_cols = st.columns(3)
                for idx, row in enumerate(others.iterrows()):
                    with p_cols[idx % 3]:
                        st.markdown(f"""
                        <div class="prism-card">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <div style="width:12px; height:12px; background:#00f2fe; border-radius:50%; box-shadow: 0 0 10px #00f2fe;"></div>
                                <b style="font-size:1.3rem; color: white;">{row[1]['name']}</b>
                            </div>
                            <p style="margin: 10px 0; color: #8b949e;">Focus: {row[1]['interests']}</p>
                            <small style="color: rgba(255,255,255,0.3);">NODE ID: {row[1]['student_id']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"UPLINK WITH {row[1]['name'].split()[0]}", key=row[1]['student_id']):
                            st.session_state.linked_peer = row[1]['name']
                            st.session_state.page = 'success'
                            st.rerun()
            else:
                st.info("No other nodes detected on the network.")
                
    except Exception as e:
        st.error(f"UI Sync Error: {e}")

    # Sidebar Logout
    with st.sidebar:
        st.markdown("### 藤 CONNECTION")
        st.write(f"Protocol Active: **{user['name']}**")
        if st.button("坎 TERMINATE CONNECTION"):
            df = conn.read(ttl=0)
            df.columns = df.columns.str.strip().str.lower()
            df.loc[df['student_id'].astype(str) == str(user['id']), 'is_active'] = "FALSE"
            conn.update(data=df)
            st.session_state.clear()
            st.rerun()

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="success-panel">
                <h1 style="font-size: 3rem;">怖 UPLINK ESTABLISHED</h1>
                <p style="font-size: 1.5rem; color: white;">You are now linked with <b>{st.session_state.linked_peer.upper()}</b></p>
                <hr style="border: 1px solid rgba(0, 242, 254, 0.2); margin: 30px 0;">
                <p style="color: #00f2fe;">Suggested Rendezvous: <b>Computer Centre Lounge</b></p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("RETURN TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()