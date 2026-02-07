import streamlit as st
import pandas as pd
import socket
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# --- 1. NETWORK DIAGNOSTICS ---
def get_local_ip():
    try:
        # Create a dummy connection to get the local interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
DB_FILE = "mesh_database.csv"
REQUIRED_COLS = ["student_id", "name", "is_active", "interests"]

# --- 2. ROBUST LOCAL DATA STORAGE ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if df.empty:
                return pd.DataFrame(columns=REQUIRED_COLS)
            # Standardize columns
            df.columns = [str(c).strip().lower() for c in df.columns]
            return df
        except Exception:
            return pd.DataFrame(columns=REQUIRED_COLS)
    return pd.DataFrame(columns=REQUIRED_COLS)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 3. ARCHITECTURAL CONFIG ---
st.set_page_config(page_title="Mesh Link // Offline", page_icon="📡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Outfit:wght@300;600;900&display=swap');
    .stApp { background: #07090e; color: #e6edf3; font-family: 'Outfit'; }
    .node-card { background: rgba(255, 255, 255, 0.03); border: 1px solid #00f2fe33; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .badge { background: #bc8cff22; color: #bc8cff; padding: 2px 8px; border-radius: 10px; font-family: 'JetBrains Mono'; font-size: 0.7rem; margin-right: 4px; border: 1px solid #bc8cff44; display: inline-block; margin-top: 5px; }
    .hud-header { background: linear-gradient(90deg, #00f2fe, #bc8cff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 class='hud-header' style='text-align:center; font-size:4rem;'>MESH-LINK</h1>", unsafe_allow_html=True)
        st.info(f"📡 OFFLINE MODE: Others can join at http://{LOCAL_IP}:8501")
        if st.button("INITIALIZE LOCAL NODE", use_container_width=True):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            with st.form("auth"):
                st.markdown("### 🛰️ JOIN LOCAL MESH")
                sid = st.text_input("UNIVERSITY ID (Roll No)")
                nick = st.text_input("ALIAS (Name)")
                interests = st.multiselect("EXPERTISE", ["Python", "ML", "DSA", "Web Dev", "Cybersec", "Design", "AI", "Blockchain"])
                
                if st.form_submit_button("BROADCAST PRESENCE"):
                    if not sid or not nick:
                        st.error("Identification required.")
                    else:
                        df = load_data()
                        sid_str = str(sid).strip()
                        interest_str = ", ".join(interests)
                        
                        # Update existing or Append new
                        if not df.empty and sid_str in df['student_id'].astype(str).values:
                            df.loc[df['student_id'].astype(str) == sid_str, ['name', 'interests', 'is_active']] = [nick, interest_str, "TRUE"]
                        else:
                            new_row = pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": interest_str}])
                            df = pd.concat([df, new_row], ignore_index=True)
                        
                        save_data(df)
                        st.session_state.user = {"id": sid_str, "name": nick}
                        st.rerun()
        st.stop()

    # --- MATCHING ENGINE ---
    user = st.session_state.user
    st.markdown(f"<h2>SYSTEM HUB // <span style='color:#bc8cff;'>{user['name'].upper()}</span></h2>", unsafe_allow_html=True)
    
    all_data = load_data()
    # Filter only active users, and ensure 'interests' isn't NaN
    active_df = all_data[(all_data['is_active'].astype(str).str.upper() == "TRUE") & (all_data['interests'].notna())].copy().reset_index(drop=True)

    if len(active_df) > 1:
        # Preprocessing for KNN
        active_df['int_list'] = active_df['interests'].str.lower().apply(lambda x: [i.strip() for i in str(x).split(',') if i.strip()])
        
        mlb = MultiLabelBinarizer()
        matrix = mlb.fit_transform(active_df['int_list'])
        
        # KNN using Jaccard Similarity (best for sets of interests)
        knn = NearestNeighbors(metric='jaccard', algorithm='brute')
        knn.fit(matrix)
        
        try:
            curr_idx = active_df[active_df['student_id'].astype(str) == str(user['id'])].index[0]
            distances, indices = knn.kneighbors([matrix[curr_idx]], n_neighbors=len(active_df))

            st.markdown("### RECOMMENDED PEER NODES")
            cols = st.columns(3)
            
            display_count = 0
            for i, neighbor_idx in enumerate(indices[0]):
                if neighbor_idx == curr_idx: continue # Skip yourself
                
                peer = active_df.iloc[neighbor_idx]
                dist = distances[0][i]
                score = int((1 - dist) * 100)
                
                with cols[display_count % 3]:
                    st.markdown(f"""
                        <div class='node-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <b style='color:#00f2fe; font-size:1.2rem;'>{peer['name']}</b>
                                <span style='color:#bc8cff; font-weight:bold;'>{score}% MATCH</span>
                            </div>
                            <p style='font-size:0.8rem; color:#8b949e; margin-bottom:10px;'>ID: {peer['student_id']}</p>
                            {"".join([f"<span class='badge'>{t.upper()}</span>" for t in peer['int_list']])}
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"LINK WITH {peer['name'].upper()}", key=f"btn_{peer['student_id']}", use_container_width=True):
                        st.balloons()
                        st.success(f"Connection established with {peer['name']}!")
                    display_count += 1
        except Exception as e:
            st.error(f"Engine Synchronization Error: {e}")
    else:
        st.warning("📡 SCANNING... No other active nodes detected on the mesh. Ask peers to join your IP.")

    with st.sidebar:
        st.markdown("### 🛠️ MESH DIAGNOSTICS")
        st.write(f"**Local IP:** {LOCAL_IP}")
        if st.button("TERMINATE CONNECTION", use_container_width=True):
            df = load_data()
            df.loc[df['student_id'].astype(str) == str(user['id']), 'is_active'] = "FALSE"
            save_data(df)
            st.session_state.clear()
            st.rerun()