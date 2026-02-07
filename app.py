import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED UI CONFIGURATION
st.set_page_config(page_title="NEXUS // AI-LINK", page_icon="🔗", layout="wide")

# 2. PRISM DARK CSS (High-Contrast + Pill Toggle)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, p, label { color: #f0f6fc !important; font-family: 'Inter', sans-serif; }
    
    /* CUSTOM BLUE PILL TOGGLE */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 40px !important; width: 80px !important;
        background-color: #21262d !important; border-radius: 40px !important;
        border: 2px solid #30363d !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #0070f3 !important;
        border-color: #0070f3 !important;
    }

    /* Glassmorphism Peer Card */
    .prism-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px; padding: 25px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DB CONNECTION & VECTOR HELPERS
conn = st.connection("gsheets", type=GSheetsConnection)
all_possible_interests = ["Python", "DSA", "ML", "Math", "Linear Algebra", "Digital Electronics"]

def encode_interests(interest_list):
    """Converts student interests into binary vectors for KNN matching."""
    return [1 if i in interest_list else 0 for i in all_possible_interests]

# --- NAVIGATION & STATE ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'linked_peer' not in st.session_state: st.session_state.linked_peer = None

# --- PAGE 1: THE GATEWAY (Entrance) ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 NEXUS GATEWAY")
    st.write("### ACTIVATE YOUR NODE TO BROADCAST AVAILABILITY")
    
    # Modern Pill Toggle Logic
    is_free = st.checkbox("SIGNAL AVAILABILITY", key="gate_toggle")
    
    if is_free:
        st.markdown("<h1 style='color:#0070f3 !important; font-size: 60px;'>I AM FREE</h1>", unsafe_allow_html=True)
        if st.button("PROCEED TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE AI HUB (KNN MATCHING) ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        st.write("## 🆔 NODE INITIALIZATION")
        with st.form("identity_form"):
            sid = st.text_input("ROLL NUMBER (e.g. 2025KUAD3005)")
            name = st.text_input("NICKNAME")
            if st.form_submit_button("CONNECT"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🛰️ HUB // {user['name'].upper()}")
    
    my_focus = st.multiselect("DEFINE FOCUS VECTORS:", all_possible_interests, default=["Python"])

    # SYNC & KNN COMPUTATION
    try:
        user_vector = encode_interests(my_focus)
        new_row = pd.DataFrame([{"student_id": user["id"], "name": user["name"], "interests": ",".join(my_focus), "is_active": True}])
        
        all_data = conn.read(ttl=0)
        all_data['interests'] = all_data['interests'].fillna("")
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        # Filter active peers only
        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        if not peers.empty:
            st.write("### 🤖 AI-MATCHED NODES")
            # KNN Algorithm Setup
            peer_vectors = [encode_interests(str(p).split(",")) for p in peers['interests']]
            knn = NearestNeighbors(n_neighbors=min(len(peer_vectors), 4), metric='cosine')
            knn.fit(peer_vectors)
            distances, indices = knn.kneighbors([user_vector])
            
            grid = st.columns(2)
            for i, idx_val in enumerate(indices[0]):
                p = peers.iloc[idx_val]
                similarity = round((1 - distances[0][i]) * 100, 1)
                
                with grid[i % 2]:
                    st.markdown(f"""
                    <div class="prism-card">
                        <h2 style="margin:0;">👤 {p['name']}</h2>
                        <p style="margin:5px 0;">Similarity: <b>{similarity}%</b></p>
                        <p style="color:#888;">Focus: {p['interests']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"⚡ LINK WITH {p['name'].split()[0]}", key=p['student_id']):
                        st.session_state.linked_peer = p['name']
                        st.session_state.page = 'success'
                        st.rerun()
        else:
            st.info("Scanning for compatible nodes in the Kota network...")

    except Exception as e:
        st.error(f"Sync Error: {e}")

    if st.sidebar.button("EXIT HUB"):
        st.session_state.page = 'gate'
        st.rerun()

# --- PAGE 3: SUCCESS INTERFACE ---
elif st.session_state.page == 'success':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; background: rgba(0, 112, 243, 0.1); border: 1px solid #0070f3; padding: 50px; border-radius: 30px;">
            <h1 style="font-size: 50px;">🚀 SUCCESS!</h1>
            <h2>NEURAL LINK ESTABLISHED WITH {st.session_state.linked_peer.upper()}</h2>
            <p>Your study session is now synchronized via the Nexus Protocol.</p>
        </div>
    """, unsafe_allow_html=True)

    

# [Image of K-Nearest Neighbors diagram]


    if st.button("RETURN TO DASHBOARD"):
        st.session_state.linked_peer = None
        st.session_state.page = 'hub'
        st.rerun()