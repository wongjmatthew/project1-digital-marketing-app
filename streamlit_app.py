import streamlit as st
import psycopg2
from psycopg2 import extras

st.set_page_config(page_title="DAMS Dashboard", layout="wide")

def get_conn():
    return psycopg2.connect(st.secrets["DB_URL"]) # Requirement #9: Secrets 

st.title("📈 Agency Executive Dashboard")

try:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            # Metrics (Requirement #8) [cite: 10, 44]
            cur.execute("SELECT COUNT(*) FROM clients")
            c_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM engagements WHERE status_id = (SELECT id FROM engagement_statuses WHERE name = 'Active')")
            e_count = cur.fetchone()[0]
            
            cur.execute("SELECT SUM(monthly_spend) FROM engagements")
            total_rev = cur.fetchone()[0] or 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Brands", c_count)
            m2.metric("Active Engagements", e_count)
            m3.metric("Total Monthly Managed Spend", f"${total_rev:,.2f}")

            st.divider()
            
            # READ: List of all Engagements with JOINS 
            st.subheader("📋 Master Engagement List")
            cur.execute("""
                SELECT c.company_name, s.service_name, e.monthly_spend, es.name as status, e.start_date
                FROM engagements e
                JOIN clients c ON e.client_id = c.id
                JOIN services s ON e.service_id = s.id
                JOIN engagement_statuses es ON e.status_id = es.id
                ORDER BY e.start_date DESC;
            """)
            rows = cur.fetchall()
            if rows:
                st.table(rows)
            else:
                st.info("No engagements found. Head to the Engagement Manager to create one.")

except Exception as e:
    st.error("Dashboard error: Could not retrieve metrics.") # Requirement #9: Error handling
