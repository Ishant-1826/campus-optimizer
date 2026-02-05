import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="NEXUS // IIIT KOTA", layout="centered")

# CSS to maintain your aesthetic
st.markdown("<style>.stApp { background-color: #050508; } h1, h2, h3, p, label { color: #00f2fe !important; }</style>", unsafe_allow_html=True)

# --- DATABASE CONNECTION ---
# This looks for your [connections.gsheets] in Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

if 'user' not in st.session_state:
    st.title("🎓 NEXUS // AUTH")
    sid = st.text_input("Roll Number")
    name = st.text_input("Full Name")
    branch = st.selectbox("Branch", ["AI & Data Engineering", "Computer Science", "Electronics"])
    if st.button("INITIALIZE"):
        st.session_state.user = {"id": sid, "name": name, "branch": branch}
        st.rerun()
    st.stop()

user = st.session_state.user
st.title("🎯 Peer Optimizer")
is_active = st.toggle("BROADCAST MY GAP", value=False)
my_focus = st.multiselect("Study Focus:", ["Python", "DSA", "ML", "Math"], default=["Python"])

# --- DATA SYNC LOGIC ---
if is_active:
    try:
        # 1. Prepare current user data
        new_row = pd.DataFrame([{
            "student_id": user["id"], "name": user["name"], "branch": user["branch"],
            "interests": ", ".join(my_focus), "is_active": True
        }])
        
        # 2. Update the Sheet: Read, Merge, Write back
        # We use ttl=0 so we don't read old cached data
        all_data = conn.read(ttl=0)
        updated_df = pd.concat([all_data[all_data['student_id'] != user["id"]], new_row], ignore_index=True)
        conn.update(data=updated_df)
        
    except Exception as e:
        st.error(f"Sync failed: {e}")

# --- PEER DISCOVERY ---
st.divider()
if is_active:
    try:
        # Read the latest data
        df = conn.read(ttl=2) 
        peers = df[(df['student_id'] != user['id']) & (df['is_active'] == True)]
        
        if peers.empty:
            st.info("Waiting for your friend to toggle ON...")
        else:
            for _, p in peers.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{p['name']}** ({p['branch']})")
                    st.caption(f"Studying: {p['interests']}")
    except:
        st.warning("Refresh or check connection.")
else:
    st.info("Toggle 'BROADCAST GAP' to see peers.")