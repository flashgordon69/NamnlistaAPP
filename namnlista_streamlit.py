import streamlit as st
import pandas as pd

st.set_page_config(page_title="Namnlista", page_icon="✅", layout="centered")

st.title("Namnlista")
st.write("Pricka av närvarande studenter för ett event.")

if "created" not in st.session_state:
    st.session_state.created = False
if "students" not in st.session_state:
    st.session_state.students = []
if "attendance" not in st.session_state:
    st.session_state.attendance = {}
if "event_name" not in st.session_state:
    st.session_state.event_name = ""

st.subheader("1. Skapa namnlista")
event_name = st.text_input("Event name", value=st.session_state.event_name)
names_input = st.text_area(
    "Studentnamn (ett namn per rad)",
    placeholder="Anna Andersson\nBjörn Berg\nClara Carlsson"
)

if st.button("Skapa lista", use_container_width=True):
    students = [name.strip() for name in names_input.splitlines() if name.strip()]

    if not event_name.strip():
        st.error("Du måste skriva ett Event name.")
    elif not students:
        st.error("Du måste skriva minst ett studentnamn.")
    else:
        st.session_state.created = True
        st.session_state.event_name = event_name.strip()
        st.session_state.students = students
        st.session_state.attendance = {name: False for name in students}
        st.success("Namnlistan är skapad.")

if st.session_state.created:
    st.divider()
    st.subheader(f"2. Närvaro – {st.session_state.event_name}")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Namn**")
    with col2:
        st.markdown("**Närvarande**")

    for student in st.session_state.students:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(student)
        with c2:
            st.session_state.attendance[student] = st.checkbox(
                "",
                value=st.session_state.attendance.get(student, False),
                key=f"attend_{student}"
            )

    st.divider()

    present = [name for name, checked in st.session_state.attendance.items() if checked]
    absent = [name for name, checked in st.session_state.attendance.items() if not checked]

    total_students = len(st.session_state.students)

    c1, c2, c3 = st.columns(3)
    c1.metric("Totalt", total_students)
    c2.metric("Närvarande", len(present))
    c3.metric("Frånvarande", len(absent))

    result_df = pd.DataFrame({
        "Event name": [st.session_state.event_name] * total_students,
        "Namn": st.session_state.students,
        "Närvarande": [st.session_state.attendance[name] for name in st.session_state.students]
    })

    st.dataframe(result_df, use_container_width=True, hide_index=True)

    csv_data = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Ladda ner CSV-fil",
        data=csv_data,
        file_name=f"namnlista_{st.session_state.event_name.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    if present:
        st.markdown("**Närvarande:**")
        st.write("\n".join(present))

    if absent:
        st.markdown("**Frånvarande:**")
        st.write("\n".join(absent))

    if st.button("Börja om", use_container_width=True):
        st.session_state.created = False
        st.session_state.students = []
        st.session_state.attendance = {}
        st.session_state.event_name = ""
        st.rerun()