import streamlit as st
import json
import os
from datetime import datetime, timedelta

# =========================================
# 🔐 LOGIN SISTEMA
# =========================================

ADMIN_USER = "admin"
ADMIN_PASS = "slaptas123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


def login(username, password):
    if username == ADMIN_USER and password == ADMIN_PASS:
        st.session_state.logged_in = True
        st.session_state.is_admin = True
    else:
        st.session_state.logged_in = True
        st.session_state.is_admin = False


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

st.markdown("<div class='header'>🎄 Kalėdinė Rezervacijų Sistema 🎁</div>", unsafe_allow_html=True)

# =========================================
# 📁 DUOMENYS
# =========================================

FILE = "reservations.json"


def load_data():
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


data = load_data()

# =========================================
# 🔑 LOGIN
# =========================================

if not st.session_state.logged_in:
    st.markdown("### 🔐 Prisijungimas (nebūtinas, bet suteikia admin teises)")

    username = st.text_input("Vartotojas")
    password = st.text_input("Slaptažodis", type="password")

    if st.button("Prisijungti"):
        login(username, password)
        st.rerun()

    st.stop()

# =========================================
# ADMIN ŽENKLAS
# =========================================

if st.session_state.is_admin:
    st.success("🔑 Prisijungta kaip **Administratorius**")
else:
    st.info("👤 Prisijungta kaip paprastas vartotojas")

# =========================================
# DATOS
# =========================================

today = datetime.today()
dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]
breaks = ["1", "2", "3", "4", "5", "6", "7"]

# =========================================
# REZERVACIJA
# =========================================

st.markdown('<div class="box">', unsafe_allow_html=True)

date = st.selectbox("📅 Pasirinkite rezervacijos datą", dates)
name = st.text_input("🎁 Vardas")
surname = st.text_input("🎄 Pavardė")
clazz = st.text_input("⛄ Klasė (pvz: 8c)")
break_num = st.selectbox("🔔 Pasirinkite pertrauką", breaks)

st.markdown('</div>', unsafe_allow_html=True)

if st.button("🎄 Rezervuoti"):
    if not name or not surname or not clazz:
        st.error("❌ Užpildyk visus laukus!")
    else:
        if date not in data:
            data[date] = {}

        if break_num not in data[date]:
            data[date][break_num] = []

        if len(data[date][break_num]) >= 2:
            st.error("❌ Ši pertrauka jau užimta: 2/2 vietos!")
        else:
            entry = {"name": name, "surname": surname, "class": clazz}
            data[date][break_num].append(entry)
            save_data(data)
            st.success("🎉 Sėkmingai rezervuota!")

# =========================================
# IŠTRINTI
# =========================================

st.markdown("## 🗑️ Ištrinti rezervaciją")

del_date = st.selectbox("📆 Pasirinkite datą", dates, key="dd")
del_break = st.selectbox("🔔 Pasirinkite pertrauką", breaks, key="db")

people = []
if del_date in data and del_break in data[del_date]:
    people = data[del_date][del_break]

if people:
    names_list = [f"{p['name']} {p['surname']} ({p['class']})" for p in people]
else:
    names_list = ["-"]

selected = st.selectbox("👤 Pasirinkite ką ištrinti", names_list)

if st.button("❌ Ištrinti"):
    if selected == "-":
        st.error("⚠️ Nėra ką ištrinti.")
    else:
        index = names_list.index(selected)

        if st.session_state.is_admin:
            del data[del_date][del_break][index]
            save_data(data)
            st.success("🗑️ Administratorius sėkmingai ištrynė rezervaciją!")
        else:
            target = people[index]
            if target["name"] == name and target["surname"] == surname and target["class"] == clazz:
                del data[del_date][del_break][index]
                save_data(data)
                st.success("🗑️ Sėkmingai ištrinta jūsų rezervacija!")
            else:
                st.error("🚫 Negalite ištrinti kito žmogaus rezervacijos!")
