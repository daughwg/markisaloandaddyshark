import streamlit as st
import pandas as pd

# 1. Setup App Title and Google Sheets Base URL
st.title("🦈💰MarkIsALoanDaddyShark💰🦈")

# Convert the standard sharing link to a direct download link for Pandas
share_url = "https://docs.google.com/spreadsheets/d/1ZDK7eQlf7OECJYOVC4L1EaObTPD_2S7y14KyI8sJSM4/edit?usp=sharing"
download_url = share_url.replace("/edit?usp=sharing", "/export?format=xlsx")

# 2. Step 1: Ask the user to select who they are
members = ["Select your name...", "Barabad", "Esbra", "Genoring", "Limen", "Palmeras"]
selected_member = st.selectbox("May Utang ka saken!!! Pay Up!!!", members)

# Only proceed if a valid name is chosen
if selected_member != "Select your name...":
    
    # Fetch the data for the selected member (assuming sheet names match their names perfectly)
    with st.spinner(f"Loading data for {selected_member}..."):
        try:
            # Read the specific sheet corresponding to the selected member
            df = pd.read_excel(download_url, sheet_name=selected_member)
            
            # Clean up column names (remove any accidental leading/trailing spaces)
            df.columns = df.columns.str.strip()
            
            # 3. Step 2: Calculate and display the debt amount
            # Verify required columns exist in the sheet
            if "Status" in df.columns and "Cost/Individual" in df.columns:
                
                # Filter rows where Status is 'unpaid' (case-insensitive and stripped of spaces)
                unpaid_filter = df["Status"].astype(str).str.strip().str.lower() == "unpaid"
                unpaid_rows = df[unpaid_filter]
                
                # Sum the 'Cost/Individual' column for those unpaid rows
                # .to_numeric ensures it handles any formatting issues gracefully
                total_debt = pd.to_numeric(unpaid_rows["Cost/Individual"], errors="coerce").sum()
                
                # Display the debt prominently
                st.markdown(f"### **Debt: ₱{total_debt:,.2f}**")
                
            else:
                st.error("Error: Could not find 'Status' or 'Cost/Individual' columns in your sheet.")
                st.write("Available columns are:", list(df.columns))

            st.write("---")

            # 4. Step 3: Add a button option to view their spreadsheet data
            # We initialize a toggle state so the data stays visible when clicked
            if f"show_{selected_member}" not in st.session_state:
                st.session_state[f"show_{selected_member}"] = False

            # Button to toggle spreadsheet visibility
            if st.button(f"View Spreadsheet for {selected_member}"):
                st.session_state[f"show_{selected_member}"] = not st.session_state[f"show_{selected_member}"]

            # If the button toggle is active, display the interactive dataframe
            if st.session_state[f"show_{selected_member}"]:
                st.subheader(f"{selected_member}'s Detailed Statement")
                st.dataframe(df, use_container_width=True)
                
        except ValueError:
            st.error(f"Could not find a sheet named '{selected_member}' in the Google Sheet. Please check your sheet capitalization.")
        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")
