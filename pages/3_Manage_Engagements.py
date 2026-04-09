import streamlit as st
import psycopg2
from psycopg2 import extras

def get_conn():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🤝 Engagement Manager")

try:
    # 1. FETCH DYNAMIC DATA (Requirement #6: No Hard-Coding) 
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("SELECT id, company_name FROM clients ORDER BY company_name;")
            client_options = {r['company_name']: r['id'] for r in cur.fetchall()}
            
            cur.execute("SELECT id, service_name, min_monthly_budget FROM services ORDER BY service_name;")
            service_data = {r['service_name']: (r['id'], r['min_monthly_budget']) for r in cur.fetchall()}
            
            cur.execute("SELECT id, name FROM engagement_statuses ORDER BY name;")
            status_options = {r['name']: r['id'] for r in cur.fetchall()}

    # --- CREATE SECTION ---
    with st.expander("➕ Create New Engagement"):
        with st.form("new_eng"):
            c_sel = st.selectbox("Client", options=list(client_options.keys()))
            s_sel = st.selectbox("Service", options=list(service_data.keys()))
            stat_sel = st.selectbox("Initial Status", options=list(status_options.keys()))
            
            min_allowed = service_data[s_sel][1]
            st.caption(f"Minimum Budget Required: ${min_allowed:,.2f}")
            
            spend = st.number_input("Monthly Spend", min_value=0.0)
            start = st.date_input("Start Date")
            end = st.date_input("End Date")
            
            if st.form_submit_button("Sign Contract"):
                errors = [] # Requirement #5: Validation list 
                if spend < min_allowed: errors.append(f"Spend must meet service floor of ${min_allowed}")
                if end <= start: errors.append("End date must be after start date")
                
                if errors:
                    for err in errors: st.error(err)
                else:
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO engagements (client_id, service_id, status_id, monthly_spend, start_date, end_date)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (client_options[c_sel], service_data[s_sel][0], status_options[stat_sel], spend, start, end))
                            conn.commit()
                            st.rerun()

    st.divider()

    # --- READ / UPDATE / DELETE SECTION ---
    st.subheader("📝 Manage Existing Engagements")
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("""
                SELECT e.id, c.company_name, s.service_name, e.monthly_spend, s.min_monthly_budget, es.name as status, e.status_id
                FROM engagements e
                JOIN clients c ON e.client_id = c.id
                JOIN services s ON e.service_id = s.id
                JOIN engagement_statuses es ON e.status_id = es.id;
            """)
            engs = cur.fetchall()

    for eng in engs:
        with st.expander(f"{eng['company_name']} - {eng['service_name']} ({eng['status']})"):
            col1, col2 = st.columns(2)
            
            # UPDATE (Requirement #4) 
            with col1.form(f"edit_{eng['id']}"):
                st.write("**Edit Engagement**")
                # Pre-populated values (Rubric Requirement) 
                new_spend = st.number_input("Monthly Spend", value=float(eng['monthly_spend']), min_value=0.0)
                new_stat = st.selectbox("Status", options=list(status_options.keys()), index=list(status_options.keys()).index(eng['status']))
                
                if st.form_submit_button("Save Changes"):
                    if new_spend < eng['min_monthly_budget']:
                        st.error(f"Cannot save: Below ${eng['min_monthly_budget']} floor.")
                    else:
                        with get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("UPDATE engagements SET monthly_spend = %s, status_id = %s WHERE id = %s", 
                                            (new_spend, status_options[new_stat], eng['id']))
                                conn.commit()
                                st.rerun()

            # DELETE WITH CONFIRMATION (Requirement #4) 
            if col2.button("🗑️ Delete Engagement", key=f"del_btn_{eng['id']}"):
                st.session_state[f"confirm_{eng['id']}"] = True
            
            if st.session_state.get(f"confirm_{eng['id']}", False):
                st.warning("Delete this contract permanently?")
                if st.button("Yes, Confirm Delete", key=f"y_{eng['id']}"):
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM engagements WHERE id = %s", (eng['id'],))
                            conn.commit()
                            st.rerun()
                if st.button("Cancel", key=f"n_{eng['id']}"):
                    del st.session_state[f"confirm_{eng['id']}"]
                    st.rerun()

except Exception as e:
    st.error(f"System Error: {e}")
