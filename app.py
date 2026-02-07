import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. BRANDING & CONFIG
st.set_page_config(page_title="Reschedule // AI-LINK", page_icon="📅", layout="wide")

# 2. PRISM DARK CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #0d1117; }
    h1, h2, h3, label { 
        font-family: 'Inter', sans-serif !important; 
        color: #f0f6fc !important; 
        font-weight: 800 !important;
    }
    p, .stMarkdown { color: #8b949e !important; }
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #bc8cff 100%) !important;
        color: #000000 !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    .prism-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px; padding: 25px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialize Session States
if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: THE GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("# 📡 RESCHEDULE GATEWAY")
    st.write("### AI-DRIVEN CAMPUS RESOURCE OPTIMIZER")
    
    is_free = st.checkbox("SIGNAL AVAILABILITY", key="gate_toggle")
    if is_free:
        st.markdown("<h1 style='color:#00f2fe !important; font-size: 60px;'>I AM FREE</h1>", unsafe_allow_html=True)
        if st.button("PROCEED TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: THE HUB ---
elif st.session_state.page == 'hub':
    # LOGIN LOGIC (Write to Spreadsheet)
    if 'user' not in st.session_state:
        with st.form("identity"):
            sid = st.text_input("ROLL NUMBER (Student ID)")
            nickname = st.text_input("NICKNAME")
            submit = st.form_submit_button("CONNECT TO NETWORK")
            
            if submit and sid and nickname:
                try:
                    # Fetch existing data
                    df = conn.read(ttl=0)
                except:
                    # If sheet is totally empty/error, create a fresh DataFrame
                    df = pd.DataFrame(columns=['student_id', 'name', 'is_active', 'interests'])

                # Force student_id to string for comparison
                df['student_id'] = df['student_id'].astype(str)
                
                if sid in df['student_id'].values:
                    df.loc[df['student_id'] == sid, 'is_active'] = True
                    df.loc[df['student_id'] == sid, 'name'] = nickname
                else:
                    new_user = pd.DataFrame([{
                        "student_id": str(sid), 
                        "name": nickname, 
                        "is_active": True, 
                        "interests": "Library / CC"
                    }])
                    df = pd.concat([df, new_user], ignore_index=True)
                
                # UPLOAD TO GOOGLE SHEETS
                conn.update(data=df)
                st.toast("Successfully added to Spreadsheet!", icon="✅")
                
                st.session_state.user = {"id": sid, "name": nickname}
                st.rerun()
        st.stop()

    # LOGGED IN VIEW
    user = st.session_state.user
    st.write(f"# 🪐 HUB // {user['name'].upper()}")

    try:
        # 1. Fetch Fresh Data
        all_data = conn.read(ttl=0)
        
        # 2. Venue Suggestions
        st.write("### 📍 Empty Venues & Suggestions")
        v1, v2 = st.columns(2)
        with v1: st.markdown('<div class="prism-card"><h3>Computer Centre</h3><p>Status: <b>Empty</b><br>Activity: Project Work</p></div>', unsafe_allow_html=True)
        with v2: st.markdown('<div class="prism-card"><h3>Lecture Hall 3</h3><p>Status: <b>No Class</b><br>Activity: Study Group</p></div>', unsafe_allow_html=True)

        st.divider()
        st.write("### 🤖 ACTIVE PEER NODES")
        
        # 3. Filtering Logic (Handles Boolean or String "TRUE")
        if not all_data.empty:
            active_peers = all_data[
                (all_data['is_active'].astype(str).str.upper() == 'TRUE') & 
                (all_data['student_id'].astype(str) != str(user['id']))
            ]
            
            if not active_peers.empty:
                for _, p in active_peers.iterrows():
                    with st.container():
                        st.markdown(f'<div class="prism-card">👤 {p["name"]} <br> <span style="font-size:0.8em; color:#8b949e;">Interests: {p["interests"]}</span></div>', unsafe_allow_html=True)
                        if st.button(f"⚡ LINK WITH {p['name'].split()[0]}", key=f"btn_{p['student_id']}"):
                            st.session_state.linked_peer = p['name']
                            st.session_state.page = 'success'
                            st.rerun()
            else:
                st.info("Scanning... No other active nodes found at IIIT Kota.")
        else:
            st.warning("No data found in the spreadsheet. Be the first to join!")

    except Exception as e:
        st.error(f"Sync Error: {e}")

    # LOGOUT LOGIC (Sign out of spreadsheet)
    if st.sidebar.button("🚪 GO OFFLINE"):
        df = conn.read(ttl=0)
        df['student_id'] = df['student_id'].astype(str)
        df.loc[df['student_id'] == str(user['id']), 'is_active'] = False
        conn.update(data=df)
        st.session_state.clear()
        st.rerun()

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.markdown(f"""
        <div style="text-align: center; border: 2px solid #00f2fe; padding: 50px; border-radius: 30px; margin-top: 50px;">
            <h1 style="color:#00f2fe !important;">🚀 UPLINK SUCCESSFUL!</h1>
            <h2 style="color:white !important;">Linked with {st.session_state.linked_peer.upper()}</h2>
            <p>Meeting point suggested: <b>Computer Centre</b></p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("RETURN TO HUB"):
        st.session_state.page = 'hub'
        st.rerun()