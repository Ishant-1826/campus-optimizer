import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

# 1. PAGE CONFIG
st.set_page_config(page_title="NEXUS // AI MATCH", layout="wide")

# 2. CUSTOM CSS FOR LARGE TOGGLE & UI
st.markdown("""
    <style>
    .stApp { background-color: #050508; }
    h1, h2, h3, p { color: #00f2fe !important; text-align: center; }
    
    /* Bigger & Different Color Toggle */
    div[data-testid="stCheckbox"] > label > div[role="checkbox"] {
        height: 30px; width: 60px; background-color: #ff4b4b !important;
    }
    
    /* Make the Toggle Label Text Huge */
    .st-emotion-cache-1ebm0u9 { font-size: 24px !important; font-weight: bold; color: #ff4b4b !important; }

    .peer-card {
        background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe;
        padding: 20px; border-radius: 15px; margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INTEREST ENCODING FOR KNN ---
all_possible_interests = ["Python", "DSA", "ML", "Linear Algebra", "Digital Electronics", "Math"]

def encode_interests(interest_list):
    """Converts a list of interests into a binary vector for KNN."""
    return [1 if interest in interest_list else 0 for interest in all_possible_interests]

# --- SESSION STATE & AUTH ---
if 'user' not in st.session_state:
    st.title("👤 NODE IDENTITY")
    with st.container(border=True):
        sid = st.text_input("ROLL NUMBER")
        name = st.text_input("FULL NAME")
        if st.button("INITIALIZE"):
            st.session_state.user = {"id": sid, "name": name}
            st.rerun()
    st.stop()

# --- MAIN UI ---
user = st.session_state.user
st.write(f"### Welcome, {user['name']}")

# LARGE TOGGLE BUTTON
status_toggle = st.toggle("ACTIVATE STATUS", value=False)
status_text = "🟢 I AM FREE" if status_toggle else "🔴 I AM BUSY"
st.markdown(f"<h1 style='color: {'#00f2fe' if status_toggle else '#ff4b4b'} !important;'>{status_text}</h1>", unsafe_allow_html=True)

my_focus = st.multiselect("CHOOSE YOUR FOCUS:", all_possible_interests, default=["Python"])

# 4. SYNC & KNN MATCHING
if status_toggle:
    try:
        # Sync current user to Google Sheets
        user_vector = encode_interests(my_focus)
        new_row = pd.DataFrame([{
            "student_id": user["id"], "name": user["name"], 
            "interests": ",".join(my_focus), "is_active": True
        }])
        
        all_data = conn.read(ttl=0)
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)

        # --- KNN ENGINE ---
        active_peers = all_data[(all_data['student_id'] != user['id']) & (all_data['is_active'] == True)]
        
        if not active_peers.empty:
            # Prepare data for KNN
            peer_vectors = [encode_interests(p.split(",")) for p in active_peers['interests']]
            
            # Fit KNN model
            knn = NearestNeighbors(n_neighbors=min(len(peer_vectors), 3), metric='cosine')
            knn.fit(peer_vectors)
            
            # Find nearest neighbors to current user
            distances, indices = knn.kneighbors([user_vector])
            
            st.write("## 🤖 AI-Matched Study Partners")
            cols = st.columns(2)
            for i, idx_val in enumerate(indices[0]):
                peer = active_peers.iloc[idx_val]
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="peer-card">
                        <h3>{peer['name']}</h3>
                        <p>Similarity Score: {round((1 - distances[0][i])*100, 1)}%</p>
                        <p>Focus: {peer['interests']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button("Link Node", key=peer['student_id'])
        else:
            st.info("Searching for nodes with similar vectors...")

    except Exception as e:
        st.error(f"Satellite Sync Error: {e}")