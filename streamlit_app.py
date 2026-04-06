import streamlit as st
import psycopg2

st.set_page_config(page_title="Power Digital PD-AMS", page_icon="📈")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📈 Power Digital Account Management")
st.write("Welcome to the internal dashboard. Use the sidebar to manage clients and services.")

st.divider()

try:
    conn = get_connection()
    cur = conn.cursor()

    # Dashboard Metrics
    cur.execute("SELECT COUNT(*) FROM clients;")
    client_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM services;")
    service_count = cur.fetchone()[0]

    cur.execute("SELECT SUM(monthly_spend) FROM engagements WHERE status = 'Active';")
    total_revenue = cur.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Clients", client_count)
    col2.metric("Service Types", service_count)
    col3.metric("Monthly Managed Spend", f"${total_revenue:,.2f}")

    st.divider()
    st.subheader("Recent Engagements")
    cur.execute("""
        SELECT c.company_name, s.service_name, e.monthly_spend, e.start_date 
        FROM engagements e
        JOIN clients c ON e.client_id = c.id
        JOIN services s ON e.service_id = s.id
        ORDER BY e.id DESC LIMIT 5;
    """)
    rows = cur.fetchall()
    if rows:
        st.table([{"Client": r[0], "Service": r[1], "Budget": f"${r[2]:,.2f}", "Started": r[3]} for r in rows])
    else:
        st.info("No active engagements found.")

    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error connecting to dashboard data: {e}")
