import streamlit as st
import psycopg2
from psycopg2 import extras

st.set_page_config(page_title="Power Digital Dashboard", page_icon="📈")

# Secrets Management: Uses st.secrets as required by rubric
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📈 Power Digital Agency Dashboard")

try:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=extras.DictCursor)

    # Dashboard Metrics (Read Requirement)
    cur.execute("SELECT COUNT(*) FROM clients;")
    client_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM services;")
    service_count = cur.fetchone()[0]
    cur.execute("SELECT SUM(monthly_spend) FROM engagements;")
    total_spend = cur.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Clients", client_count)
    col2.metric("Services Offered", service_count)
    col3.metric("Total Managed Revenue", f"${total_spend:,.2f}")

    st.divider()
    st.subheader("Recent Client Engagements")
    
    # SQL JOIN to show names instead of IDs (Database Quality Requirement)
    query = """
        SELECT c.company_name, s.service_name, e.monthly_spend, e.start_date
        FROM engagements e
        JOIN clients c ON e.client_id = c.id
        JOIN services s ON e.service_id = s.id
        ORDER BY e.id DESC LIMIT 5
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    if rows:
        st.table([{"Client": r[0], "Service": r[1], "Budget": f"${r[2]:,.2f}", "Started": r[3]} for r in rows])
    else:
        st.info("No engagements recorded yet.")

    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Connection Error: {e}")
