import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import socket
import threading
import time
from datetime import datetime
from sklearn.neighbors import NearestNeighbors
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Reschedule // AI-LINK", page_icon="🪐", layout="wide")

# ---------------- 3D SPLINE BACKGROUND ----------------
def spline_background():
    components.html("""
    <style>
    iframe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: -10; pointer-events: none; }
    </style>
    <iframe src="https://my.spline.design/scene-APLWNQ6NOdTkkMLi/"></iframe>
    """, height=0)

spline_background()

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stApp { background: transparent; }
h1, h2, h3 {
    font-family: 'Inter', sans-serif; font-weight: 800 !important;
    background: linear-gradient(90deg,#00f2fe,#bc8cff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.glass {
    background: rgba(20, 25, 35, 0.45); backdrop-filter: blur(18px);
    border-radius: 18px; border: 1px solid rgba(255,255,255,0.15);
    padding: 25px; margin-bottom: 20px;
}
.stButton>button {
    background: linear-gradient(135deg,#00f2fe,#bc8cff);
    color: black; font-weight: 700; border-radius: 14px; border: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- P2P DISCOVERY ----------------
UDP_PORT = 5005
if 'local_peers' not in st.session_state: st.session_state.local_peers = {}

def start_broadcast(name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        try:
            sock.sendto(f"RESCHEDULE_PEER:{name}".encode(), ('<broadcast>', UDP_PORT))
        except: pass
        time.sleep(4)

def listen_for_peers():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        if msg.startswith("RESCHEDULE_PEER:"):
            st.session_state.local_peers[addr[0]] = {"name": msg.split(":")[1], "time": time.time()}

# ---------------- PAGE ROUTING ----------------
if 'page' not in st.session_state: st.session_state.page = 'gate'

# ======================= GATEWAY ==========================
if st.session_state.page == 'gate':
    st.markdown('<div class="glass" style="text-align:center; margin-top:120px;"><h1>RESCHEDULE AI-LINK</h1><p>Real-time peer matching system.</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.toggle("I am available now", key="gate_toggle"):
            if st.button("ENTER HUB"):
                st.session_state.page = 'hub'
                st.rerun()

# ========================= HUB ============================
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("id"):
            sid = st.text_input("Roll Number")
            name = st.text_input("Nickname")
            if st.form_submit_button("Connect"):
                st.session_state.user = {"id": sid, "name": name}
                threading.Thread(target=start_broadcast, args=(name,), daemon=True).start()
                threading.Thread(target=listen_for_peers, daemon=True).start()
                st.rerun()
        st.stop()

    user = st.session_state.user
    all_interests = ["Python", "DSA", "ML", "Math", "Linear Algebra"]
    my_focus = st.multiselect("Select your focus:", all_interests, default=["Python"])

    # HEARTBEAT & CLOUD SYNC
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        
        # Cleanup old users (Auto-disconnect anyone inactive for > 2 minutes)
        now_ts = time.time()
        
        # Update current user
        new_data = {
            "student_id": user["id"],
            "name": user["name"],
            "interests": ",".join(my_focus),
            "last_seen": now_ts,
            "is_active": True
        }
        
        # Filter: Keep others who are active AND seen within last 120 seconds
        active_others = df[
            (df['student_id'] != user["id"]) & 
            (now_ts - df['last_seen'].astype(float) < 120)
        ]
        
        updated_df = pd.concat([active_others, pd.DataFrame([new_data])], ignore_index=True)
        conn.update(data=updated_df)

        st.markdown(f"### 🤖 AI Matched Peers ({len(active_others)} online)")

        if not active_others.empty:
            def encode(lst): return [1 if i in str(lst).split(",") else 0 for i in all_interests]
            peer_vecs = [encode(p) for p in active_others['interests']]
            my_vec = [1 if i in my_focus else 0 for i in all_interests]

            knn = NearestNeighbors(n_neighbors=min(len(peer_vecs), 4), metric='cosine')
            knn.fit(peer_vecs)
            dist, idx = knn.kneighbors([my_vec])

            
            for i, val in enumerate(idx[0]):
                p = active_others.iloc[val]
                sim = round((1 - dist[0][i]) * 100, 1)
                st.markdown(f'<div class="glass"><h3>👤 {p["name"]}</h3><p>Similarity: {sim}%</p></div>', unsafe_allow_html=True)
                if st.button(f"Link with {p['name']}", key=p['student_id']):
                    st.session_state.linked_peer = p['name']
                    st.session_state.page = 'success'
                    st.rerun()
        else:
            st.info("No other active peers found in the cloud yet.")

    except Exception as e:
        # Improved error handling to see why it fails
        st.error(f"Connection Error: {e}")
        st.warning("Running in local mesh mode only.")

    if st.sidebar.button("Disconnect"):
        st.session_state.clear()
        st.rerun()

# ======================== SUCCESS =========================
elif st.session_state.page == 'success':
    st.markdown(f'<div class="glass" style="text-align:center; margin-top:150px;"><h1>🚀 LINK ESTABLISHED</h1><h2>Connected with {st.session_state.linked_peer}</h2></div>', unsafe_allow_html=True)
    if st.button("Return to Hub"):
        st.session_state.page = 'hub'
        st.rerun()