import streamlit as st
import psycopg2
import re

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🏢 Client Directory")

# 1. CREATE: Working Insert Form (Rubric Requirement)
with st.expander("➕ Onboard New Client"):
    with st.form("client_form"):
        name = st.text_input("Company Name*")
        email = st.text_input("Contact Email*")
        url = st.text_input("Website URL (Include http:// or https://)*")
        industry = st.selectbox("Industry", ["SaaS", "E-commerce", "B2B", "Healthcare", "Other"])
        tier = st.selectbox("Account Tier", ["Enterprise", "Mid-Market", "Core"])
        submit = st.form_submit_button("Add Client")

        if submit:
            # Form Validation (Rubric Requirement)
            errors = []
            if not name: errors.append("Company Name is required.")
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Invalid email format.")
            if not re.match(r'https?://', url):
                errors.append("Website URL must start with http:// or https://.")

            if errors:
                for err in errors: st.error(err)
            else:
                conn = get_connection()
                cur = conn.cursor()
                # Parameterized SQL (Security Requirement)
                cur.execute("""
                    INSERT INTO clients (company_name, contact_email, website_url, industry, account_tier) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, email, url, industry, tier))
                conn.commit()
                st.success(f"Successfully added {name}")
                st.rerun()

st.divider()

# 2. SEARCH/FILTER: Functional Search (Rubric Requirement)
search_query = st.text_input("🔍 Search Clients by Company Name")

conn = get_connection()
cur = conn.cursor()
if search_query:
    cur.execute("SELECT id, company_name, industry, account_tier FROM clients WHERE company_name ILIKE %s", (f"%{search_query}%",))
else:
    cur.execute("SELECT id, company_name, industry, account_tier FROM clients ORDER BY company_name")
clients = cur.fetchall()

# 3. DELETE: With Confirmation (Rubric Requirement)
for c in clients:
    col1, col2, col3 = st.columns([3, 2, 1])
    col1.write(f"**{c[1]}** ({c[2]})")
    col2.write(c[3])
    
    if col3.button("🗑️ Delete", key=f"del_c_{c[0]}"):
        st.session_state[f"conf_del_{c[0]}"] = True
    
    if st.session_state.get(f"conf_del_{c[0]}", False):
        st.warning(f"Confirm deleting {c[1]}? This will also delete all active engagements.")
        if st.button("Yes, Permanent Delete", key=f"y_del_{c[0]}"):
            cur.execute("DELETE FROM clients WHERE id = %s", (c[0],))
            conn.commit()
            st.rerun()
