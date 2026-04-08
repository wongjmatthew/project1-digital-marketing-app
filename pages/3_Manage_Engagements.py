import streamlit as st
import psycopg2

def get_conn(): return psycopg2.connect(st.secrets["DB_URL"])

st.title("🤝 Engagement Manager")

with get_conn() as conn:
    cur = conn.cursor()
    # Requirement #6: Dynamic Dropdowns for EVERYTHING
    cur.execute("SELECT id, company_name FROM clients")
    clients = {r[1]: r[0] for r in cur.fetchall()}
    cur.execute("SELECT id, service_name FROM services")
    services = {r[1]: r[0] for r in cur.fetchall()}
    cur.execute("SELECT id, name FROM engagement_statuses")
    statuses = {r[1]: r[0] for r in cur.fetchall()}

with st.form("new_engagement"):
    c_choice = st.selectbox("Client", options=list(clients.keys()))
    s_choice = st.selectbox("Service", options=list(services.keys()))
    stat_choice = st.selectbox("Status", options=list(statuses.keys()))
    spend = st.number_input("Monthly Spend", min_value=0.0)
    start = st.date_input("Start Date")
    end = st.date_input("End Date")
    
    if st.form_submit_button("Sign Engagement"):
        # Validation
        if end <= start:
            st.error("End date must be after start date.")
        elif spend <= 0:
            st.error("Spend must be positive.")
        else:
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO engagements (client_id, service_id, status_id, monthly_spend, start_date, end_date) 
                               VALUES (%s, %s, %s, %s, %s, %s)""", 
                            (clients[c_choice], services[s_choice], statuses[stat_choice], spend, start, end))
                conn.commit()
                st.success("Contract Signed!")
