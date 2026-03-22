import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from src.file_loader import load_file
from src.data_profiler import profile_data
from src.cleaning_engine import (
    remove_duplicates,
    remove_high_missing_columns,
    fill_missing_values
)

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="SmartClean AI", layout="wide")

st.title("SmartClean AI - Data Cleaning Tool")
st.write("Upload, analyze, clean and export your dataset")

# -------------------------------
# Session State
# -------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Upload Dataset",
        "Dataset Overview",
        "Data Profiling",
        "Visualization",
        "Outlier Detection",
        "Data Cleaning",
        "Download Data"
    ]
)

# -------------------------------
# Upload Dataset
# -------------------------------
if page == "Upload Dataset":

    uploaded_file = st.file_uploader(
        "Upload CSV, TXT, Excel file",
        type=["csv", "txt", "xlsx"]
    )

    if uploaded_file is not None:
        df = load_file(uploaded_file)
        st.session_state.df = df.copy()
        st.success("File loaded successfully!")

# -------------------------------
# Dataset Overview
# -------------------------------
elif page == "Dataset Overview":

    if st.session_state.df is not None:
        df = st.session_state.df

        st.header("Dataset Overview")

        col1, col2, col3, col4 = st.columns(4)

        rows = df.shape[0]
        cols = df.shape[1]
        duplicates = df.duplicated().sum()
        missing = df.isnull().sum().sum()

        col1.metric("Rows", rows)
        col2.metric("Columns", cols)
        col3.metric("Duplicates", duplicates)
        col4.metric("Missing Values", missing)

        # Data Quality Score
        total_cells = rows * cols
        score = round((1 - ((missing + duplicates) / total_cells)) * 100, 2)
        st.metric("Data Quality Score", f"{score}%")

        st.subheader("Preview")
        st.dataframe(df.head())

    else:
        st.warning("Upload dataset first")

# -------------------------------
# Data Profiling
# -------------------------------
elif page == "Data Profiling":

    if st.session_state.df is not None:
        df = st.session_state.df
        profile = profile_data(df)

        st.header("Data Profiling")

        st.subheader("Duplicates")
        st.write(profile["duplicates"])

        st.subheader("Missing Values")
        st.dataframe(profile["missing"])

        st.subheader("Summary")
        st.dataframe(profile["summary"])

    else:
        st.warning("Upload dataset first")

# -------------------------------
# Visualization
# -------------------------------
elif page == "Visualization":

    if st.session_state.df is not None:
        df = st.session_state.df

        st.header("Missing Values Chart")
        missing = df.isnull().sum()
        st.plotly_chart(px.bar(x=missing.index, y=missing.values))

        st.header("Correlation Heatmap")
        num_df = df.select_dtypes(include=["int64", "float64"])

        if not num_df.empty:
            fig, ax = plt.subplots()
            sns.heatmap(num_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

        st.header("Feature Distribution")
        if len(num_df.columns) > 0:
            col = st.selectbox("Select Column", num_df.columns)
            st.plotly_chart(px.histogram(df, x=col))

    else:
        st.warning("Upload dataset first")

# -------------------------------
# Outlier Detection
# -------------------------------
elif page == "Outlier Detection":

    if st.session_state.df is not None:
        df = st.session_state.df

        st.header("Outlier Detection")

        outliers = {}

        for col in df.select_dtypes(include=["int64", "float64"]):
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            mask = (df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)
            outliers[col] = mask.sum()

        st.write(outliers)

        if len(df.select_dtypes(include=["int64", "float64"]).columns) > 0:
            col = st.selectbox("Column", df.select_dtypes(include=["int64","float64"]).columns)
            st.plotly_chart(px.box(df, y=col))

    else:
        st.warning("Upload dataset first")

# -------------------------------
# Data Cleaning (IMPROVED)
# -------------------------------
elif page == "Data Cleaning":

    if st.session_state.df is not None:
        df = st.session_state.df

        st.header("Data Cleaning Options")

        col1, col2, col3 = st.columns(3)

        if col1.button("Remove Duplicates"):
            df, removed = remove_duplicates(df)
            st.session_state.df = df
            st.session_state.history.append(f"Removed {removed} duplicates")

        if col2.button("Drop Missing >40%"):
            df, dropped = remove_high_missing_columns(df, 40)
            st.session_state.df = df
            st.session_state.history.append(f"Dropped columns: {dropped}")

        if col3.button("Fill Missing"):
            df = fill_missing_values(df)
            st.session_state.df = df
            st.session_state.history.append("Filled missing values")

        # Column Drop Option
        st.subheader("Drop Specific Column")
        col = st.selectbox("Select Column", df.columns)

        if st.button("Drop Column"):
            df = df.drop(columns=[col])
            st.session_state.df = df
            st.session_state.history.append(f"Dropped column {col}")

        # History
        st.subheader("Cleaning History")
        for h in st.session_state.history:
            st.write("•", h)

        # Updated Data
        st.subheader("Updated Dataset")
        st.dataframe(st.session_state.df.head())

    else:
        st.warning("Upload dataset first")

# -------------------------------
# Download
# -------------------------------
elif page == "Download Data":

    if st.session_state.df is not None:
        df = st.session_state.df

        st.header("Download Cleaned Dataset")

        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            "cleaned_data.csv"
        )

    else:
        st.warning("Upload dataset first")
