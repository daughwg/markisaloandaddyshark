import streamlit as st
import pandas as pd

# Set up page layout
st.set_page_config(page_title="Friendship Ledger", page_icon="📝", layout="centered")

# Your specific Google Sheet ID
SHEET_ID = "1ZDK7eQlf7OECJYOVC4L1EaObTPD_2S7y14KyI8sJSM4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Centralized Sheet link
BASE_LINK = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing"

@st.cache_data(ttl=30)  # Re-checks your sheet every 30 seconds for changes
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # Standardize columns to avoid case-sensitivity errors
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return None

df = load_data()

st.title("⚖️ Balanced Account Ledger")
st.write("Select your name below to view any remaining balance details.")

# The specific individual groups requested
options = ["Select your profile...", "barabad", "esbra", "genoring", "limen", "palmeras"]
selected_name = st.selectbox("Who is logging in?", options)

if selected_name != "Select your profile...":
    st.divider()
    
    if df is not None:
        try:
            # Dynamically identify the names column (assuming it's column 1 or named 'name')
            name_col = 'name' if 'name' in df.columns else df.columns[0]
            
            # Filter rows for the selected person
            person_df = df[df[name_col].astype(str).str.strip().str.lower() == selected_name]
            
            # Filter rows where the status column is NOT 'paid'
            status_col = 'status' if 'status' in df.columns else 'status column'
            unpaid_df = person_df[person_df['status'].astype(str).str.strip().str.lower() != 'paid']
            
            # Isolate the Cost/Individual values and drop currency formatting symbols safely
            cost_col = 'cost/individual' if 'cost/individual' in df.columns else 'cost'
            unpaid_costs = unpaid_df[cost_col].astype(str).str.replace(r'[^\d\.]', '', regex=True)
            total_debt = pd.to_numeric(unpaid_costs, errors='coerce').sum()
            
            st.subheader(f"Summary for: **{selected_name.upper()}**")
            
            if total_debt > 0:
                # Displays standard metric styling
                st.metric(label="Current Balance Owed", value=f"₱ {total_debt:,.2f}")
                st.caption("Amounts are automatically added up from all unchecked or unpaid line items.")
            else:
                st.success("🎉 Balance clear! You have no outstanding amounts outstanding.")
                
        except Exception:
            st.warning("⚠️ Connected to sheet, but formatting doesn't match standard layout headers.")
            st.info("Ensure headers match exactly: 'Name', 'Cost/Individual', and 'Status'.")
    else:
        st.error("Could not fetch the database records. Please double-check sheet sharing access permissions.")

    st.write("---")
    # Redirects straight to their workspace context
    st.link_button(f"📂 Open Spreadsheet Workspace", BASE_LINK)
