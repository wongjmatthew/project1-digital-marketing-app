import streamlit as st
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🛠️ Agency Service Catalog")

# CREATE Service
with st.form("service_form"):
    s_name = st.text_input("Service Name (e.g., SEO)")
    dept = st.selectbox("Department", ["Organic", "Paid", "Creative"])
    min_b = st.number_input("Minimum Monthly Budget ($)", min_value=0)
    if st.form_submit_button("Add Service"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO services (service_name, department, min_monthly_budget) VALUES (%s, %s, %s)", (s_name, dept, min_b))
        conn.commit()
        st.rerun()

st.divider()

# READ & DELETE Service
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, service_name, department, min_monthly_budget FROM services")
for s in cur.fetchall():
    col1, col2 = st.columns([4, 1])
    col1.write(f"**{s[1]}** ({s[2]}) - Min: ${s[3]}")
    
    # Referential Integrity Check (Validation Requirement)
    if col2.button("Delete", key=f"ds_{s[0]}"):
        cur.execute("SELECT COUNT(*) FROM engagements WHERE service_id = %s", (s[0],))
        if cur.fetchone()[0] > 0:
            st.error("⚠️ Cannot delete: Service is tied to an active engagement.")
        else:
            cur.execute("DELETE FROM services WHERE id = %s", (s[0],))
            conn.commit()
            st.rerun()
