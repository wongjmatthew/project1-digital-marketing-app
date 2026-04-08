import streamlit as st
import psycopg2
from psycopg2 import extras

st.set_page_config(page_title="Service Catalog", layout="wide")

def get_conn():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🛠️ Agency Service Catalog")

# --- 1. DYNAMIC DROPDOWN FETCH (Requirement #6) ---
try:
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Pull departments from the database lookup table
            cur.execute("SELECT id, name FROM departments ORDER BY name;")
            dept_data = cur.fetchall()
            # Create a dictionary { "Creative": 3, "Paid Media": 2 }
            dept_options = {row[1]: row[0] for row in dept_data}
except Exception as e:
    st.error("Error loading departments. Please check your database setup.")

# --- 2. CREATE: ADD SERVICE FORM (Requirement #4 & #5) ---
with st.expander("➕ Add New Service Offering"):
    with st.form("add_service_form"):
        service_name = st.text_input("Service Name (e.g., SEO Strategy)*")
        # Use the dynamic options from the database
        selected_dept = st.selectbox("Department", options=list(dept_options.keys()))
        min_budget = st.number_input("Minimum Monthly Budget ($)", min_value=0.0)
        
        submitted = st.form_submit_button("Add Service")
        
        if submitted:
            errors = []
            if not service_name.strip(): errors.append("Service Name is required.")
            if min_budget <= 0: errors.append("Minimum budget must be a positive number.")
            
            if errors:
                for err in errors: st.error(err)
            else:
                try:
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            # Requirement #9: Parameterized SQL
                            cur.execute(
                                "INSERT INTO services (service_name, dept_id, min_monthly_budget) VALUES (%s, %s, %s)",
                                (service_name, dept_options[selected_dept], min_budget)
                            )
                            conn.commit()
                            st.success(f"Successfully added {service_name}!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Error adding service: {e}")

st.divider()

# --- 3. READ: DISPLAY SERVICES WITH JOIN (Requirement #4 & #9) ---
st.subheader("Current Service Catalog")
try:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            # CRITICAL FIX: Use JOIN to get department name instead of the ID
            query = """
                SELECT s.id, s.service_name, d.name as dept_name, s.min_monthly_budget 
                FROM services s
                JOIN departments d ON s.dept_id = d.id
                ORDER BY d.name, s.service_name;
            """
            cur.execute(query)
            services = cur.fetchall()

    if services:
        # Table Header
        h_col1, h_col2, h_col3, h_col4 = st.columns([3, 2, 2, 1])
        h_col1.write("**Service Name**")
        h_col2.write("**Department**")
        h_col3.write("**Min Budget**")
        h_col4.write("**Action**")
        st.divider()

        for s in services:
            row_col1, row_col2, row_col3, row_col4 = st.columns([3, 2, 2, 1])
            row_col1.write(s['service_name'])
            row_col2.write(s['dept_name'])
            row_col3.write(f"${s['min_monthly_budget']:,.2f}")
            
            # --- 4. DELETE: WITH CONFIRMATION (Requirement #4) ---
            if row_col4.button("🗑️", key=f"del_{s['id']}"):
                st.session_state[f"confirm_delete_{s['id']}"] = True
            
            if st.session_state.get(f"confirm_delete_{s['id']}", False):
                st.warning(f"Delete '{s['service_name']}'?")
                c_col1, c_col2 = st.columns(2)
                if c_col1.button("Confirm", key=f"y_{s['id']}"):
                    try:
                        with get_conn() as conn:
                            with conn.cursor() as cur:
                                # Referential Integrity check is handled by 'ON DELETE RESTRICT' in DB
                                cur.execute("DELETE FROM services WHERE id = %s", (s['id'],))
                                conn.commit()
                                st.rerun()
                    except psycopg2.errors.ForeignKeyViolation:
                        st.error("Cannot delete: This service is tied to an active engagement.")
                        del st.session_state[f"confirm_delete_{s['id']}"]
                
                if c_col2.button("Cancel", key=f"n_{s['id']}"):
                    del st.session_state[f"confirm_delete_{s['id']}"]
                    st.rerun()
    else:
        st.info("No services found in the catalog.")

except Exception as e:
    st.error(f"Error loading catalog: {e}")
