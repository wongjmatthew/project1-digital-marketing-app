import streamlit as st
import psycopg2
import re

def get_conn(): return psycopg2.connect(st.secrets["DB_URL"])

st.title("🏢 Client Management")

# --- CREATE WITH VALIDATION & DYNAMIC DROPDOWNS ---
with st.expander("Onboard New Client"):
    with get_conn() as conn:
        cur = conn.cursor()
        # Requirement #6: Dynamic Dropdowns (NO hard-coding)
        cur.execute("SELECT id, name FROM industries")
        industries = {r[1]: r[0] for r in cur.fetchall()}
        cur.execute("SELECT id, name FROM account_tiers")
        tiers = {r[1]: r[0] for r in cur.fetchall()}

    with st.form("add_client_form"):
        name = st.text_input("Company Name*")
        email = st.text_input("Contact Email*")
        ind_choice = st.selectbox("Industry", options=list(industries.keys()))
        tier_choice = st.selectbox("Tier", options=list(tiers.keys()))
        
        if st.form_submit_button("Submit"):
            # Requirement #5: Collect errors in a list
            errors = []
            if not name.strip(): errors.append("Company Name is required.")
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email): errors.append("Invalid email format.")
            
            if errors:
                for err in errors: st.error(err)
            else:
                with get_conn() as conn:
                    cur = conn.cursor()
                    # Requirement #9: Parameterized Query
                    cur.execute("INSERT INTO clients (company_name, contact_email, industry_id, tier_id) VALUES (%s, %s, %s, %s)",
                                (name, email, industries[ind_choice], tiers[tier_choice]))
                    conn.commit()
                    st.success("Client Added!")
                    st.rerun()

# --- SEARCH / FILTER (Requirement #7) ---
search = st.text_input("Search Clients by Name")
with get_conn() as conn:
    cur = conn.cursor()
    if search:
        cur.execute("SELECT id, company_name, contact_email FROM clients WHERE company_name ILIKE %s", (f"%{search}%",))
    else:
        cur.execute("SELECT id, company_name, contact_email FROM clients")
    clients = cur.fetchall()

# --- READ, UPDATE, DELETE (Requirement #4) ---
for c in clients:
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.write(f"**{c[1]}** | {c[2]}")
    
    if col2.button("Edit", key=f"ed_{c[0]}"):
        st.session_state[f"edit_{c[0]}"] = True

    # Update Logic
    if st.session_state.get(f"edit_{c[0]}", False):
        with st.form(f"f_{c[0]}"):
            new_email = st.text_input("Update Email", value=c[2])
            if st.form_submit_button("Save"):
                with get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE clients SET contact_email = %s WHERE id = %s", (new_email, c[0]))
                    conn.commit()
                    st.session_state[f"edit_{c[0]}"] = False
                    st.rerun()

    # Delete with Confirmation
    if col3.button("Delete", key=f"del_{c[0]}"):
        st.session_state[f"conf_{c[0]}"] = True
    
    if st.session_state.get(f"conf_{c[0]}", False):
        st.warning(f"Are you sure you want to delete {c[1]}?")
        if st.button("Yes, Delete", key=f"y_{c[0]}"):
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM clients WHERE id = %s", (c[0],))
                conn.commit()
                st.rerun()
