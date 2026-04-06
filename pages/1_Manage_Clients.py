import streamlit as st
import psycopg2
import re

st.set_page_config(page_title="Manage Clients", page_icon="🏢")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🏢 Client Directory")

with st.form("add_client"):
    name = st.text_input("Company Name*")
    email = st.text_input("Contact Email*")
    industry = st.selectbox("Industry", ["E-commerce", "SaaS", "B2B", "Consumer Goods", "Other"])
    url = st.text_input("Website URL")
    submitted = st.form_submit_button("Add Client")

    if submitted:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not name or not email:
            st.error("Name and Email are required.")
        elif not re.match(email_pattern, email):
            st.error("Invalid email format.")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO clients (company_name, contact_email, industry, website_url) VALUES (%s, %s, %s, %s)", 
                            (name, email, industry, url))
                conn.commit()
                st.success(f"Added {name}!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# Display List
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, company_name, contact_email, industry FROM clients ORDER BY company_name")
    clients = cur.fetchall()
    if clients:
        st.dataframe(clients, column_config={"0":"ID", "1":"Company", "2":"Email", "3":"Industry"})
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error loading clients: {e}")
