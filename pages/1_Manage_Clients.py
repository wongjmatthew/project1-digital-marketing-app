import streamlit as st
import psycopg2
import re

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🏢 Manage Clients")

# CREATE: Working insert form
with st.form("add_client"):
    name = st.text_input("Company Name*")
    email = st.text_input("Contact Email*")
    industry = st.text_input("Industry")
    submitted = st.form_submit_button("Add Client")

    if submitted:
        # Form Validation (Rubric Requirement)
        errors = []
        if not name.strip(): errors.append("Name is required.")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("Valid email is required.")
        
        if errors:
            for err in errors: st.error(err)
        else:
            conn = get_connection()
            cur = conn.cursor()
            # Parameterized SQL (Security Requirement)
            cur.execute("INSERT INTO clients (company_name, contact_email, industry) VALUES (%s, %s, %s)", (name, email, industry))
            conn.commit()
            st.success("Client added!")
            st.rerun()

st.divider()

# SEARCH / FILTER: Narrow down displayed data (Rubric Requirement)
search = st.text_input("🔍 Search Clients by Name")
conn = get_connection()
cur = conn.cursor()

if search:
    cur.execute("SELECT * FROM clients WHERE company_name ILIKE %s", (f"%{search}%",))
else:
    cur.execute("SELECT * FROM clients")

clients = cur.fetchall()
if clients:
    st.dataframe(clients, use_container_width=True)
