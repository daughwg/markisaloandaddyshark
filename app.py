import streamlit as st
import pandas as pd

# Set up page layout
st.set_page_config(page_title="Friendship Ledger", page_icon="📝", layout="centered")

# Your specific Google Sheet ID
SHEET_ID = "1ZDK7eQlf7OECJYOVC4L1EaObTPD_2S7y14KyI8sJSM4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
BASE_LINK = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing"

@st.cache_data(ttl=2)  # Set to 2 seconds so it pulls your manual updates instantly
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # Strip spaces from column headers but KEEP their original case for safety
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        return None

df = load_data()

st.title("⚖️ Balanced Account Ledger")
st.write("Select your name below to view any remaining balance details.")

options = ["Select your profile...", "barabad", "esbra", "genoring", "limen", "palmeras"]
selected_name = st.selectbox("Who is logging in?", options)

if selected_name != "Select your profile...":
    st.divider()

    if df is not None:
        try:
            # 1. Force find columns regardless of exact casing
            name_col = [c for c in df.columns if c.lower() == 'name'][0]
            status_col = [c for c in df.columns if c.lower() == 'status'][0]
            cost_col = [c for c in df.columns if c.lower() == 'cost/individual'][0]

            # 2. Clean up the data columns for matching
            df[name_col] = df[name_col].astype(str).str.strip().str.lower()
            df[status_col] = df[status_col].astype(str).str.strip().str.lower()

            # 3. FILTER 1: Get the person's rows
            person_df = df[df[name_col] == selected_name]

            # 4. FILTER 2: Get anything that is NOT 'paid' (catches 'unpaid')
            unpaid_df = person_df[person_df[status_col] != 'paid']

            # 5. MATH: Strip currency strings, force empty strings to 0, and sum
            clean_costs = unpaid_df[cost_col].astype(str).str.replace(r'[^\d\.]', '', regex=True)
            numeric_costs = pd.to_numeric(clean_costs, errors='coerce').fillna(0)
            total_debt = numeric_costs.sum()

            st.subheader(f"Summary for: **{selected_name.upper()}**")

            # CRITICAL CHECK: Show data if rows exist, even if math failed
            if len(unpaid_df) > 0:
                st.metric(label="Current Balance Owed", value=f"₱ {total_debt:,.2f}")
                
                with st.expander("📋 View Your Unpaid Rows"):
                    st.dataframe(unpaid_df)
                    
                if total_debt == 0:
                    st.warning("⚠️ Rows were found, but the 'Cost/Individual' column numbers couldn't be parsed. Check your currency formatting!")
            else:
                st.success("🎉 Balance clear! You have no outstanding amounts.")

            # ---- FORCE VISUAL DEBUGGER ----
            st.info("🛠️ Developer Live Feed (See what Python sees below):")
            st.write(f"**Rows matching your name ('{selected_name}'):** {len(person_df)}")
            st.write(f"**Rows marked unpaid/blank:** {len(unpaid_df)}")
            st.write("**Your Google Sheet Data Preview (First 5 Rows):**")
            st.dataframe(df.head(5))

        except Exception as e:
            st.error(f"⚠️ Column Matching Error: {e}")
            st.info("Double check that your sheet columns are named exactly: 'Name', 'Cost/Individual', and 'Status'.")
    else:
        st.error("Could not fetch the database records. Please check sheet sharing permissions.")

    st.write("---")
    st.link_button(f"📂 Open Spreadsheet Workspace", BASE_LINK)
