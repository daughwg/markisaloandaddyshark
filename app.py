import streamlit as st
import pandas as pd

# Set up page layout
st.set_page_config(page_title="Friendship Ledger", page_icon="📝", layout="centered")

# Your specific Google Sheet ID
SHEET_ID = "1ZDK7eQlf7OECJYOVC4L1EaObTPD_2S7y14KyI8sJSM4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Centralized Sheet link
BASE_LINK = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing"

@st.cache_data(ttl=10)  # Re-checks sheet every 10 seconds
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # Standardize column headers: lowercase and stripped of extra spaces
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
            # 1. Safely identify dynamic column names
            name_col = 'name' if 'name' in df.columns else df.columns[0]
            
            status_col = 'status'
            if status_col not in df.columns:
                status_col = [c for c in df.columns if 'status' in c][0] if any('status' in c for c in df.columns) else df.columns[-1]

            cost_col = 'cost/individual'
            if cost_col not in df.columns:
                cost_col = [c for c in df.columns if 'cost' in c or 'indiv' in c][0] if any('cost' in c for c in df.columns) else 'cost'

            # 2. Clean the core data strings to eliminate matching issues
            df_clean = df.copy()
            df_clean[name_col] = df_clean[name_col].astype(str).str.strip().str.lower()
            
            # Convert status column to lowercase string, strip spaces
            df_clean[status_col] = df_clean[status_col].astype(str).str.strip().str.lower()
            
            # CRITICAL FIX: If the cell was blank (NaN) or explicitly written as 'nan', force it to 'unpaid'
            df_clean[status_col] = df_clean[status_col].replace(['nan', ''], 'unpaid')

            # 3. Filter rows for the selected person
            person_df = df_clean[df_clean[name_col] == selected_name]

            # 4. Filter rows where the status column is NOT 'paid'
            unpaid_df = person_df[person_df[status_col] != 'paid']

            # 5. Extract numeric values, removing currency symbols safely
            unpaid_costs = unpaid_df[cost_col].astype(str).str.replace(r'[^\d\.]', '', regex=True)
            
            # Convert empty text to 0 instead of dropping the row, then sum
            total_debt = pd.to_numeric(unpaid_costs, errors='coerce').fillna(0).sum()

            st.subheader(f"Summary for: **{selected_name.upper()}**")

            if total_debt > 0:
                # Displays standard metric styling
                st.metric(label="Current Balance Owed", value=f"₱ {total_debt:,.2f}")
                st.caption("Amounts are automatically added up from all blank, unchecked, or unpaid line items.")
                
                # Shows the breakdown items so the user knows exactly what they are paying for
                with st.expander("📋 View Unpaid Items Details"):
                    st.dataframe(unpaid_df)
            else:
                st.success("🎉 Balance clear! You have no outstanding amounts.")

            # ---- SYSTEM DEVELOPER DIAGNOSIS ----
            with st.expander("⚙️ System Developer Diagnosis"):
                st.write("**Detected Columns:**", list(df.columns))
                st.write(f"**Identified Name Col:** `{name_col}`, **Status Col:** `{status_col}`, **Cost Col:** `{cost_col}`")
                st.write("**Rows found for you:**", len(person_df))
                st.write("**Unpaid/Blank rows found for you:**", len(unpaid_df))
                st.write("**Your raw data rows (Top 5):**")
                st.dataframe(df.head(5))

        except Exception as e:
            st.warning("⚠️ Connected to sheet, but formatting doesn't match standard layout headers.")
            st.error(f"Error Details: {e}")
            st.info("Ensure headers match exactly: 'Name', 'Cost/Individual', and 'Status'.")
    else:
        st.error("Could not fetch the database records. Please double-check sheet sharing access permissions.")

    st.write("---")
    st.link_button(f"📂 Open Spreadsheet Workspace", BASE_LINK)
