import streamlit as st
import psycopg2
from psycopg2 import extras

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🤝 Client Engagements")

conn = get_connection()
cur = conn.cursor(cursor_factory=extras.DictCursor)

# DYNAMIC DROPDOWNS: Options pulled from DB (Rubric Requirement)
cur.execute("SELECT id, company_name FROM clients")
client_map = {row[1]: row[0] for row in cur.fetchall()}
cur.execute("SELECT id, service_name FROM services")
service_map = {row[1]: row[0] for row in cur.fetchall()}

# CREATE ENGAGEMENT
with st.form("new_engagement"):
    c = st.selectbox("Client", options=list(client_map.keys()))
    s = st.selectbox("Service", options=list(service_map.keys()))
    budget = st.number_input("Budget", min_value=0)
    start = st.date_input("Start Date")
    if st.form_submit_button("Link Service"):
        cur.execute("INSERT INTO engagements (client_id, service_id, monthly_spend, start_date) VALUES (%s, %s, %s, %s)",
                    (client_map[c], service_map[s], budget, start))
        conn.commit()
        st.rerun()

st.divider()

# READ, UPDATE, & DELETE
cur.execute("""
    SELECT e.id, c.company_name, s.service_name, e.monthly_spend 
    FROM engagements e 
    JOIN clients c ON e.client_id = c.id 
    JOIN services s ON e.service_id = s.id
""")
engs = cur.fetchall()

for eng in engs:
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.write(f"{eng[1]} - {eng[2]} (${eng[3]})")
    
    # UPDATE: Pre-populated edit form (Rubric Requirement)
    if col2.button("Edit", key=f"edit_{eng[0]}"):
        st.session_state[f"editing_{eng[0]}"] = True
    
    if st.session_state.get(f"editing_{eng[0]}", False):
        with st.form(f"f_{eng[0]}"):
            new_spend = st.number_input("New Budget", value=float(eng[3]))
            if st.form_submit_button("Save"):
                cur.execute("UPDATE engagements SET monthly_spend = %s WHERE id = %s", (new_spend, eng[0]))
                conn.commit()
                st.session_state[f"editing_{eng[0]}"] = False
                st.rerun()

    # DELETE: Confirmation step (Rubric Requirement)
    if col3.button("Delete", key=f"del_{eng[0]}"):
        st.session_state[f"confirm_{eng[0]}"] = True

    if st.session_state.get(f"confirm_{eng[0]}", False):
        st.warning("Delete this record?")
        if st.button("Confirm", key=f"y_{eng[0]}"):
            cur.execute("DELETE FROM engagements WHERE id = %s", (eng[0],))
            conn.commit()
            st.rerun()
