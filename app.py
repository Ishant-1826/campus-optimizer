import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# 1. ARCHITECTURAL CONFIG
st.set_page_config(page_title="AI-LINK", page_icon="🧬", layout="wide")

# 2. CYBER-GRID CSS (Improved for visibility)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;600;900&display=swap');
    .stApp { background: radial-gradient(circle at 10% 10%, #10141d 0%, #07090e 100%); font-family: 'Outfit', sans-serif; color: #e6edf3; }
    .hud-header { background: linear-gradient(90deg, #00f2fe 0%, #bc8cff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; text-transform: uppercase; }
    .node-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 254, 0.2); border-radius: 16px; padding: 20px; margin-bottom: 20px; transition: 0.4s; backdrop-filter: blur(10px); }
    .node-card:hover { border-color: #00f2fe; box-shadow: 0 0 20px rgba(0, 242, 254, 0.2); }
    .match-percent { color: #bc8cff; font-family: 'JetBrains Mono'; font-weight: 900; font-size: 1.1rem; }
    .badge { background: rgba(188, 140, 255, 0.1); color: #bc8cff; padding: 2px 10px; border-radius: 10px; font-size: 0.7rem; font-family: 'JetBrains Mono'; border: 1px solid rgba(188, 140, 255, 0.3); margin-right: 4px; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
if 'page' not in st.session_state: st.session_state.page = 'gate'

# --- PAGE 1: GATEWAY ---
if st.session_state.page == 'gate':
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 class='hud-header' style='font-size: 5rem; text-align: center;'>AI-LINK</h1>", unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM"):
            st.session_state.page = 'hub'
            st.rerun()

# --- PAGE 2: HUB ---
elif st.session_state.page == 'hub':
    if 'user' not in st.session_state:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            with st.form("auth"):
                st.markdown("## USER UPLINK")
                sid = st.text_input("UNIVERSITY ID")
                nick = st.text_input("ALIAS")
                interests = st.multiselect("EXPERTISE", ["Python", "ML", "DSA", "Math", "AI"], default=["Python"])
                if st.form_submit_button("CONNECT"):
                    df = conn.read(ttl=0).dropna(how='all')
                    df.columns = df.columns.str.strip().str.lower()
                    sid_str = str(sid).strip()
                    # Ensure we write to 'is_active' as per your sheet image
                    new_data = {"student_id": sid_str, "name": nick, "interests": ", ".join(interests), "is_active": "TRUE"}
                    if sid_str in df['student_id'].astype(str).values:
                        df.loc[df['student_id'].astype(str) == sid_str, ['name', 'interests', 'is_active']] = [nick, ", ".join(interests), "TRUE"]
                    else:
                        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    conn.update(data=df)
                    st.session_state.user = {"id": sid_str, "name": nick}
                    st.rerun()
        st.stop()

    st.markdown(f"<h1>SYSTEM HUB // <span style='color:#bc8cff;'>{st.session_state.user['name'].upper()}</span></h1>", unsafe_allow_html=True)

    try:
        all_data = conn.read(ttl=0).dropna(how='all')
        all_data.columns = all_data.columns.str.strip().str.lower()
        
        # FIXED: Robust filtering to handle '1', 'TRUE', 'true', etc.
        def check_active(val):
            v = str(val).strip().upper()
            return v in ['TRUE', '1', 'YES', 'ACTIVE']

        active_df = all_data[all_data['is_active'].apply(check_active)].copy().reset_index(drop=True)

        if len(active_df) < 2:
            st.info("📡 Scanning... No other active nodes found in the spreadsheet.")
        else:
            # KNN Processing
            active_df['int_list'] = active_df['interests'].astype(str).str.lower().apply(lambda x: [i.strip() for i in x.split(',') if i.strip()])
            mlb = MultiLabelBinarizer()
            feats = mlb.fit_transform(active_df['int_list'])
            knn = NearestNeighbors(n_neighbors=len(active_df), metric='jaccard').fit(feats)
            
            user_idx = active_df[active_df['student_id'].astype(str) == str(st.session_state.user['id'])].index[0]
            dists, inds = knn.kneighbors([feats[user_idx]])

            st.markdown("### RECOMMENDED PEERS")
            cols = st.columns(3)
            for i, n_idx in enumerate(inds[0][1:]):
                peer = active_df.iloc[n_idx]
                score = int((1 - dists[0][i+1]) * 100)
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class='node-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <b style='color:#00f2fe; font-size:1.2rem;'>{str(peer['name']).upper()}</b>
                                <span class='match-percent'>{score}%</span>
                            </div>
                            <p style='color:#8b949e; font-size:0.7rem;'>ID: {peer['student_id']}</p>
                            <div>{"".join([f"<span class='badge'>{t.upper()}</span>" for t in peer['int_list']])}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"LINK: {str(peer['name']).upper()}", key=f"l_{peer['student_id']}"):
                        st.session_state.linked_peer = peer['name']
                        st.session_state.page = 'success'
                        st.rerun()
    except Exception as e:
        st.error(f"System Check Required: {e}")

elif st.session_state.page == 'success':
    st.markdown(f"## SUCCESS: LINKED WITH {st.session_state.linked_peer.upper()}")
    if st.button("RETURN"):
        st.session_state.page = 'hub'; st.rerun()