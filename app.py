import streamlit as st
import pandas as pd
import time
import os

# --- DATABASE SETTINGS ---
DB_FILE = "mesh_database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["student_id", "name", "is_active", "interests", "last_seen"])

def save_data(df):
    # 1. Save to Local CSV (This is what makes Offline work)
    df.to_csv(DB_FILE, index=False)
    
    # 2. OPTIONAL: Try to sync to Google Sheets if internet is available
    # This won't crash the app if offline because of the 'try' block
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(data=df)
    except Exception:
        pass # Stay silent if offline

# --- UI LOGIC ---
st.title("📡 MESH-LINK SYNC")

if 'user' not in st.session_state:
    with st.form("join"):
        sid = st.text_input("ID")
        name = st.text_input("NAME")
        if st.form_submit_button("JOIN"):
            df = load_data()
            # Add/Update the user
            new_user = pd.DataFrame([{
                "student_id": sid, "name": name, 
                "is_active": "TRUE", "last_seen": time.time()
            }])
            df = pd.concat([df, new_user], ignore_index=True)
            save_data(df) # This saves to the local file!
            st.session_state.user = {"id": sid, "name": name}
            st.rerun()
else:
    # HEARTBEAT: Keep the user active in the CSV
    @st.fragment(run_every=5)
    def heartbeat():
        df = load_data()
        now = time.time()
        # Update current user's timestamp
        df.loc[df['student_id'].astype(str) == str(st.session_state.user['id']), 'last_seen'] = now
        save_data(df)
        
        # Display everyone in the CSV
        st.write("### All Users in Database:")
        st.dataframe(df) 
        
    heartbeat()