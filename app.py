import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
import json
import os
import socket

# 1. CONFIG & STYLING
st.set_page_config(page_title="AI-LINK // Mesh", page_icon="藤", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Outfit:wght@300;900&display=swap');
    .stApp { background: #07090e; font-family: 'Outfit', sans-serif; color: #e6edf3; }
    .node-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .hud-header {
        background: linear-gradient(90deg, #00f2fe, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MESH UTILITIES
LOCAL_FILE = "mesh_nodes.json"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_internet():
    try:
        # Check for connection to Cloudflare DNS
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        return False

# 3. CORE LOGIC
if 'page' not in st.session_state: st.session_state.page = 'gate'
online_status = check_internet()

# --- PAGE: GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<h1 class='hud-header' style='font-size:4rem; margin-top:100px;'>AI-LINK</h1>", unsafe_allow_html=True)
    if not online_status:
        st.warning("坑 INTERNET BLACKOUT DETECTED: AUTO-SWITCHING TO MESH MODE")
    
    if st.button("INITIALIZE PROTOCOL", use_container_width=True):
        st.session_state.page = 'hub'
        st.rerun()

# --- PAGE: HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("auth"):
            st.subheader("USER UPLINK")
            sid = st.text_input("UNIVERSITY ID")
            nick = st.text_input("ALIAS")
            interests = st.multiselect("EXPERTISE", ["Python", "ML", "DSA", "Math", "AI", "Web Dev"], default=["Python"])
            
            if st.form_submit_button("CONNECT"):
                user_data = {"student_id": str(sid), "name": nick, "interests": ", ".join(interests), "is_active": "TRUE"}
                
                if online_status:
                    # GSheets Logic
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df = conn.read(ttl=0)
                    df.columns = df.columns.str.strip().str.lower()
                    # Append or update
                    df = df[df['student_id'].astype(str) != str(sid)] # Remove old record
                    df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
                    conn.update(data=df)
                else:
                    # Local Mesh Logic
                    if os.path.exists(LOCAL_FILE):
                        with open(LOCAL_FILE, 'r') as f: 
                            data = json.load(f)
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame(columns=["student_id", "name", "interests", "is_active"])
                    
                    df = df[df['student_id'].astype(str) != str(sid)]
                    df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
                    with open(LOCAL_FILE, 'w') as f: 
                        f.write(df.to_json(orient='records'))
                
                st.session_state.user = {"id": str(sid), "name": nick}
                st.rerun()
        st.stop()

    # DISPLAY PEERS
    st.title(f"HUB // {st.session_state.user['name'].upper()}")
    
    # Load Data based on connectivity
    if online_status:
        try:
            all_data = st.connection("gsheets", type=GSheetsConnection).read(ttl=0)
        except:
            all_data = pd.read_json(LOCAL_FILE) if os.path.exists(LOCAL_FILE) else pd.DataFrame()
    else:
        all_data = pd.read_json(LOCAL_FILE) if os.path.exists(LOCAL_FILE) else pd.DataFrame()

    if not all_data.empty:
        all_data.columns = all_data.columns.str.strip().str.lower()
        # CRITICAL FIX: Ensure we only show OTHER active peers
        active_peers = all_data[
            (all_data['is_active'].astype(str).str.upper() == "TRUE") & 
            (all_data['student_id'].astype(str) != st.session_state.user['id'])
        ].copy()

        if active_peers.empty:
            st.info("Scanning for active nodes... No other peers online.")
        else:
            st.subheader("RECOMMENDED PEER NODES")
            for _, peer in active_peers.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class='node-card'>
                            <h3 style='color:#00f2fe; margin:0;'>{peer['name']}</h3>
                            <p style='color:#8b949e;'>ID: {peer['student_id']} | SKILLS: {peer['interests']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"LINK WITH {peer['name'].upper()}", key=peer['student_id']):
                        st.success(f"Uplink established with {peer['name']}!")

    st.sidebar.markdown(f"**MESH STATUS:** {'ONLINE' if online_status else 'OFFLINE'}")
    st.sidebar.markdown(f"**NODE IP:** `{get_local_ip()}`")