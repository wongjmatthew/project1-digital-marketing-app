import streamlit as st
import psycopg2

st.set_page_config(page_title="Service Catalog", page_icon="🛠️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🛠️ Agency Service Catalog")

with st.form("add_service"):
    s_name = st.text_input("Service Name (e.g. SEO)")
    dept = st.selectbox("Department", ["Organic", "Paid", "Creative", "Strategy"])
    min_b = st.number_input("Minimum Monthly Budget", min_value=0)
    submitted = st.form_submit_button("Create Service")

    if submitted and s_name:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO services (service_name, department, min_monthly_budget) VALUES (%s, %s, %s)", 
                        (s_name, dept, min_b))
            conn.commit()
            st.success(f"Service {s_name} added.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
