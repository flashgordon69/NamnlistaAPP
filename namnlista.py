import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Namnlista",
    page_icon="✅",
    layout="centered"
)

# =========================
# Läs studentlista
# =========================
students_filename = "NamnlistaToApp.csv"
event_filename = "EventNameToApp.csv"

if not os.path.exists(students_filename):
    st.error(f"Filen {students_filename} hittades inte.")
    st.stop()

if not os.path.exists(event_filename):
    st.error(f"Filen {event_filename} hittades inte.")
    st.stop()

try:
    df_students = pd.read_csv(students_filename, encoding="utf-8-sig")
    df_students.columns = df_students.columns.str.strip()
except Exception as e:
    st.error(f"Kunde inte läsa {students_filename}: {e}")
    st.stop()

try:
    df_event = pd.read_csv(event_filename, encoding="utf-8-sig")
    df_event.columns = df_event.columns.str.strip()
except Exception as e:
    st.error(f"Kunde inte läsa {event_filename}: {e}")
    st.stop()

if "Namn" not in df_students.columns:
    st.error("Kolumnen 'Namn' saknas i NamnlistaToApp.csv.")
    st.stop()

if "Event name" not in df_event.columns:
    st.error("Kolumnen 'Event name' saknas i EventNameToApp.csv.")
    st.stop()

students = (
    df_students["Namn"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)

if not students:
    st.error("Inga studentnamn hittades.")
    st.stop()

event_name = (
    df_event["Event name"]
    .dropna()
    .astype(str)
    .str.strip()
    .iloc[0]
)

# =========================
# Session state
# =========================
if "attendance" not in st.session_state:
    st.session_state.attendance = {name: False for name in students}

# Synka om studentlistan ändras
for name in students:
    if name not in st.session_state.attendance:
        st.session_state.attendance[name] = False

st.session_state.attendance = {
    name: st.session_state.attendance.get(name, False)
    for name in students
}

# =========================
# CSS
# =========================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 2rem;
        max-width: 650px;
    }

    div[data-testid="stButton"] > button {
        width: 100%;
        text-align: left;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        border: 1px solid #d9d9d9;
        background: white;
        color: #222;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.3;
        margin-bottom: 0.45rem;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: #00a84f;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Rubriker
# =========================
st.title("Namnlista")
st.write("Tryck på en rad för att markera eller avmarkera närvaro.")

st.subheader("1. Event")
st.write(event_name)

st.subheader("2. Närvaro")

# =========================
# Klickbara rader
# =========================
for student in students:
    checked = st.session_state.attendance[student]
    symbol = "🟢" if checked else "⚪"
    text = f"{symbol}  {student}"

    if st.button(text, key=f"row_{student}", use_container_width=True):
        st.session_state.attendance[student] = not st.session_state.attendance[student]
        st.rerun()

st.divider()

# =========================
# Statistik
# =========================
present = [
    name for name, checked in st.session_state.attendance.items()
    if checked
]

absent = [
    name for name, checked in st.session_state.attendance.items()
    if not checked
]

c1, c2, c3 = st.columns(3)
c1.metric("Totalt", len(students))
c2.metric("Närvarande", len(present))
c3.metric("Frånvarande", len(absent))

# =========================
# Sammanställning
# =========================
st.subheader("3. Sammanställning")

result_df = pd.DataFrame({
    "Event name": [event_name] * len(students),
    "Namn": students,
    "Närvarande": [st.session_state.attendance[name] for name in students]
})

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)

# =========================
# Listor
# =========================
if present:
    st.markdown("**Närvarande:**")
    st.write("\n".join(present))
else:
    st.info("Ingen är markerad som närvarande ännu.")

if absent:
    st.markdown("**Frånvarande:**")
    st.write("\n".join(absent))

# =========================
# Ladda ner CSV
# =========================
csv_data = result_df.to_csv(index=False).encode("utf-8-sig")

safe_event_name = event_name.replace(" ", "_").replace("/", "-")

st.download_button(
    label="Ladda ner CSV-fil",
    data=csv_data,
    file_name=f"namnlista_{safe_event_name}.csv",
    mime="text/csv",
    use_container_width=True
)

# =========================
# Nollställ
# =========================
if st.button("Nollställ närvaro", use_container_width=True):
    st.session_state.attendance = {name: False for name in students}
    st.rerun()