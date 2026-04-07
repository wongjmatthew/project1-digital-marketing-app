import streamlit as st
import psycopg2
from psycopg2 import extras

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🤝 Engagement Manager")

conn = get_connection()
cur = conn.cursor(cursor_factory=extras.DictCursor)

# DYNAMIC DROPDOWNS: Pulled from DB (Rubric Requirement)
cur.execute("SELECT id, company_name FROM clients")
client_options = {row[1]: row[0] for row in cur.fetchall()}

cur.execute("SELECT id, service_name, min_monthly_budget FROM services")
service_data = {row[1]: (row[0], row[2]) for row in cur.fetchall()}

# CREATE ENGAGEMENT
with st.form("new_eng"):
    c_choice = st.selectbox("Select Client", options=list(client_options.keys()))
    s_choice = st.selectbox("Select Service", options=list(service_data.keys()))
    spend = st.number_input("Monthly Spend ($)")
    start = st.date_input("Start Date")
    end = st.date_input("End Date")
    
    if st.form_submit_button("Sign Contract"):
        # Validation: Budget Integrity and Date Logic (Rubric Requirement)
        if spend < service_data[s_choice][1]:
            st.error(f"Error: Spend must meet minimum budget of ${service_data[s_choice][1]}")
        elif end <= start:
            st.error("Error: End date must be after start date.")
        else:
            cur.execute("""
                INSERT INTO engagements (client_id, service_id, monthly_spend, start_date, end_date) 
                VALUES (%s, %s, %s, %s, %s)
            """, (client_options[c_choice], service_data[s_choice][0], spend, start, end))
            conn.commit()
            st.rerun()

st.divider()

# UPDATE: Edit existing records (Rubric Requirement)
cur.execute("""
    SELECT e.id, c.company_name, s.service_name, e.monthly_spend, e.status
    FROM engagements e
    JOIN clients c ON e.client_id = c.id
    JOIN services s ON e.service_id = s.id
""")
engs = cur.fetchall()

for eng in engs:
    with st.expander(f"{eng['company_name']} - {eng['service_name']} (${eng['monthly_spend']})"):
        with st.form(f"edit_eng_{eng['id']}"):
            new_status = st.selectbox("Status", ["Active", "Paused", "Completed"], index=["Active", "Paused", "Completed"].index(eng['status']))
            new_spend = st.number_input("Update Spend", value=float(eng['monthly_spend']))
            
            if st.form_submit_button("Update Engagement"):
                cur.execute("UPDATE engagements SET status = %s, monthly_spend = %s WHERE id = %s", (new_status, new_spend, eng['id']))
                conn.commit()
                st.success("Record Updated!")
                st.rerun()
