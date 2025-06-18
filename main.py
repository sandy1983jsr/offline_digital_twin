import pandas as pd
from analytics import (
    run_full_analytics,
    run_closed_loop_optimization,
    run_ai_sop_recommendation,
    digital_worker_assistant,
    get_sample_data,
)
import streamlit as st

st.set_page_config(page_title="Offline Digital Twin for Forging", layout="wide")

st.title("Offline Digital Twin for Forging (Batch/Hourly Data Dashboard)")

st.sidebar.header("Data Options")
data_option = st.sidebar.radio(
    "Choose Data Source:",
    ("Upload your CSV file", "Use sample dataset"),
)

df = None

if data_option == "Upload your CSV file":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Periodic/Manual/Hourly Dataset (CSV format)", type=["csv"]
    )
    if uploaded_file:
        try:
            # Read the uploaded file only once
            df = pd.read_csv(uploaded_file)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.success("File uploaded successfully!")
        except pd.errors.EmptyDataError:
            st.error("Uploaded file is empty. Please upload a valid CSV file with data.")
            df = None
    else:
        st.info("Please upload your CSV file to proceed.")
else:
    df = get_sample_data()
    st.info("Using built-in sample dataset:")

if df is not None and not df.empty:
    st.subheader("Sample Data Preview")
    st.dataframe(df.head())

    st.markdown("## 🛠️ Key Process KPIs")
    analytics = run_full_analytics(df)
    kpis = analytics["kpis"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Furnace Temp (°C)", f"{kpis['mean_furnace_temp']:.1f}")
    col2.metric("Power Usage (kWh)", f"{kpis['mean_power_usage']:.1f}")
    col3.metric("Gas Cons. (Nm³)", f"{kpis['mean_gas_consumption']:.1f}")
    col4.metric("Water Usage (m³)", f"{kpis['mean_water_usage']:.2f}")

    col5, col6, col7 = st.columns(3)
    col5.metric("Scrap Rate (%)", f"{kpis['mean_scrap_rate']:.2f}")
    col6.metric("Downtime (%)", f"{kpis['downtime_pct']:.2f}")
    col7.metric("Runtime (%)", f"{kpis['runtime_pct']:.2f}")

    st.markdown("---")
    st.markdown("## 📈 Trends & Distributions")

    # If timestamp available, use as x-axis
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")
        st.line_chart(df.set_index("timestamp")[["furnace_temp", "power_usage", "gas_consumption"]])
        scrap_rate_series = ((df["material_input"] - df["production_output"]) / df["material_input"]).rename("scrap_rate") * 100
        st.line_chart(scrap_rate_series)
    else:
        chart_cols = st.columns(2)
        chart_cols[0].subheader("Furnace Temp Trend")
        chart_cols[0].line_chart(df["furnace_temp"])
        chart_cols[1].subheader("Power Usage Trend")
        chart_cols[1].line_chart(df["power_usage"])

        chart_cols2 = st.columns(2)
        chart_cols2[0].subheader("Gas Consumption Trend")
        chart_cols2[0].line_chart(df["gas_consumption"])
        chart_cols2[1].subheader("Scrap per Batch")
        scrap_per_batch = ((df["material_input"] - df["production_output"]) / df["material_input"]) * 100
        chart_cols2[1].bar_chart(scrap_per_batch)

    st.markdown("---")
    st.markdown("## 🤖 Insights & Optimization")

    with st.expander("Full Analytics (JSON)", expanded=False):
        st.json(analytics)
    st.success(
        f"Predicted Scrap Rate: {analytics['predicted_scrap_rate']}%"
        if isinstance(analytics['predicted_scrap_rate'], (int, float))
        else f"Predicted Scrap Rate: {analytics['predicted_scrap_rate']}"
    )

    st.info("Energy Optimization Recommendations:")
    for rec in analytics["energy_optimization"]:
        st.write(f"- **{rec['action']}** ({rec['suggested_value']})")

    if analytics["alerts"]:
        st.error("Alerts:")
        for alert in analytics["alerts"]:
            st.write(f"- {alert}")
    else:
        st.success("No critical alerts detected.")

    st.markdown("---")
    st.markdown("## 🔁 Closed-Loop Optimization")
    opt = run_closed_loop_optimization(df)
    st.write(
        f"**Recommended Furnace Temp Setpoint:** {opt['furnace_temp_setpoint']:.1f}°C"
    )
    st.info(opt["reason"])

    st.markdown("---")
    st.markdown("## 📋 AI-Driven SOP Recommendation")
    sop = run_ai_sop_recommendation(df)
    st.success(sop)

    st.markdown("---")
    st.markdown("## 👷 Digital Worker Assistant (NLP Q&A)")
    user_query = st.text_input("Ask a question about alerts, KPIs, or trends:")
    if user_query and not df.empty:
        resp = digital_worker_assistant(user_query, df)
        st.info(resp)

else:
    st.stop()

st.caption("Offline Digital Twin | Visual KPIs, Trends, Optimization, and Digital Worker Assistant.")
