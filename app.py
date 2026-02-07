import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# 1. ARCHITECTURAL CONFIG
st.set_page_config(
    page_title="Reschedule // Resource Protocol", 
    page_icon="🤖", 
    layout="wide"
)

# 2. HIGH-END CYBER-GRID CSS
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
    
    .node-card:hover {
        border-color: #00f2fe;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.15);
        transform: translateY(-5px);
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

    .stButton > button {
        background: transparent !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono' !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        transition: 0.3s;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 class='hud-header' style='font-size: 5rem; text-align: center; margin-bottom:0;'>AI-LINK</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e; letter-spacing: 4px;'>NETWORK ACCESS PROTOCOL</p>", unsafe_allow_html=True)
        st.write("---")
        if st.button("INITIALIZE SYSTEM"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB ---
elif st.session_state.page == 'hub':
    # --- AUTHENTICATION BLOCK ---
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
                        st.cache_data.clear()
                        df = conn.read(ttl=0)
                        df.columns = df.columns.str.strip().str.lower()
                        
                        # Data Cleaning: Convert existing 1/0 to TRUE/FALSE strings
                        df['is_active'] = df['is_active'].astype(str).str.replace('1', 'TRUE').str.replace('0', 'FALSE').str.upper()
                        
                        sid_str = str(sid).strip()
                        interest_str = ", ".join(interests)
                        
                        if not df.empty and sid_str in df['student_id'].astype(str).values:
                            mask = df['student_id'].astype(str) == sid_str
                            df.loc[mask, 'is_active'] = "TRUE"
                            df.loc[mask, 'name'] = nick
                            df.loc[mask, 'interests'] = interest_str
                        else:
                            new_user = pd.DataFrame([{
                                "student_id": sid_str, 
                                "name": nick, 
                                "is_active": "TRUE", 
                                "interests": interest_str
                            }])
                            df = pd.concat([df, new_user], ignore_index=True)
                        
                        # Final check before update to ensure no 1/0 is sent
                        df['is_active'] = df['is_active'].astype(str).str.upper()
                        
                        conn.update(data=df)
                        st.cache_data.clear()
                        st.session_state.user = {"id": sid_str, "name": nick}
                        st.rerun()
                    except Exception as e:
                        st.error(f"Write Error: {e}")
        st.stop()

    # --- MAIN INTERFACE BLOCK ---
    user = st.session_state.user
    st.markdown(f"<h1>SYSTEM HUB // <span style='color:#bc8cff;'>{user['name'].upper()}</span></h1>", unsafe_allow_html=True)

    if st.button("🔄 SYNCHRONIZE ACTIVE NODES"):
        st.cache_data.clear()
        st.rerun()

    try:
        all_data = conn.read(ttl=0)
        all_data.columns = all_data.columns.str.strip().str.lower()
        
        # Cleanup Column D for UI and Logic
        all_data['is_active'] = all_data['is_active'].astype(str).str.strip().str.upper()
        all_data['is_active'] = all_data['is_active'].replace({'1': 'TRUE', '0': 'FALSE', '1.0': 'TRUE', '0.0': 'FALSE'})
        
        active_df = all_data[all_data['is_active'] == "TRUE"].copy().reset_index(drop=True)

        if len(active_df) < 2:
             st.info("📡 SCANNING... No other active nodes detected.")
        else:
            # KNN Logic
            active_df['interests_clean'] = active_df['interests'].astype(str).str.lower().apply(
                lambda x: [i.strip() for i in x.split(',') if i.strip()]
            )
            mlb = MultiLabelBinarizer()
            feature_matrix = mlb.fit_transform(active_df['interests_clean'])
            knn = NearestNeighbors(n_neighbors=len(active_df), metric='jaccard', algorithm='brute')
            knn.fit(feature_matrix)

            curr_user_idx = active_df[active_df['student_id'].astype(str) == str(user['id'])].index[0]
            distances, indices = knn.kneighbors([feature_matrix[curr_user_idx]])

            st.markdown(f"### 🎯 RECOMMENDED PEER NODES")
            cols = st.columns(3)
            count = 0
            
            for i, neighbor_idx in enumerate(indices[0][1:]):
                peer_row = active_df.iloc[neighbor_idx]
                dist = distances[0][i+1]
                match_score = int((1 - dist) * 100)
                display_tags = [t.upper() for t in peer_row['interests_clean']]
                badges_html = "".join([f"<span class='badge'>{x}</span>" for x in display_tags])
                
                with cols[count % 3]:
                    st.markdown(f"""
                        <div class='node-card'>
                            <div style='display: flex; justify-content: space-between;'>
                                <b style='color:#00f2fe; font-size:1.4rem;'>{peer_row['name']}</b>
                                <span style='color: #bc8cff; font-weight:bold;'>{match_score}% MATCH</span>
                            </div>
                            <p style='color:#8b949e; font-size:0.8rem; margin:10px 0;'>ID: {peer_row['student_id']}</p>
                            <div style='margin-bottom:20px;'>{badges_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"LINK WITH {peer_row['name'].upper()}", key=f"btn_{peer_row['student_id']}"):
                        st.session_state.linked_peer = peer_row['name']
                        st.session_state.page = 'success'
                        st.rerun()
                count += 1
                
    except Exception as e:
        st.error(f"System Error: {e}")

    with st.sidebar:
        st.markdown("### 🛠 DIAGNOSTICS")
        if st.checkbox("Show Network Data (Internal View)"):
            st.dataframe(all_data)
        if st.button("TERMINATE CONNECTION"):
            st.cache_data.clear()
            df = conn.read(ttl=0)
            df.columns = df.columns.str.strip().str.lower()
            df.loc[df['student_id'].astype(str) == str(user['id']), 'is_active'] = "FALSE"
            conn.update(data=df)
            st.session_state.clear()
            st.rerun()

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='text-align: center; border: 2px solid #00f2fe; padding: 50px; border-radius: 20px; background: rgba(0, 242, 254, 0.05);'>
            <h1 style='font-size: 4rem;'>UPLINK ESTABLISHED</h1>
            <p style='font-size: 1.5rem;'>Matched with <b style='color:#bc8cff;'>{st.session_state.linked_peer.upper()}</b></p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("RETURN TO HUB"):
        st.session_state.page = 'hub'
        st.rerun()