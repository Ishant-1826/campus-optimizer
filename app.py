import streamlit as st
import pandas as pd
import socket
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Mesh Link", page_icon="📡", layout="wide")

# Add auto-refresh logic
if "last_update" not in st.session_state:
    st.session_state.last_update = 0

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

DB_FILE = "mesh_database.csv"
REQUIRED_COLS = ["student_id", "name", "is_active", "interests"]

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if df.empty: return pd.DataFrame(columns=REQUIRED_COLS)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    return pd.DataFrame(columns=REQUIRED_COLS)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- UI LOGIC ---
if 'page' not in st.session_state: st.session_state.page = 'gate'

if st.session_state.page == 'gate':
    st.title("📡 MESH-LINK OFFLINE")
    st.info(f"HOST IP: {get_local_ip()}")
    if st.button("ENTER MESH"):
        st.session_state.page = 'hub'
        st.rerun()

elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("join"):
            sid = st.text_input("ID")
            name = st.text_input("NAME")
            ints = st.multiselect("SKILLS", ["Python", "JS", "AI", "Design"])
            if st.form_submit_button("JOIN"):
                df = load_data()
                new_row = pd.DataFrame([{"student_id": sid, "name": name, "is_active": "TRUE", "interests": ",".join(ints)}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    # --- THE REFRESHING PART ---
    # This experimental fragment keeps the peer list updated every 3 seconds
    @st.fragment(run_every=3)
    def peer_grid():
        df = load_data()
        active = df[df['is_active'].astype(str).str.upper() == "TRUE"]
        
        st.subheader(f"Active Nodes ({len(active)})")
        if len(active) > 1:
            # KNN Logic here (simplified for space)
            cols = st.columns(3)
            for i, row in active.iterrows():
                if str(row['student_id']) != str(st.session_state.user['id']):
                    with cols[i % 3]:
                        st.success(f"Peer: {row['name']}")
                        st.caption(f"Interests: {row['interests']}")
        else:
            st.write("Waiting for peers to join the IP...")

    peer_grid()

    if st.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()