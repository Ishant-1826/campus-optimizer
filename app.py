import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from sklearn.neighbors import NearestNeighbors

# --- CONFIGURATION ---
st.set_page_config(page_title="AI-LINK // KNN-GRID", page_icon="📡", layout="wide")

# Cyber-Grid Styling
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e6edf3; }
    .node-card {
        background: rgba(22, 27, 34, 0.9);
        border: 1px solid #30363d;
        padding: 15px; border-radius: 10px;
        margin-bottom: 10px;
    }
    .highlight { border: 1px solid #00f2fe; box-shadow: 0 0 10px #00f2fe; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'hub'

# --- PAGE: REGISTER (The "Make Me Available" Logic) ---
if st.session_state.page == 'register':
    st.markdown("<h1>REGISTRATION // <span style='color:#00f2fe;'>INJECT NODE</span></h1>", unsafe_allow_html=True)
    
    with st.form("injection_form"):
        name = st.text_input("Full Name")
        student_id = st.text_input("Student ID")
        # Interests represented as numbers for KNN logic (e.g., 1 for AI, 2 for Web, etc.)
        feat1 = st.slider("Interest in AI/ML", 0, 10, 5)
        feat2 = st.slider("Interest in Web Dev", 0, 10, 5)
        feat3 = st.slider("Interest in DSA", 0, 10, 5)
        
        submit = st.form_submit_button("INJECT INTO SPREADSHEET")
        
        if submit:
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                df = conn.read()
                new_row = pd.DataFrame([{
                    "Name": name, "ID": student_id, 
                    "AI": feat1, "Web": feat2, "DSA": feat3
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success(f"System Online: {name} added to Global Grid.")
            except Exception as e:
                st.error("Write Access Error: Check GSheet permissions (Editor access required).")

# --- PAGE: HUB (KNN Discovery) ---
elif st.session_state.page == 'hub':
    st.markdown("<h1>PROXIMITY // <span style='color:#00f2fe;'>KNN MESH</span></h1>", unsafe_allow_html=True)
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    if not df.empty:
        st.subheader("Discovered Nodes")
        st.dataframe(df, use_container_width=True)
        
        # --- KNN LOGIC ---
        # Using AI, Web, and DSA columns as features for the vector space
        features = df[['AI', 'Web', 'DSA']].values
        knn = NearestNeighbors(n_neighbors=min(len(df), 3), metric='euclidean')
        knn.fit(features)
        
        st.write("---")
        st.markdown("### 🔍 Vector Analysis")
        # Identify "You" (assuming last added or search by ID)
        target_id = st.text_input("Enter your ID to find nearest peers:")
        
        if target_id:
            user_idx = df[df['ID'] == target_id].index
            if not user_idx.empty:
                idx = user_idx[0]
                distances, indices = knn.kneighbors([features[idx]])
                
                for i in range(1, len(indices[0])):
                    peer_idx = indices[0][i]
                    peer_name = df.iloc[peer_idx]['Name']
                    dist = distances[0][i]
                    st.markdown(f"""
                        <div class='node-card highlight'>
                            <b>PEER MATCH:</b> {peer_name}<br>
                            <span style='color:#8b949e;'>Vector Distance: {dist:.2f}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("ID not found in spreadsheet. Go to 'Register' to add yourself.")

# --- SIDEBAR ---
with st.sidebar:
    if st.button("HUB"): st.session_state.page = 'hub'
    if st.button("REGISTER (ADD ME)"): st.session_state.page = 'register'
    if st.button("TIMETABLE"): st.session_state.page = 'timetable'