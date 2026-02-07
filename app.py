import streamlit as st
import pandas as pd
import socket
import os
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# --- CONFIG ---
st.set_page_config(page_title="Mesh Link", page_icon="📡", layout="wide")

DB_FILE = "mesh_database.csv"
REQUIRED_COLS = ["student_id", "name", "is_active", "interests", "last_seen"]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "127.0.0.1"

# --- DATABASE ENGINE ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if df.empty: return pd.DataFrame(columns=REQUIRED_COLS)
            return df
        except: return pd.DataFrame(columns=REQUIRED_COLS)
    return pd.DataFrame(columns=REQUIRED_COLS)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- APP LOGIC ---
if 'page' not in st.session_state: st.session_state.page = 'gate'

if st.session_state.page == 'gate':
    st.title("📡 MESH-LINK")
    st.info(f"HOST IP: {get_local_ip()}")
    if st.button("INITIALIZE"):
        st.session_state.page = 'hub'
        st.rerun()

elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("auth"):
            sid = st.text_input("ID")
            name = st.text_input("ALIAS")
            ints = st.multiselect("SKILLS", ["Python", "ML", "Web", "Design"])
            if st.form_submit_button("JOIN MESH"):
                df = load_data()
                # Remove existing entry if same ID to prevent duplicates
                df = df[df['student_id'].astype(str) != str(sid)]
                new_row = pd.DataFrame([{
                    "student_id": sid, "name": name, 
                    "is_active": "TRUE", "interests": ",".join(ints),
                    "last_seen": time.time()
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    # --- HEARTBEAT & AUTO-CLEANUP ---
    # This fragment runs every 5 seconds to update current user and filter others
    @st.fragment(run_every=5)
    def mesh_sync():
        df = load_data()
        now = time.time()
        
        # 1. Update MY pulse
        df.loc[df['student_id'].astype(str) == str(st.session_state.user['id']), 'last_seen'] = now
        df.loc[df['student_id'].astype(str) == str(st.session_state.user['id']), 'is_active'] = "TRUE"
        
        # 2. Filter Active: Must be "TRUE" AND seen in the last 15 seconds
        # This automatically "removes" users who closed their tab
        active_nodes = df[
            (df['is_active'].astype(str).str.upper() == "TRUE") & 
            (now - df['last_seen'] < 15)
        ].copy()
        
        save_data(df) # Save the pulse
        
        st.subheader(f"📡 ACTIVE PEERS ({len(active_nodes) - 1})")
        
        if len(active_nodes) > 1:
            cols = st.columns(3)
            peer_idx = 0
            for _, row in active_nodes.iterrows():
                if str(row['student_id']) == str(st.session_state.user['id']):
                    continue
                
                with cols[peer_idx % 3]:
                    st.markdown(f"""
                        <div style='background:rgba(0,242,254,0.05); border:1px solid #00f2fe; border-radius:10px; padding:15px;'>
                            <b style='color:#00f2fe;'>{row['name']}</b><br>
                            <small>ID: {row['student_id']}</small><br>
                            <span style='font-size:0.7rem;'>{row['interests']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                peer_idx += 1
        else:
            st.warning("No other peers detected. Waiting for connections...")

    mesh_sync()

    # --- MANUAL EXIT ---
    if st.sidebar.button("TERMINATE CONNECTION"):
        df = load_data()
        df.loc[df['student_id'].astype(str) == str(st.session_state.user['id']), 'is_active'] = "FALSE"
        save_data(df)
        st.session_state.clear()
        st.rerun()