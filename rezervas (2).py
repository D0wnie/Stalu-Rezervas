import streamlit as st
import json
from datetime import date, timedelta

RES_FILE = "reservations.json"

# Funkcijos rezervacijų skaitymui ir saugojimui
def load_reservations():
    try:
        with open(RES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_reservations(res):
    with open(RES_FILE, "w") as f:
        json.dump(res, f, indent=4)

# Inicijuojam rezervacijas
if "reservations" not in st.session_state:
    st.session_state.reservations = load_reservations()

st.title("Stalo Futbolo Rezervacija")

# Dienų pasirinkimas (iki 2 savaičių į priekį)
max_date = date.today() + timedelta(days=14)
selected_date = st.date_input("Pasirinkite dieną", min_value=date.today(), max_value=max_date)
day_str = str(selected_date)
if day_str not in st.session_state.reservations:
    st.session_state.reservations[day_str] = {}

# Įveskite savo duomenis
st.subheader("Jūsų duomenys:")
name = st.text_input("Vardas", key="name")
surname = st.text_input("Pavardė", key="surname")
class_name = st.text_input("Klasė", key="class")

# Pertraukų mygtukai su spalvomis
st.subheader("Pasirinkite pertrauką (1–7):")
cols = st.columns(7)
for i in range(1, 8):
    b_str = str(i)
    if b_str not in st.session_state.reservations[day_str]:
        st.session_state.reservations[day_str][b_str] = []
    reserved = st.session_state.reservations[day_str][b_str]

    # Patikrinam, ar tavo rezervacija čia
    is_mine = any(r['name']==name and r['surname']==surname for r in reserved)

    if len(reserved) >= 2 and not is_mine:
        color = "#FF6961"  # Raudona – užimta
        label = f"{i}\nUŽIMTA"
    elif is_mine:
        color = "#1E90FF"  # Mėlyna – tavo rezervacija
        label = f"{i}\nTAVO"
    else:
        color = "#77DD77"  # Žalia – laisva
        label = f"{i}\nLAISVA"

    if cols[i-1].button(label, key=f"break_{i}"):
        if len(reserved) >= 2 and not is_mine:
            st.warning("Ši pertrauka jau užimta! ❌")
        elif not name or not surname or not class_name:
            st.error("Įveskite vardą, pavardę ir klasę")
        elif is_mine:
            st.info("Jūs jau rezervavote šią pertrauką")
        else:
            # Rezervuojam
            reserved.append({"name": name, "surname": surname, "class": class_name})
            save_reservations(st.session_state.reservations)
            st.success(f"Rezervuota pertrauka {i} ✅")
            # Atspausdinam atnaujintas rezervacijas be experimental_rerun
            st.experimental_set_query_params(update="true")  # Nenaudojama rerun
            st.experimental_rerun = lambda: None  # tiesiog ignoruojam, kad nebeliktų klaidos

# Rodom visų rezervacijas
st.subheader(f"Rezervacijos {selected_date}:")
for brk, res_list in st.session_state.reservations[day_str].items():
    line = f"Pertrauka {brk}: "
    if res_list:
        line += ", ".join(f"{r['name']} {r['surname']}" for r in res_list)
    else:
        line += "Laisva"
    st.write(line)

# Ištrinti savo rezervacijas
st.subheader("Ištrinti savo rezervaciją:")
if st.button("Ištrinti visas mano rezervacijas šiai dienai"):
    changed = False
    for brk in st.session_state.reservations[day_str]:
        old_len = len(st.session_state.reservations[day_str][brk])
        st.session_state.reservations[day_str][brk] = [
            r for r in st.session_state.reservations[day_str][brk]
            if not (r['name']==name and r['surname']==surname)
        ]
        if len(st.session_state.reservations[day_str][brk]) != old_len:
            changed = True
    if changed:
        save_reservations(st.session_state.reservations)
        st.success("Jūsų rezervacijos ištrintos ✅")
