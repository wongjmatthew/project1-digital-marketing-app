import streamlit as st
import psycopg2
from psycopg2 import extras

# Function to handle database connection securely (Requirement #9)
def get_conn(): 
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🤝 Engagement Manager")

try:
    # 1. FETCH DATA FOR DYNAMIC DROPDOWNS (Requirement #6: No Hard-Coding)
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("SELECT id, company_name FROM clients ORDER BY company_name")
            clients = {r['company_name']: r['id'] for r in cur.fetchall()}
            
            cur.execute("SELECT id, service_name, min_monthly_budget FROM services ORDER BY service_name")
            service_data = {r['service_name']: (r['id'], r['min_monthly_budget']) for r in cur.fetchall()}
            
            cur.execute("SELECT id, name FROM engagement_statuses ORDER BY name")
            statuses = {r['name']: r['id'] for r in cur.fetchall()}

    # --- CREATE SECTION ---
    with st.expander("➕ New Engagement"):
        with st.form("new_engagement_form"):
            c_sel = st.selectbox("Select Client", options=list(clients.keys()))
            s_sel = st.selectbox("Select Service", options=list(service_data.keys()))
            stat_sel = st.selectbox("Initial Status", options=list(statuses.keys()))
            
            # Fetch budget floor to display and validate (Requirement #55)
            min_req = service_data[s_sel][1]
            st.info(f"Minimum monthly budget for this service: ${min_req:,.2f}")
            
            spend = st.number_input("Monthly Spend ($)", min_value=0.0)
            start = st.date_input("Start Date")
            end = st.date_input("End Date")
            
            # THE FIX: This button is required for the form to submit
            submitted = st.form_submit_button("Sign Contract")
            
            if submitted:
                # Requirement #5: Validation list (collect all errors first)
                errors = []
                if spend < min_req: 
                    errors.append(f"Budget Violation: Spend must meet floor of ${min_req:,.2f}") [cite: 55, 60]
                if end <= start: 
                    errors.append("Date Consistency: End date must be after start date") [cite: 63]
                
                if errors:
                    for err in errors: st.error(err)
                else:
                    # Requirement #9: Parameterized SQL to prevent injection
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO engagements (client_id, service_id, status_id, monthly_spend, start_date, end_date) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (clients[c_sel], service_data[s_sel][0], statuses[stat_sel], spend, start, end))
                            conn.commit()
                            st.success("Contract successfully recorded!")
                            st.rerun()

    st.divider()

    # --- READ / UPDATE / DELETE SECTION (Requirement #4) ---
    st.subheader("📝 Manage Active Engagements")
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("""
                SELECT e.id, c.company_name, s.service_name, e.monthly_spend, s.min_monthly_budget, es.name as status
                FROM engagements e
                JOIN clients c ON e.client_id = c.id
                JOIN services s ON e.service_id = s.id
                JOIN engagement_statuses es ON e.status_id = es.id;
            """)
            engs = cur.fetchall()

    for eng in engs:
        with st.expander(f"{eng['company_name']} - {eng['service_name']} ({eng['status']})"):
            col1, col2 = st.columns(2)
            
            # UPDATE Form
            with col1.form(f"update_{eng['id']}"):
                new_spend = st.number_input("Update Spend", value=float(eng['monthly_spend']), min_value=0.0)
                if st.form_submit_button("Save Changes"):
                    if new_spend < eng['min_monthly_budget']:
                        st.error(f"Cannot save: Below ${eng['min_monthly_budget']} floor.")
                    else:
                        with get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("UPDATE engagements SET monthly_spend = %s WHERE id = %s", (new_spend, eng['id']))
                                conn.commit()
                                st.rerun()

            # DELETE with Confirmation (Requirement #49, #57)
            if col2.button("🗑️ Delete", key=f"del_{eng['id']}"):
                st.session_state[f"conf_{eng['id']}"] = True
            
            if st.session_state.get(f"conf_{eng['id']}", False):
                st.warning("Are you sure? This action is permanent.")
                if st.button("Yes, Delete Engagement", key=f"y_{eng['id']}"):
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM engagements WHERE id = %s", (eng['id'],))
                            conn.commit()
                            st.rerun()
                if st.button("Cancel", key=f"n_{eng['id']}"):
                    del st.session_state[f"conf_{eng['id']}"]
                    st.rerun()

except Exception as e:
    st.error(f"System Error: {e}")
