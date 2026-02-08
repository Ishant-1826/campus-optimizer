import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
import socket
import threading
import time
from p2p_manager import P2PNode
from bluetooth_manager import BluetoothNode
import requests
import json

# FIREBASE CONFIG
FIREBASE_URL = "https://reschedule-b3620-default-rtdb.firebaseio.com"

# HELPER: Firebase Operations
def get_firebase_data():
    try:
        response = requests.get(f"{FIREBASE_URL}/users.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                # Convert dict of dicts to list of dicts
                users_list = []
                for key, val in data.items():
                    if isinstance(val, dict):
                        users_list.append(val)
                return pd.DataFrame(users_list)
        return pd.DataFrame(columns=["student_id", "name", "interests", "is_active"])
    except Exception as e:
        return pd.DataFrame(columns=["student_id", "name", "interests", "is_active"])

def update_user_firebase(user_data):
    try:
        sid = user_data.get("student_id")
        if not sid: return False
        requests.put(f"{FIREBASE_URL}/users/{sid}.json", json=user_data, timeout=10)
        return True
    except Exception as e:
        return False


# HELPER: Check Online Status
def check_online():
    try:
        # Try a quick connection to a public DNS
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

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
# 3. DATABASE CONNECTION (Replaced by Firebase)
# conn = st.connection("gsheets", type=GSheetsConnection) 


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
                        # df = conn.read(ttl=0) - REPLACED
                        df = get_firebase_data()
                        
                        if not df.empty:
                            df.columns = df.columns.str.strip().str.lower()
                        
                        sid_str = str(sid).strip()
                        interest_str = ", ".join(interests)
                        
                        # Prepare User Data
                        user_data = {
                            "student_id": sid_str, 
                            "name": nick, 
                            "is_active": "TRUE", 
                            "interests": interest_str
                        }
                        
                        # Update Firebase directly (No need to manipulate full DF and rewrite)
                        if update_user_firebase(user_data):
                            st.cache_data.clear()
                            st.session_state.user = {"id": sid_str, "name": nick, "interests": interests}
                            st.rerun()
                        else:
                            st.error("Connection Failed: Could not update Firebase.")
                            
                    except Exception as e:
                        st.error(f"Write Error: {e}")

        st.stop()

    # --- P2P INITIALIZATION (BACKGROUND) ---
    user = st.session_state.user
    
    # Check connectivity ONCE per run or on demand
    if 'is_online' not in st.session_state:
        st.session_state.is_online = check_online()

    # Initialize P2P Node if Offline (or Hybrid)
    if not st.session_state.is_online:
        if 'p2p_node' not in st.session_state:
            # Format interests for P2P
            # If user comes from GSheets cache, interests might be a string. 
            # If fresh, it might be a list. Normalize.
            # For simplicity in this edit, we assume 'user' dict has basic info.
            # We might need to fetch interests if not present.
            
            # Let's try to get interests from session state if available, or default
            p2p_interests = user.get('interests', [])
            
            try:
                st.session_state.p2p_node = P2PNode(
                    user_id=user['id'], 
                    user_name=user['name'], 
                    interests=p2p_interests
                )
                st.session_state.p2p_node.start()
            except Exception as e:
                st.error(f"P2P Init Failed: {e}")



    # --- BLUETOOTH INITIALIZATION ---
    # Auto-enable if offline, or respect user toggle
    default_bt = not st.session_state.is_online
    enable_bt = st.sidebar.checkbox("Enable Bluetooth Discovery", value=default_bt)
    
    if enable_bt:
        if 'bt_node' not in st.session_state:
             try:
                 st.session_state.bt_node = BluetoothNode(
                     user_id=user['id'], 
                     user_name=user['name'], 
                     interests=str(user.get('interests', []))
                 )
                 st.session_state.bt_node.start()
                 st.toast("Bluetooth Node Started")
             except Exception as e:
                 st.error(f"Bluetooth Init Failed: {e}")
    else:
        if 'bt_node' in st.session_state:
            st.session_state.bt_node.stop()
            del st.session_state.bt_node

    # --- MAIN INTERFACE BLOCK ---
    
    # HUD Header
    status_color = "#00f2fe" if st.session_state.is_online else "#ff4b4b"
    if st.session_state.is_online:
        status_text = "ONLINE"
    else:
        status_text = "OFFLINE / P2P + BLUETOOTH MODE" if enable_bt else "OFFLINE / P2P MODE"
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <h1>SYSTEM HUB // <span style='color:#bc8cff;'>{user['name'].upper()}</span></h1>
            <div style='border: 1px solid {status_color}; color: {status_color}; padding: 5px 15px; border-radius: 20px; font-family: "JetBrains Mono";'>
                ● {status_text}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # REFRESH / SCAN BUTTON
    btn_label = "🔄 SYNCHRONIZE ACTIVE NODES" if st.session_state.is_online else "📡 SCAN FOR LOCAL PEERS"
    if st.button(btn_label):
        if st.session_state.is_online:
            st.cache_data.clear()
        else:
            # Force UI refresh for P2P
            pass 
        st.rerun()

    try:
        active_df = pd.DataFrame()
        
        if st.session_state.is_online:
            # --- ONLINE MODE: FIREBASE ---
            # all_data = conn.read(ttl=0) - REPLACED
            all_data = get_firebase_data()
            
            if not all_data.empty:
                all_data.columns = all_data.columns.str.strip().str.lower()
                
                # Cleanup Column D for UI and Logic (Handle potential missing columns in empty db)
                if 'is_active' in all_data.columns:
                    all_data['is_active'] = all_data['is_active'].astype(str).str.strip().str.upper()
                    all_data['is_active'] = all_data['is_active'].replace({'1': 'TRUE', '0': 'FALSE', '1.0': 'TRUE', '0.0': 'FALSE'})
                    active_df = all_data[all_data['is_active'] == "TRUE"].copy().reset_index(drop=True)
                else:
                    active_df = pd.DataFrame()
            else:
                 active_df = pd.DataFrame()
        
        # MERGED PEER LIST LOGIC
        else:
            # ... (Peer discovery logic maintained) ...
            
            # --- OFFLINE MODE: PEER DISCOVERY (Wi-Fi + Bluetooth) ---
            peer_rows = []
            
            # 1. Wi-Fi P2P Peers
            if 'p2p_node' in st.session_state:
                p2p_peers = st.session_state.p2p_node.get_active_peers()
                for p in p2p_peers:
                    ints = p.get('interests', [])
                    if isinstance(ints, str): ints = [ints]
                    peer_rows.append({
                        "student_id": p['id'],
                        "name": p['name'],
                        "interests": ",".join(ints),
                        "ip": p['ip'],
                        "port": p['port'],
                        "type": "WIFI",
                        "is_active": "TRUE"
                    })
                    
            # 2. Bluetooth Peers
            if 'bt_node' in st.session_state:
                bt_peers = st.session_state.bt_node.get_active_peers()
                for p in bt_peers:
                    ints = p.get('interests', [])
                    if isinstance(ints, str): ints = [ints]
                    elif isinstance(ints, list): ints = ints
                    
                    peer_rows.append({
                        "student_id": p['id'],
                        "name": p['name'],
                        "interests": ",".join(ints),
                        "ip": "BLUETOOTH",
                        "port": p['port'], 
                        "type": "BT",
                        "is_active": "TRUE"
                    })

            if peer_rows:
                active_df = pd.DataFrame(peer_rows)
            else:
                active_df = pd.DataFrame()

            # --- MESSAGE HANDLING & NOTIFICATIONS ---
            msgs = []
            if 'p2p_node' in st.session_state:
                msgs.extend(st.session_state.p2p_node.get_latest_messages())
            if 'bt_node' in st.session_state:
                msgs.extend(st.session_state.bt_node.get_latest_messages())
            
            # Initialize Notification Storage
            if 'notifications' not in st.session_state:
                st.session_state.notifications = []

            for m in msgs:
                if m.get("type") == "LINK_REQUEST":
                    # Add to notifications list
                    notif = {
                        "from_name": m.get("from_name", "Unknown"),
                        "from_id": m.get("from_id", "Unknown"),
                        "time": time.time(),
                        "msg": "wants to link with you!"
                    }
                    st.session_state.notifications.append(notif)
                    st.toast(f"New Link Request from {notif['from_name']}")
                else:
                    st.toast(f"Message: {m}")

        # --- NOTIFICATION CENTER ---
        if 'notifications' in st.session_state and st.session_state.notifications:
            with st.sidebar:
                st.markdown("### 🔔 NOTIFICATIONS")
                for i, notif in enumerate(st.session_state.notifications):
                    st.info(f"**{notif['from_name']}** {notif['msg']}")
                    # Future: Add Accept/Decline here
                    if st.button("Dismiss", key=f"dismiss_{i}"):
                        st.session_state.notifications.pop(i)
                        st.rerun()

        if active_df.empty or len(active_df) < (2 if st.session_state.is_online else 1):
             st.info("📡 SCANNING... No other active nodes detected.")
        else:
            # KNN Logic (Simplified for brevity as we focus on offline)
            
            active_df['interests_clean'] = active_df['interests'].astype(str).str.lower().apply(
                lambda x: [i.strip() for i in x.split(',') if i.strip()]
            )
            
            curr_sid = str(user['id'])
            # (KNN logic skipped for brevity, showing all peers)
            peer_indices = active_df.index
            
            st.markdown(f"### 🎯 RECOMMENDED PEER NODES")
            cols = st.columns(3)
            count = 0
            
            for i, neighbor_idx in enumerate(peer_indices):
                if neighbor_idx >= len(active_df): continue 
                peer_row = active_df.iloc[neighbor_idx]
                if str(peer_row['student_id']) == curr_sid: continue
                
                display_tags = [t.upper() for t in peer_row['interests_clean']]
                badges_html = "".join([f"<span class='badge'>{x}</span>" for x in display_tags])
                
                # Determine Badge Type
                node_type = peer_row.get('type', 'LOCAL')
                if node_type == 'BT':
                    type_badge = "<span style='color: #00f2fe; font-weight:bold;'>BLUETOOTH</span>"
                elif node_type == 'WIFI':
                     type_badge = "<span style='color: #bc8cff; font-weight:bold;'>WI-FI LAN</span>"
                else:
                    type_badge = "<span style='color: #bc8cff; font-weight:bold;'>LOCAL</span>"

                with cols[count % 3]:
                    st.markdown(f"""
                        <div class='node-card'>
                            <div style='display: flex; justify-content: space-between;'>
                                <b style='color:#00f2fe; font-size:1.4rem;'>{peer_row['name']}</b>
                                {type_badge}
                            </div>
                            <p style='color:#8b949e; font-size:0.8rem; margin:10px 0;'>ID: {peer_row['student_id']}</p>
                            <div style='margin-bottom:20px;'>{badges_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Link Button with Feedback
                    btn_key = f"btn_{peer_row['student_id']}"
                    if st.button(f"LINK WITH {peer_row['name'].upper()}", key=btn_key):
                        
                        # --- P2P HANDSHAKE ---
                        msg = {
                             "type": "LINK_REQUEST",
                             "from_id": user['id'],
                             "from_name": user['name']
                         }
                         
                        success = False
                        if not st.session_state.is_online:
                            if node_type == 'BT' and 'bt_node' in st.session_state:
                                 target_mac = peer_row['student_id'] 
                                 st.session_state.bt_node.send_direct_message(target_mac, msg)
                                 success = True
                            elif 'p2p_node' in st.session_state:
                                 target_ip = peer_row['ip']
                                 target_port = int(peer_row['port'])
                                 st.session_state.p2p_node.send_direct_message(target_ip, target_port, msg)
                                 success = True
                        
                        if success:
                            st.toast(f"Request sent to {peer_row['name']}!", icon="📨")
                        else:
                            st.error("Failed to send request.")
                count += 1

    except Exception as e:
        st.error(f"System Error: {e}")

    with st.sidebar:
        st.markdown("### 🛠 DIAGNOSTICS")
        if st.checkbox("Show Network Data (Internal View)"):
            st.dataframe(all_data)
        if st.button("TERMINATE CONNECTION"):
            st.cache_data.clear()
            # Update just this user to Inactive in Firebase
            user_data = {
                "student_id": user['id'],
                "name": user['name'], # Keep name
                "is_active": "FALSE",
                "interests": ",".join(user.get('interests', []))
            }
            update_user_firebase(user_data)
            
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