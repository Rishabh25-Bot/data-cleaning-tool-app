import streamlit as st
import pandas as pd

st.title("🧹 Data Cleaning Tool")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.write("### Original Data")
    st.dataframe(df)

    st.write("### Cleaned Data (No Missing Values)")
    df_clean = df.dropna()
    st.dataframe(df_clean)

    st.download_button(
        label="Download Cleaned Data",
        data=df_clean.to_csv(index=False),
        file_name="cleaned_data.csv",
        mime="text/csv"
    )
