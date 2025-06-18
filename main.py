import pandas as pd
from analytics import run_full_analytics, run_closed_loop_optimization, run_ai_sop_recommendation, digital_worker_assistant, get_sample_data
import streamlit as st

st.set_page_config(page_title="Offline Digital Twin for Forging", layout="wide")

st.title("Offline Digital Twin for Forging (Batch Data Mode)")

# Option to upload or use sample data
data_option = st.radio(
    "Choose Data Source:",
    ("Upload your CSV file", "Use sample dataset"),
    horizontal=True,
)

if data_option == "Upload your CSV file":
    uploaded_file = st.file_uploader(
        "Upload Periodic/Manual Dataset (CSV format)", type=["csv"]
    )
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
    else:
        st.info("Please upload your CSV file to proceed.")
        df = None
else:
    df = get_sample_data()
    st.info("Using built-in sample dataset:")

if df is not None:
    st.write("Sample Data Preview:", df.head())

    st.header("1. Full Analytics")
    result = run_full_analytics(df)
    st.json(result)

    st.header("2. Closed-Loop Optimization")
    opt = run_closed_loop_optimization(df)
    st.json(opt)

    st.header("3. AI-Driven SOP Recommendation")
    sop = run_ai_sop_recommendation(df)
    st.success(sop)

    st.header("4. Digital Worker Assistant (NLP Q&A)")
    user_query = st.text_input("Ask a question about alerts, KPIs, or trends:")
    if user_query and not df.empty:
        resp = digital_worker_assistant(user_query, df)
        st.info(resp)
else:
    st.stop()

st.caption("Offline Digital Twin | AI/ML Analytics, Optimization, and Digital Worker Assistant.")
