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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');

    /* ========================================
       1. BACKGROUND: DEEP SPACE WITH SUBTLE ANIMATION
       ======================================== */
    .stApp {
        background: linear-gradient(135deg, #0a0e14 0%, #0d1117 50%, #05080d 100%);
        background-attachment: fixed;
        position: relative;
    }
    
    /* Subtle animated gradient overlay - reduces harshness */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(
            circle at 20% 50%, 
            rgba(0, 212, 255, 0.03) 0%, 
            transparent 50%
        ),
        radial-gradient(
            circle at 80% 80%, 
            rgba(167, 139, 250, 0.04) 0%, 
            transparent 50%
        );
        pointer-events: none;
        z-index: 0;
    }

    /* ========================================
       2. TYPOGRAPHY: CLEAR HIERARCHY
       ======================================== */
    
    /* Main Heading - Bold, Statement */
    h1 {
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 3.2rem !important;
        color: #ffffff !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.1 !important;
        text-shadow: 0 2px 20px rgba(0, 212, 255, 0.15);
    }
    
    /* Secondary Headings - Colored Accent */
    h2 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        color: #00d4ff !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 1rem !important;
        line-height: 1.3 !important;
    }
    
    /* Tertiary Headings */
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        color: #c9d1d9 !important;
        letter-spacing: 0.01em !important;
        text-transform: uppercase !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Body Text - Improved Readability */
    .stMarkdown p, label, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: #8b949e !important;
        font-weight: 400 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        text-shadow: none !important; /* Removed glow */
    }

    /* ========================================
       3. GLASSMORPHISM CARDS 2.0
       ======================================== */
    .glass-card {
        background: rgba(13, 17, 23, 0.7) !important;
        backdrop-filter: blur(16px) saturate(150%);
        -webkit-backdrop-filter: blur(16px) saturate(150%);
        border: 1px solid rgba(48, 54, 61, 0.6);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 
            0 4px 24px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    /* Subtle edge glow on hover */
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 20px;
        padding: 1px;
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.3), 
            rgba(167, 139, 250, 0.3)
        );
        -webkit-mask: linear-gradient(#fff 0 0) content-box, 
                      linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .glass-card:hover {
        transform: translateY(-6px);
        border-color: rgba(167, 139, 250, 0.6);
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.6),
            0 0 0 1px rgba(167, 139, 250, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .glass-card:hover::before {
        opacity: 1;
    }

    /* ========================================
       4. BUTTONS: REFINED GRADIENTS & ANIMATIONS
       ======================================== */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
        color: #0a0e14 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 4px 16px rgba(0, 212, 255, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #00b8e6 100%) !important;
        box-shadow: 
            0 6px 24px rgba(0, 212, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px) scale(1.02);
    }

    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }

    /* Secondary Button Style (for disconnect, etc.) */
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #ff6b9d 0%, #c94277 100%) !important;
        color: #ffffff !important;
    }

    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #ff85ad 0%, #e35188 100%) !important;
        box-shadow: 0 6px 24px rgba(255, 107, 157, 0.4) !important;
    }

    /* ========================================
       5. TOGGLE/CHECKBOX: MODERN PILL SWITCH
       ======================================== */
    div[data-testid="stCheckbox"] {
        padding: 1rem 0;
    }

    div[data-testid="stCheckbox"] > label {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #c9d1d9 !important;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    /* The actual toggle switch */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 32px !important;
        width: 60px !important;
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%) !important;
        border-radius: 16px !important;
        border: 2px solid #30363d !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        position: relative;
    }

    /* Checked state - gradient accent */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #a78bfa 100%) !important;
        border-color: #00d4ff !important;
        box-shadow: 
            0 0 20px rgba(0, 212, 255, 0.4),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
    }

    /* The sliding knob */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"]::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        width: 24px;
        height: 24px;
        background: #ffffff;
        border-radius: 50%;
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"]::after {
        transform: translateX(28px);
    }

    /* ========================================
       6. INPUTS: TEXT FIELDS & MULTISELECT
       ======================================== */
    .stTextInput > div > div > input {
        background-color: rgba(22, 27, 34, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        color: #c9d1d9 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15) !important;
        background-color: rgba(13, 17, 23, 0.8) !important;
    }

    /* Multiselect */
    .stMultiSelect div[data-baseweb="select"] {
        background-color: rgba(22, 27, 34, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    .stMultiSelect div[data-baseweb="select"]:focus-within {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15) !important;
    }

    /* Multiselect tags */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: rgba(167, 139, 250, 0.2) !important;
        border: 1px solid rgba(167, 139, 250, 0.4) !important;
        color: #a78bfa !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* ========================================
       7. SIDEBAR: REFINED DARK PANEL
       ======================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e14 0%, #0d1117 100%) !important;
        border-right: 1px solid rgba(48, 54, 61, 0.6) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }

    /* ========================================
       8. CONTAINERS & BORDERS
       ======================================== */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        gap: 1.5rem;
    }

    /* Container with border (used in entrance page) */
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(13, 17, 23, 0.6) !important;
        border: 1px solid rgba(48, 54, 61, 0.6) !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        backdrop-filter: blur(12px);
    }

    /* ========================================
       9. STATUS WIDGETS & TOASTS
       ======================================== */
    div[data-testid="stStatusWidget"] {
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.1) 0%, 
            rgba(167, 139, 250, 0.1) 100%) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(8px);
    }

    div[data-testid="stStatusWidget"] > div {
        color: #00d4ff !important;
    }

    /* Info boxes */
    .stAlert {
        background-color: rgba(13, 17, 23, 0.8) !important;
        border-left: 4px solid #a78bfa !important;
        border-radius: 8px !important;
        color: #c9d1d9 !important;
    }

    /* ========================================
       10. COLUMNS & GRID LAYOUT
       ======================================== */
    div[data-testid="column"] {
        padding: 0.5rem;
    }

    /* ========================================
       11. SCROLLBAR STYLING
       ======================================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #0d1117;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d4ff 0%, #a78bfa 100%);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00f2fe 0%, #b49dff 100%);
    }

    /* ========================================
       12. LOADING ANIMATIONS
       ======================================== */
    div[data-testid="stSpinner"] > div {
        border-top-color: #00d4ff !important;
        border-right-color: #a78bfa !important;
    }

    /* ========================================
       13. SPECIAL: "I AM FREE" STATEMENT
       ======================================== */
    h1[style*="color:#4facfe"] {
        background: linear-gradient(135deg, #00d4ff 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 4rem !important;
        font-weight: 800 !important;
        text-align: center;
        animation: pulse 2s ease-in-out infinite;
        filter: drop-shadow(0 4px 30px rgba(0, 212, 255, 0.4));
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.9; transform: scale(1.02); }
    }

    /* ========================================
       14. UTILITY: SPACING & RESPONSIVE
       ======================================== */
    .element-container {
        margin-bottom: 1rem;
    }

    /* Better mobile spacing */
    @media (max-width: 768px) {
        h1 { font-size: 2.5rem !important; }
        h2 { font-size: 1.5rem !important; }
        .glass-card { padding: 1.5rem; }
        .stButton > button { padding: 0.65rem 1.5rem !important; }
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