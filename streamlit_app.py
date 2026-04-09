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
            
           st.subheader("📋 Master Engagement List")

try:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            # SQL JOIN to pull all relevant columns for the headers
            cur.execute("""
                SELECT c.company_name, s.service_name, e.monthly_spend, es.name as status, e.start_date, e.end_date
                FROM engagements e
                JOIN clients c ON e.client_id = c.id
                JOIN services s ON e.service_id = s.id
                JOIN engagement_statuses es ON e.status_id = es.id
                ORDER BY e.start_date DESC;
            """)
            rows = cur.fetchall()

            if rows:
                # 1. Create the Header Row (Requirement #56)
                h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([2, 2, 2, 1, 3])
                h_col1.write("**Brand**")
                h_col2.write("**Service**")
                h_col3.write("**Monthly Budget**")
                h_col4.write("**Status**")
                h_col5.write("**Start / End Date**")
                st.divider()

                # 2. Iterate through rows and place data under headers
                for r in rows:
                    r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([2, 2, 2, 1, 3])
                    r_col1.write(r['company_name'])
                    r_col2.write(r['service_name'])
                    r_col3.write(f"${r['monthly_spend']:,.0f}")
                    r_col4.write(r['status'])
                    # Combining start and end dates into one column as requested
                    r_col5.write(f"{r['start_date']} to {r['end_date']}")
            else:
                st.info("No engagements found. Add some in the Engagement Manager!")

except Exception as e:
    st.error("Dashboard error: Could not retrieve metrics.") # Requirement #9: Error handling
