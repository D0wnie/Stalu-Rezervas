import streamlit as st
import json
import os
from datetime import datetime, timedelta

# =========================================
# CONFIG
# =========================================

ADMIN_USER = "admin"
ADMIN_PASS = "slaptas123"

USERS_FILE = "users.json"
RESERV_FILE = "reservations.json"

# =========================================
# 🎄 DIZAINAS
# =========================================

st.markdown("""
<style>

body { background-color: #0b0f17; }
.header {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    color: #ffcccc;
    padding: 10px;
    margin-bottom: 20px;
    text-shadow: 0 0 10px #ff4d4d;
}
.box {
    background: rgba(255, 220, 220, 0.1);
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #ffb3b3;
    box-shadow: 0 0 15px rgba(255,100,100,0.15);
    margin-bottom: 20px;
}
.stTextInput>div>div>input {
    background-color: #1a1f2c; color: white;
    border: 1px solid #ffb3b3; border-radius: 10px;
}
.stSelectbox>div>div>select {
    background-color: #1e2533; color: white;
    border-radius: 8px; border: 1px solid #ffb3b3;
}
.stButton>button {
    background-color: #b30000 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 2px solid #660000 !important;
    transition: 0.2s;
}
.stButton>button:hover {
    background-color: #ff1a1a !important;
    box-shadow: 0 0 10px #ff3333;
}
.reslist {
    background: rgba(255, 230, 230, 0.05);
    padding: 10px;
    border-radius: 10px;
    border-left: 3px solid #ff9999;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>🎄 Stalo futbolo staliukų rezervavimo sistema 🎁</div>", unsafe_allow_html=True)

# =========================================
# DATA LOAD/SAVE
# =========================================

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

users = load_json(USERS_FILE)
reservations = load_json(RESERV_FILE)

# =========================================
# SESSION STATE
# =========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================================
# LOGIN / REGISTER LOGIC
# =========================================

def login(username, password):
    if username == ADMIN_USER and password == ADMIN_PASS:
        st.session_state.logged_in = True
        st.session_state.current_user = "ADMIN"
        st.session_state.is_admin = True
        return True

    if username in users and users[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.session_state.is_admin = False
        return True

    return False


def register(username, password, surname, clazz):
    if username in users:
        return False  # already exists

    users[username] = {
        "password": password,
        "surname": surname,
        "class": clazz
    }
    save_json(USERS_FILE, users)
    return True

# =========================================
# LOGIN / REGISTER SCREEN
# =========================================

if not st.session_state.logged_in:

    st.title("🔑 Stalo Futbolo Rezervacija")

    mode = st.radio("Pasirinkite:", ["Prisijungti", "Registruotis"])

    if mode == "Prisijungti":
        username = st.text_input("Vardas")
        password = st.text_input("Slaptažodis", type="password")

        if st.button("Prisijungti"):
            if login(username, password):
                st.success("Prisijungta!")
                st.rerun()
            else:
                st.error("Neteisingi duomenys.")

    if mode == "Registruotis":
        username = st.text_input("Vardas (bus tavo prisijungimo vardas)")
        surname = st.text_input("Pavardė")
        clazz = st.text_input("Klasė (pvz: 8c)")
        password = st.text_input("Slaptažodis", type="password")

        if st.button("Sukurti paskyrą"):
            if not username or not surname or not clazz or not password:
                st.error("Užpildyk visus laukus!")
            elif register(username, password, surname, clazz):
                st.success("Paskyra sukurta! Dabar prisijunk 🔑")
            else:
                st.error("Toks vartotojas jau egzistuoja.")

    st.stop()

# =========================================
# MAIN SYSTEM
# =========================================

st.title("⚽ Stalo Futbolo Staliukų Rezervacija")
st.write(f"Sveikas, **{st.session_state.current_user}**!")

today = datetime.today()
dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]
breaks = ["1", "2", "3", "4", "5", "6", "7"]

# USER DATA
if not st.session_state.is_admin:
    user_data = users[st.session_state.current_user]
    user_name = st.session_state.current_user
    user_surname = user_data["surname"]
    user_class = user_data["class"]
else:
    user_name = "ADMIN"
    user_surname = ""
    user_class = ""

# =========================================
# RESERVATION PANEL
# =========================================

st.subheader("📅 Nauja rezervacija")

date = st.selectbox("Pasirinkite datą", dates)
break_num = st.selectbox("Pasirinkite pertrauką", breaks)

if st.button("Rezervuoti"):
    if date not in reservations:
        reservations[date] = {}

    if break_num not in reservations[date]:
        reservations[date][break_num] = []

    # limit 2 reservations per break
    if len(reservations[date][break_num]) >= 2:
        st.error("❌ Ši pertrauka užimta (2/2).")
    else:
        entry = {
            "name": user_name,
            "surname": user_surname,
            "class": user_class
        }
        reservations[date][break_num].append(entry)
        save_json(RESERV_FILE, reservations)
        st.success("Rezervuota!")

# =========================================
# DELETE RESERVATION
# =========================================

st.subheader("🗑️ Ištrinti rezervaciją")

del_date = st.selectbox("Data", dates, key="ddd")
del_break = st.selectbox("Pertrauka", breaks, key="dbb")

people = []
if del_date in reservations and del_break in reservations[del_date]:
    people = reservations[del_date][del_break]

if people:
    names_list = [f"{p['name']} {p['surname']} ({p['class']})" for p in people]
else:
    names_list = ["-"]

selected = st.selectbox("Ką ištrinti", names_list)

if st.button("Ištrinti"):
    if selected == "-":
        st.error("Nėra ką ištrinti.")
    else:
        idx = names_list.index(selected)
        res = people[idx]

        if st.session_state.is_admin or res["name"] == user_name:
            del reservations[del_date][del_break][idx]
            save_json(RESERV_FILE, reservations)
            st.success("Ištrinta.")
        else:
            st.error("Negalite ištrinti kito žmogaus rezervacijos.")

# =========================================
# LOGOUT
# =========================================

if st.button("Atsijungti"):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False
    st.rerun()
