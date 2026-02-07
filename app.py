import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
import json
import os
import socket

# 1. ARCHITECTURAL CONFIG
st.set_page_config(
    page_title="AI-LINK // Mesh Protocol", 
    page_icon="藤", 
    layout="wide"
)

# 2. LOCAL MESH LOGIC (Twist Option B)
LOCAL_DB = "mesh_nodes.json"

def get_local_ip():
    """Retrieves the local IP to allow peers to connect during blackout."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def load_local_data():
    if os.path.exists(LOCAL_DB):
        with open(LOCAL_DB, "r") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame(columns=["student_id", "name", "is_active", "interests"])

def save_local_data(df):
    with open(LOCAL_DB, "w") as f:
        json.dump(df.to_dict(orient="records"), f)

# 3. HIGH-END CYBER-GRID CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;600;900&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 10% 10%, #10141d 0%, #07090e 100%);
        font-family: 'Outfit', sans-serif;
        color: #e6edf3;
    }

    .hud-header {
        background: linear-gradient(90deg, #00f2fe 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -2px;
        text-transform: uppercase;
    }

    .node-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
    }
    
    .badge {
        background: rgba(188, 140, 255, 0.1);
        color: #bc8cff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid rgba(188, 140, 255, 0.3);
        margin-right: 5px;
    }

    .status-offline { color: #ff4b4b; font-family: 'JetBrains Mono'; font-size: 0.8rem; }
    .status-online { color: #00f2fe; font-family: 'JetBrains Mono'; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# 4. CONNECTION ROUTER
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'mesh_mode' not in st.session_state: st.session_state.mesh_mode = False

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 class='hud-header' style='font-size: 5rem; text-align: center; margin-bottom:0;'>AI-LINK</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e; letter-spacing: 4px;'>NETWORK ACCESS PROTOCOL</p>", unsafe_allow_html=True)
        st.write("---")
        
        # Check Connection
        local_ip = get_local_ip()
        if local_ip == "127.0.0.1":
            st.markdown("<p class='status-offline'>坑 WEB UPLINK SEVERED // MESH MODE AUTO-ENABLED</p>", unsafe_allow_html=True)
            st.session_state.mesh_mode = True
        else:
            st.markdown(f"<p class='status-online'>鉄 MESH ACTIVE // HOST IP: {local_ip}</p>", unsafe_allow_html=True)

        if st.button("INITIALIZE SYSTEM"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            with st.form("auth"):
                st.markdown("<h2 style='text-align: center;'>USER UPLINK</h2>", unsafe_allow_html=True)
                sid = st.text_input("UNIVERSITY ID", placeholder="Roll Number")
                nick = st.text_input("ALIAS", placeholder="Choose a display name")
                interests = st.multiselect(
                    "CORE EXPERTISE", 
                    ["Python", "ML", "DSA", "Math", "Web Dev", "Cybersec", "AI", "Blockchain", "Design"],
                    default=["Python"]
                )
                
                if st.form_submit_button("ESTABLISH CONNECTION"):
                    try:
                        interest_str = ", ".join(interests)
                        sid_str = str(sid).strip()
                        
                        if not st.session_state.mesh_mode:
                            # Attempt GSheets
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            df = conn.read(ttl=0)
                            df.columns = df.columns.str.strip().str.lower()
                            # (Update logic remains same as your original)
                            if sid_str in df['student_id'].astype(str).values:
                                df.loc[df['student_id'].astype(str) == sid_str, ['name', 'interests', 'is_active']] = [nick, interest_str, "TRUE"]
                            else:
                                df = pd.concat([df, pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": interest_str}])])
                            conn.update(data=df)
                        else:
                            # Mesh Local Storage
                            df = load_local_data()
                            if sid_str in df['student_id'].astype(str).values:
                                df.loc[df['student_id'].astype(str) == sid_str, ['name', 'interests', 'is_active']] = [nick, interest_str, "TRUE"]
                            else:
                                df = pd.concat([df, pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": interest_str}])])
                            save_local_data(df)
                        
                        st.session_state.user = {"id": sid_str, "name": nick}
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sync Failure: {e}")
        st.stop()

    # --- MAIN INTERFACE ---
    user = st.session_state.user
    st.markdown(f"<h1>SYSTEM HUB // <span style='color:#bc8cff;'>{user['name'].upper()}</span></h1>", unsafe_allow_html=True)

    try:
        if not st.session_state.mesh_mode:
            all_data = st.connection("gsheets", type=GSheetsConnection).read(ttl=0)
        else:
            all_data = load_local_data()
            st.sidebar.warning("坑 RUNNING ON MESH PROTOCOL")

        all_data.columns = all_data.columns.str.strip().str.lower()
        active_df = all_data[all_data['is_active'].astype(str).str.upper() == "TRUE"].copy().reset_index(drop=True)

        if len(active_df) < 2:
             st.info("藤 SCANNING MESH... No other peers found on this node.")
        else:
            # KNN Logic
            active_df['interests_clean'] = active_df['interests'].astype(str).str.lower().apply(lambda x: [i.strip() for i in x.split(',') if i.strip()])
            mlb = MultiLabelBinarizer()
            feature_matrix = mlb.fit_transform(active_df['interests_clean'])
            knn = NearestNeighbors(n_neighbors=len(active_df), metric='jaccard', algorithm='brute')
            knn.fit(feature_matrix)

            curr_user_idx = active_df[active_df['student_id'].astype(str) == str(user['id'])].index[0]
            distances, indices = knn.kneighbors([feature_matrix[curr_user_idx]])

            st.markdown(f"### RECOMMENDED PEER NODES")
            cols = st.columns(3)
            for i, neighbor_idx in enumerate(indices[0][1:]):
                peer_row = active_df.iloc[neighbor_idx]
                match_score = int((1 - distances[0][i+1]) * 100)
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class='node-card'>
                            <b style='color:#00f2fe; font-size:1.4rem;'>{peer_row['name']}</b>
                            <span style='float:right; color:#bc8cff;'>{match_score}%</span>
                            <p style='color:#8b949e; font-size:0.8rem;'>NODE_ID: {peer_row['student_id']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"LINK {peer_row['name'].upper()}", key=f"btn_{peer_row['student_id']}"):
                        st.session_state.linked_peer = peer_row['name']
                        st.session_state.page = 'success'
                        st.rerun()

    except Exception as e:
        st.error(f"Node Read Error: {e}")

    with st.sidebar:
        st.markdown(f"**MESH STATUS:** {'ONLINE' if not st.session_state.mesh_mode else 'OFFLINE/LOCAL'}")
        st.markdown(f"**LOCAL IP:** `{get_local_ip()}`")
        if st.button("TERMINATE CONNECTION"):
            st.session_state.clear()
            st.rerun()

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; border: 2px solid #00f2fe; padding: 50px; border-radius: 20px; background: rgba(0, 242, 254, 0.05);'><h1>UPLINK ESTABLISHED</h1><p>Matched with {st.session_state.linked_peer.upper()}</p></div>", unsafe_allow_html=True)
    if st.button("RETURN TO HUB"):
        st.session_state.page = 'hub'; st.rerun()