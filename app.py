import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Set the page to a dark, academic theme
st.set_page_config(page_title="NEXUS // IIIT KOTA", layout="centered")

# --- DATABASE CONNECTION ---
# In Streamlit Cloud, you'll put your Google Sheet link in "Secrets"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN SECTION ---
if 'user' not in st.session_state:
    st.title("🎓 NEXUS // AUTH")
    sid = st.text_input("Roll Number")
    name = st.text_input("Full Name")
    branch = st.selectbox("Branch", ["AI & Data Engineering", "Computer Science", "Electronics"])
    if st.button("INITIALIZE"):
        st.session_state.user = {"id": sid, "name": name, "branch": branch}
        st.rerun()
    st.stop()

# --- MAIN INTERFACE ---
user = st.session_state.user
st.title("🎯 Peer Optimizer")
st.write(f"Active Node: **{user['name']}** | Branch: **{user['branch']}**")

is_active = st.toggle("BROADCAST MY GAP", value=False)
my_focus = st.multiselect("Study Focus:", ["Python", "DSA", "ML", "Linear Algebra"], default=["Python"])

# --- SYNC LOGIC ---
if is_active:
    # This part would normally write to the sheet. 
    # For now, let's read the shared peer list.
    try:
        df = conn.read(ttl=5) # Refresh every 5 seconds to see friends
        
        st.subheader("🤝 Available Peers")
        # Filter the sheet to show other active students
        others = df[df['student_id'] != user['id']]
        
        if others.empty:
            st.info("Searching for peers... Tell your friend to join!")
        else:
            for index, row in others.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['name']}** ({row['branch']})")
                    st.caption(f"Studying: {row['interests']}")
                    st.button("Sync Request", key=row['student_id'])
    except:
        st.warning("Connect your Google Sheet in App Secrets to see live peers.")