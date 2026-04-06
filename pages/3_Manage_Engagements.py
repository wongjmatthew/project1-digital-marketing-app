import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Engagements", page_icon="🤝")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🤝 Client Engagements")

# Get Dropdown Data
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, company_name FROM clients")
client_map = {row[1]: row[0] for row in cur.fetchall()}
cur.execute("SELECT id, service_name FROM services")
service_map = {row[1]: row[0] for row in cur.fetchall()}

with st.form("new_engagement"):
    c_choice = st.selectbox("Select Client", options=list(client_map.keys()))
    s_choice = st.selectbox("Select Service", options=list(service_map.keys()))
    budget = st.number_input("Monthly Spend", min_value=1)
    s_date = st.date_input("Start Date")
    e_date = st.date_input("End Date")
    submitted = st.form_submit_button("Link Service to Client")

    if submitted:
        if e_date <= s_date:
            st.error("End date must be after start date.")
        else:
            cur.execute("""INSERT INTO engagements (client_id, service_id, monthly_spend, start_date, end_date) 
                           VALUES (%s, %s, %s, %s, %s)""", 
                        (client_map[c_choice], service_map[s_choice], budget, s_date, e_date))
            conn.commit()
            st.success("Engagement created!")
            st.rerun()
cur.close()
conn.close()