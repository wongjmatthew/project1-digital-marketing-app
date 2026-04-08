import streamlit as st
import psycopg2
from psycopg2 import extras

st.set_page_config(page_title="DAMS Home", layout="wide")

def get_conn():
    return psycopg2.connect(st.secrets["DB_URL"]) # Requirement #9: st.secrets

st.title("📈 Agency Dashboard")

try:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            # Dashboard Metrics (Requirement #8)
            cur.execute("SELECT COUNT(*) FROM clients")
            c_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM engagements WHERE status_id = 1") # 1 = Active
            e_count = cur.fetchone()[0]
            cur.execute("SELECT SUM(monthly_spend) FROM engagements")
            total_rev = cur.fetchone()[0] or 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Clients", c_count)
            m2.metric("Active Engagements", e_count)
            m3.metric("Monthly Managed Spend", f"${total_rev:,.2f}")
except Exception as e:
    st.error(f"User-friendly Error: Could not load dashboard data.") # Requirement #9: Error handling
