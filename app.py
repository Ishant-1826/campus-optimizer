import streamlit as st
import pandas as pd
import socket
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# --- 1. NETWORK DIAGNOSTICS (For Offline Discovery) ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # Doesn't actually send data
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
DB_FILE = "mesh_database.csv"

# --- 2. LOCAL DATA STORAGE LOGIC ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df.columns = df.columns.str.strip().lower()
        return df
    return pd.DataFrame(columns=["student_id", "name", "is_active", "interests"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 3. ARCHITECTURAL CONFIG ---
st.set_page_config(page_title="Mesh Link // Offline", page_icon="📡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Outfit:wght@300;600;900&display=swap');
    .stApp { background: #07090e; color: #e6edf3; font-family: 'Outfit'; }
    .node-card { background: rgba(255, 255, 255, 0.03); border: 1px solid #00f2fe33; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .badge { background: #bc8cff22; color: #bc8cff; padding: 2px 8px; border-radius: 10px; font-family: 'JetBrains Mono'; font-size: 0.7rem; margin-right: 4px; border: 1px solid #bc8cff44; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"<h1 style='text-align:center; color:#00f2fe;'>MESH-LINK</h1>", unsafe_allow_html=True)
        st.info(f"📡 OFFLINE DISCOVERY ACTIVE: Peers should connect to http://{LOCAL_IP}:8501")
        if st.button("INITIALIZE LOCAL NODE"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("auth"):
            st.markdown("### 🛰️ JOIN LOCAL MESH")
            sid = st.text_input("UNIVERSITY ID")
            nick = st.text_input("ALIAS")
            interests = st.multiselect("EXPERTISE", ["Python", "ML", "DSA", "Web Dev", "Cybersec", "Design"])
            
            if st.form_submit_button("BROADCAST PRESENCE"):
                df = load_data()
                sid_str = str(sid).strip()
                interest_str = ", ".join(interests)
                
                # Update or Append
                if sid_str in df['student_id'].astype(str).values:
                    df.loc[df['student_id'].astype(str) == sid_str, ['name', 'interests', 'is_active']] = [nick, interest_str, "TRUE"]
                else:
                    new_user = pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": interest_str}])
                    df = pd.concat([df, new_user], ignore_index=True)
                
                save_data(df)
                st.session_state.user = {"id": sid_str, "name": nick}
                st.rerun()
        st.stop()

    # --- MATCHING ENGINE ---
    user = st.session_state.user
    st.markdown(f"## NODE: {user['name'].upper()}")
    
    all_data = load_data()
    active_df = all_data[all_data['is_active'].astype(str).str.upper() == "TRUE"].copy().reset_index(drop=True)

    if len(active_df) > 1:
        # Preprocessing
        active_df['int_list'] = active_df['interests'].str.lower().apply(lambda x: [i.strip() for i in str(x).split(',')])
        mlb = MultiLabelBinarizer()
        matrix = mlb.fit_transform(active_df['int_list'])
        
        # KNN
        knn = NearestNeighbors(metric='jaccard', algorithm='brute')
        knn.fit(matrix)
        
        curr_idx = active_df[active_df['student_id'].astype(str) == str(user['id'])].index[0]
        distances, indices = knn.kneighbors([matrix[curr_idx]], n_neighbors=len(active_df))

        st.subheader("PEER NODES DETECTED")
        cols = st.columns(3)
        
        for i, neighbor_idx in enumerate(indices[0][1:]): # Skip self
            peer = active_df.iloc[neighbor_idx]
            dist = distances[0][i+1]
            score = int((1 - dist) * 100)
            
            with cols[i % 3]:
                st.markdown(f"""
                    <div class='node-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <b style='color:#00f2fe;'>{peer['name']}</b>
                            <span style='color:#bc8cff;'>{score}%</span>
                        </div>
                        <p style='font-size:0.7rem; color:grey;'>ID: {peer['student_id']}</p>
                        {"".join([f"<span class='badge'>{t.upper()}</span>" for t in peer['int_list']])}
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"LINK WITH {peer['name']}", key=peer['student_id']):
                    st.success(f"Uplink established with {peer['name']} over Local Mesh!")
    else:
        st.warning("Scanning for peers... Ensure others are connected to your hotspot.")

    if st.sidebar.button("TERMINATE CONNECTION"):
        df = load_data()
        df.loc[df['student_id'].astype(str) == str(user['id']), 'is_active'] = "FALSE"
        save_data(df)
        st.session_state.clear()
        st.rerun()