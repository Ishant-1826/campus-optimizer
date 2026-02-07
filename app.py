import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import socket
import threading
import time
from sklearn.neighbors import NearestNeighbors
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Reschedule // AI-LINK",
    page_icon="🪐",
    layout="wide"
)

# ---------------- 3D SPLINE BACKGROUND ----------------
def spline_background():
    components.html("""
    <style>
    iframe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        border: none;
        z-index: -10;
        pointer-events: none;
    }
    </style>
    <iframe src="https://my.spline.design/scene-APLWNQ6NOdTkkMLi/"></iframe>
    """, height=0)

spline_background()

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp { background: transparent; }
h1, h2, h3 {
    font-family: 'Inter', sans-serif;
    font-weight: 800 !important;
    background: linear-gradient(90deg,#00f2fe,#bc8cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.glass {
    background: rgba(20, 25, 35, 0.45);
    backdrop-filter: blur(18px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 0 30px rgba(123,156,255,0.15);
}
.stButton>button {
    background: linear-gradient(135deg,#00f2fe,#bc8cff);
    color: black;
    font-weight: 700;
    border-radius: 14px;
    padding: 12px 25px;
    border: none;
    transition: 0.25s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px #7b9cff;
}
.status { color:#00f2fe; font-weight:600; font-size:18px; }
</style>
""", unsafe_allow_html=True)

# ---------------- OFFLINE P2P DISCOVERY ----------------
UDP_PORT = 5005
if 'local_peers' not in st.session_state:
    st.session_state.local_peers = {}

def start_broadcast(name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        try:
            message = f"RESCHEDULE_PEER:{name}".encode()
            sock.sendto(message, ('<broadcast>', UDP_PORT))
        except:
            pass
        time.sleep(4)

def listen_for_peers():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', UDP_PORT))
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("RESCHEDULE_PEER:"):
                peer_name = msg.split(":")[1]
                st.session_state.local_peers[addr[0]] = {
                    "name": peer_name,
                    "time": time.time()
                }
    except:
        pass

# ---------------- PAGE ROUTING ----------------
if 'page' not in st.session_state:
    st.session_state.page = 'gate'

# ======================= GATEWAY ==========================
if st.session_state.page == 'gate':
    st.markdown("""
    <div class="glass" style="text-align:center; margin-top:120px;">
        <h1 style="font-size:60px;">RESCHEDULE AI-LINK</h1>
        <p style="color:#c9d1d9; font-size:18px;">
        Real-time peer matching system that detects free students.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        is_free = st.toggle("I am available now", key="gate_toggle")
        if is_free:
            st.markdown('<p class="status">● Discoverable to peers</p>', unsafe_allow_html=True)
            if st.button("ENTER HUB"):
                st.session_state.page = 'hub'
                st.rerun()

# ========================= HUB ============================
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("id"):
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            sid = st.text_input("Roll Number")
            name = st.text_input("Nickname")
            submit = st.form_submit_button("Connect to Network")
            st.markdown('</div>', unsafe_allow_html=True)
            if submit:
                st.session_state.user = {"id": sid, "name": name}
                threading.Thread(target=start_broadcast, args=(name,), daemon=True).start()
                threading.Thread(target=listen_for_peers, daemon=True).start()
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.markdown(f'<div class="glass"><h2>🪐 Welcome, {user["name"]}</h2></div>', unsafe_allow_html=True)

    # -------- LOCAL MESH --------
    st.markdown("### 📶 Nearby Offline Peers")
    current_time = time.time()
    active_local = {k: v for k, v in st.session_state.local_peers.items() if current_time - v['time'] < 12}
    
    if active_local:
        for ip, info in active_local.items():
            st.success(f"Detected: {info['name']} (Local Wi-Fi)")
    else:
        st.info("Scanning network...")

    # -------- KNN CLOUD MATCHING --------
    st.markdown("### 🤖 AI Matched Peers")
    all_interests = ["Python", "DSA", "ML", "Math", "Linear Algebra"]
    my_focus = st.multiselect("Select your focus:", all_interests, default=["Python"])

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        all_data = conn.read(ttl=0)

        # Ensure required columns exist
        for col in ['student_id', 'interests', 'is_active', 'last_seen']:
            if col not in all_data.columns:
                all_data[col] = None

        all_data['interests'] = all_data['interests'].fillna("")
        all_data['is_active'] = all_data['is_active'].fillna(False).astype(bool)
        all_data['last_seen'] = pd.to_numeric(all_data['last_seen'], errors='coerce').fillna(0)

        # Update current user's status with heartbeat (last_seen)
        new_row = pd.DataFrame([{
            "student_id": user["id"],
            "name": user["name"],
            "interests": ",".join(my_focus),
            "is_active": True,
            "last_seen": time.time()
        }])

        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        # FILTER: Show only users active in the last 60 seconds (prevents zombie users)
        active_peers = all_data[
            (all_data['is_active'] == True) & 
            (all_data['student_id'] != user['id']) & 
            (time.time() - all_data['last_seen'] < 60)
        ]

        if not active_peers.empty:
            def encode(lst): return [1 if i in lst.split(",") else 0 for i in all_interests]
            peer_vecs = [encode(p) for p in active_peers['interests']]
            my_vec = [1 if i in my_focus else 0 for i in all_interests]

            knn = NearestNeighbors(n_neighbors=min(len(peer_vecs), 4), metric='cosine')
            knn.fit(peer_vecs)
            dist, idx = knn.kneighbors([my_vec])

            for i, val in enumerate(idx[0]):
                p = active_peers.iloc[val]
                sim = round((1 - dist[0][i]) * 100, 1)
                st.markdown(f'<div class="glass"><h3>👤 {p["name"]}</h3><p>Similarity: <b>{sim}%</b></p></div>', unsafe_allow_html=True)
                if st.button(f"Link with {p['name']}", key=p['student_id']):
                    st.session_state.linked_peer = p['name']
                    st.session_state.page = 'success'
                    st.rerun()
        else:
            st.write("No active peers found in the last minute.")

    except Exception as e:
        st.error(f"Cloud Error: {e}")
        st.warning("Offline mesh mode active.")

    if st.sidebar.button("Disconnect"):
        st.session_state.clear()
        st.rerun()

# ======================== SUCCESS =========================
elif st.session_state.page == 'success':
    st.markdown(f"""
    <div class="glass" style="text-align:center; margin-top:150px;">
        <h1>🚀 LINK ESTABLISHED</h1>
        <h2>Connected with {st.session_state.get('linked_peer', 'Peer')}</h2>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Return to Hub"):
        st.session_state.page = 'hub'
        st.rerun()