import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import time
from sklearn.neighbors import NearestNeighbors

# 1. ADVANCED UI CONFIGURATION
st.set_page_config(page_title="NEXUS // AI-LINK", page_icon="🔗", layout="wide")

# 2. PRISM DARK CSS (High-Contrast Black Font + Pill Toggle)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=JetBrains+Mono&display=swap');
    
    .stApp { background-color: #0d1117; }
    
    /* Global Typography */
    h1, h2, h3, label { 
        font-family: 'Inter', sans-serif !important; 
        color: #f0f6fc !important; 
        font-weight: 800 !important;
    }
    p, .stMarkdown { color: #8b949e !important; font-family: 'Inter', sans-serif; }

    /* BUTTONS: Prism Gradient with BLACK FONT for readability */
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #bc8cff 100%) !important;
        color: #000000 !important; /* Black font as requested */
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.4) !important;
    }

    /* TOGGLE: Modern Pill */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 34px !important; width: 65px !important;
        background-color: #21262d !important; border-radius: 20px !important;
        border: 2px solid #30363d !important;
    }
    div[data-testid="stCheckbox"] > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #00f2fe !important;
        border-color: #00f2fe !important;
    }

    /* Resource & Peer Cards */
    .prism-card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px; padding: 25px; margin-bottom: 20px;
    }
    .venue-badge { background: #238636; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. DB CONNECTION & HELPERS
conn = st.connection("gsheets", type=GSheetsConnection)
all_possible_interests = ["Python", "DSA", "ML", "Math", "Linear Algebra", "Digital Electronics"]

def encode_interests(interest_list):
    return [1 if i in interest_list else 0 for i in all_possible_interests]

# --- NAVIGATION & STATE ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'linked_peer' not in st.session_state: st.session_state.linked_peer = None

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 NEXUS GATEWAY")
    is_free = st.checkbox("SIGNAL AVAILABILITY", key="gate_toggle")
    if is_free:
        # High-contrast "I AM FREE" message
        st.markdown("<h1 style='color:#00f2fe !important; font-size: 60px;'>I AM FREE</h1>", unsafe_allow_html=True)
        if st.button("PROCEED TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB (AI MATCH + TIMETABLE) ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        st.write("## 🆔 NODE INITIALIZATION")
        with st.form("identity_form"):
            sid = st.text_input("ROLL NUMBER")
            name = st.text_input("NICKNAME")
            if st.form_submit_button("CONNECT"):
                st.session_state.user = {"id": sid, "name": name}
                st.rerun()
        st.stop()

    user = st.session_state.user
    st.write(f"# 🛰️ HUB // {user['name'].upper()}")

    # --- NEW: CAMPUS RESOURCE ENGINE ---
    st.divider()
    st.subheader("📍 Live Campus Resource Availability")
    
    # Static demo data representing empty venues and suggests
    campus_data = [
        {"venue": "Computer Centre (CC)", "status": "Empty", "suggested": "ML Project Work"},
        {"venue": "Lecture Hall 201", "status": "No Class", "suggested": "DSA Study Group"},
        {"venue": "Library Zone 4", "status": "Available", "suggested": "Quiet Reading"}
    ]
    
    res_cols = st.columns(3)
    for i, res in enumerate(campus_data):
        with res_cols[i]:
            st.markdown(f"""
            <div class="prism-card">
                <span class="venue-badge">LIVE: {res['status']}</span>
                <h3 style="margin:10px 0;">{res['venue']}</h3>
                <p>Activity: <b>{res['suggested']}</b></p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    # --- KNN MATCHING ENGINE ---
    my_focus = st.multiselect("DEFINE FOCUS VECTORS:", all_possible_interests, default=["Python"])
    
    try:
        user_vector = encode_interests(my_focus)
        new_row = pd.DataFrame([{"student_id": user["id"], "name": user["name"], "interests": ",".join(my_focus), "is_active": True}])
        
        all_data = conn.read(ttl=0)
        all_data['interests'] = all_data['interests'].fillna("")
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        if not peers.empty:
            st.write("### 🤖 AI-MATCHED PEER NODES")
            peer_vectors = [encode_interests(str(p).split(",")) for p in peers['interests']]
            knn = NearestNeighbors(n_neighbors=min(len(peer_vectors), 4), metric='cosine')
            knn.fit(peer_vectors)
            distances, indices = knn.kneighbors([user_vector])
            
            grid = st.columns(2)
            for i, idx_val in enumerate(indices[0]):
                p = peers.iloc[idx_val]
                sim = round((1 - distances[0][i]) * 100, 1)
                with grid[i % 2]:
                    st.markdown(f"""
                    <div class="prism-card">
                        <h2 style="margin:0;">👤 {p['name']}</h2>
                        <p style="margin:5px 0;">Neural Similarity: <b>{sim}%</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    # Button text is black for high contrast
                    if st.button(f"⚡ LINK WITH {p['name'].split()[0]}", key=p['student_id']):
                        st.session_state.linked_peer = p['name']
                        st.session_state.page = 'success'
                        st.rerun()
        else:
            st.info("Scanning for compatible nodes in the Kota network...")
    except Exception as e:
        st.error(f"Sync Error: {e}")

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; background: rgba(0, 112, 243, 0.1); border: 1px solid #00f2fe; padding: 50px; border-radius: 30px;">
            <h1 style="font-size: 50px; color:#00f2fe !important;">🚀 SUCCESS!</h1>
            <h2 style="color:#ffffff !important;">LINK ESTABLISHED WITH {st.session_state.linked_peer.upper()}</h2>
            <p style="color:#ffffff !important; font-weight:800;">Suggested Venue: COMPUTER CENTRE</p>
        </div>
    """, unsafe_allow_html=True)
    
    

    if st.button("RETURN TO HUB"):
        st.session_state.page = 'hub'
        st.rerun()