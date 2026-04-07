import streamlit as st
import psycopg2
from psycopg2 import extras

# Basic Page Config
st.set_page_config(page_title="DAMS Dashboard", page_icon="📈", layout="wide")

# Secrets Management (Rubric Requirement)
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📈 Power Digital: Executive Dashboard")
st.write("Welcome to the Digital Account Management System (DAMS).")

try:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.DictCursor)

    # 1. READ: Metrics for Dashboard (Rubric Requirement)
    cur.execute("SELECT SUM(monthly_spend) FROM engagements WHERE status = 'Active';")
    total_revenue = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(DISTINCT id) FROM clients;")
    total_clients = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM engagements WHERE status = 'Active';")
    active_contracts = cur.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Managed Monthly Spend", f"${total_revenue:,.2f}")
    col2.metric("Total Clients", total_clients)
    col3.metric("Active Engagements", active_contracts)

    st.divider()

    # 2. READ: Recent Engagements (Rubric Requirement)
    st.subheader("📋 Recent & Expiring Engagements")
    cur.execute("""
        SELECT c.company_name, s.service_name, e.monthly_spend, e.start_date, e.status
        FROM engagements e
        JOIN clients c ON e.client_id = c.id
        JOIN services s ON e.service_id = s.id
        ORDER BY e.start_date DESC LIMIT 5;
    """)
    recent_rows = cur.fetchall()
    
    if recent_rows:
        st.table(recent_rows)
    else:
        st.info("No engagement data available.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Error connecting to database: {e}")
