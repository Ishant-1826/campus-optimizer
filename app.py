import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Reschedule // AI-LINK", page_icon="📅", layout="wide")

# 2. PRISM DARK CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3, label { color: #f0f6fc !important; font-family: 'Inter', sans-serif; }
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #bc8cff 100%) !important;
        color: black !important; font-weight: 800; width: 100%; border-radius: 10px;
    }
    .prism-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        border-radius: 15px; padding: 20px; margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)

if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: GATEWAY ---
if st.session_state.page == 'gate':
    st.write("# 📡 RESCHEDULE GATEWAY")
    if st.checkbox("SIGNAL AVAILABILITY"):
        if st.button("PROCEED TO HUB"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        with st.form("login"):
            sid = st.text_input("ROLL NUMBER")
            nick = st.text_input("NICKNAME")
            if st.form_submit_button("CONNECT"):
                # Fetch and Update
                df = conn.read(ttl=0) # ttl=0 is vital for real-time
                df.columns = df.columns.str.strip().str.lower() # Normalize headers
                
                # Update logic
                sid_str = str(sid)
                if not df.empty and sid_str in df['student_id'].astype(str).values:
                    df.loc[df['student_id'].astype(str) == sid_str, 'is_active'] = "TRUE"
                else:
                    new_data = pd.DataFrame([{"student_id": sid_str, "name": nick, "is_active": "TRUE", "interests": "General"}])
                    df = pd.concat([df, new_data], ignore_index=True)
                
                conn.update(data=df)
                st.session_state.user = {"id": sid_str, "name": nick}
                st.rerun()
        st.stop()

    # LOGGED IN
    user = st.session_state.user
    st.write(f"# 🪐 HUB // {user['name'].upper()}")
    
    # REFRESH BUTTON (Manual override)
    if st.button("🔄 REFRESH NETWORK STATUS"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Load data and CLEAN HEADERS
        all_data = conn.read(ttl=0)
        all_data.columns = all_data.columns.str.strip().str.lower()
        
        # --- THE FIX: ROBUST FILTER ---
        # We convert the entire column to string and check for 'TRUE'
        if not all_data.empty:
            # 1. Filter out the current user
            # 2. Filter only those where is_active is TRUE
            others = all_data[
                (all_data['student_id'].astype(str) != str(user['id'])) & 
                (all_data['is_active'].astype(str).str.upper() == "TRUE")
            ]

            st.write(f"### 🤖 ACTIVE PEER NODES ({len(others)})")

            if not others.empty:
                for _, row in others.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="prism-card">
                            <b style="color:#00f2fe; font-size:1.2em;">{row['name']}</b><br>
                            <small>ID: {row['student_id']} | Interests: {row['interests']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"⚡ LINK WITH {row['name']}", key=row['student_id']):
                            st.session_state.linked_peer = row['name']
                            st.session_state.page = 'success'
                            st.rerun()
            else:
                st.info("No other active users detected. Try opening this link in an Incognito window to log in as a second user!")
                
    except Exception as e:
        st.error(f"Error displaying peers: {e}")

    if st.sidebar.button("🚪 GO OFFLINE"):
        df = conn.read(ttl=0)
        df.columns = df.columns.str.strip().str.lower()
        df.loc[df['student_id'].astype(str) == str(user['id']), 'is_active'] = "FALSE"
        conn.update(data=df)
        st.session_state.clear()
        st.rerun()

# --- PAGE 3: SUCCESS ---
elif st.session_state.page == 'success':
    st.success(f"UPLINK SUCCESSFUL WITH {st.session_state.linked_peer}")
    if st.button("RETURN"):
        st.session_state.page = 'hub'
        st.rerun()