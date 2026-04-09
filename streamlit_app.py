import streamlit as st
import psycopg2
from psycopg2 import extras

# Page configuration for a professional wide layout
st.set_page_config(page_title="DAMS Dashboard", page_icon="📈", layout="wide")

# Secrets Management (Requirement #9)
def get_conn():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📈 Executive Dashboard")
st.write("Real-time summary of agency clients and active service engagements.")

try:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            # 1. DASHBOARD METRICS (Requirement #8)
            # Pulling live counts and sums using st.metric
            cur.execute("SELECT COUNT(*) FROM clients")
            c_count = cur.fetchone()[0]
            
            # Count engagements where status is 'Active'
            cur.execute("""
                SELECT COUNT(*) FROM engagements 
                WHERE status_id = (SELECT id FROM engagement_statuses WHERE name = 'Active')
            """)
            e_count = cur.fetchone()[0]
            
            cur.execute("SELECT SUM(monthly_spend) FROM engagements")
            total_rev = cur.fetchone()[0] or 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Brands", c_count)
            m2.metric("Active Engagements", e_count)
            m3.metric("Monthly Managed Spend", f"${total_rev:,.2f}")

            st.divider()
            
            # 2. READ: MASTER ENGAGEMENT LIST (Requirement #4 & #56)
            st.subheader("📋 Master Engagement List")
            
            # SQL JOIN to pull readable names instead of IDs (Requirement #41)
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
                # Create the Header Row for the table
                h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([2, 2, 2, 1, 3])
                h_col1.write("**Brand**")
                h_col2.write("**Service**")
                h_col3.write("**Monthly Budget**")
                h_col4.write("**Status**")
                h_col5.write("**Start / End Date**")
                st.divider()

                # Iterate through database rows to populate the table
                for r in rows:
                    r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([2, 2, 2, 1, 3])
                    r_col1.write(r['company_name'])
                    r_col2.write(r['service_name'])
                    # Format budget as currency (Requirement #60)
                    r_col3.write(f"${r['monthly_spend']:,.0f}")
                    r_col4.write(r['status'])
                    # Combining start and end dates as requested
                    r_col5.write(f"{r['start_date']} to {r['end_date']}")
            else:
                st.info("No engagements found. Add some in the Engagement Manager!")

except Exception as e:
    # Requirement #9: User-friendly error handling
    st.error(f"Error loading dashboard: {e}")
