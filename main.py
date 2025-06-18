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

    # KPIs as metrics and table
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Furnace Temp (°C)", f"{kpis['mean_furnace_temp']:.1f}")
    col2.metric("Power Usage (kWh)", f"{kpis['mean_power_usage']:.1f}")
    col3.metric("Gas Cons. (Nm³)", f"{kpis['mean_gas_consumption']:.1f}")
    col4.metric("Water Usage (m³)", f"{kpis['mean_water_usage']:.2f}")

    col5, col6, col7 = st.columns(3)
    col5.metric("Scrap Rate (%)", f"{kpis['mean_scrap_rate']:.2f}")
    col6.metric("Downtime (%)", f"{kpis['downtime_pct']:.2f}")
    col7.metric("Runtime (%)", f"{kpis['runtime_pct']:.2f}")

    with st.expander("Show All KPIs (Table)"):
        st.table(pd.DataFrame([kpis]))

    st.markdown("---")
    st.markdown("## 📈 Trends & Distributions")

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

    # Predicted Scrap Rate as metric
    st.metric(
        "Predicted Scrap Rate (%)",
        f"{analytics['predicted_scrap_rate']:.2f}"
        if isinstance(analytics['predicted_scrap_rate'], (int, float))
        else analytics['predicted_scrap_rate']
    )

    # KPIs table again for completeness in Insights section (optional, can remove if redundant)
    # st.table(pd.DataFrame([analytics["kpis"]]))

    # Energy Optimization Recommendations as Table
    st.subheader("Energy Optimization Recommendations")
    if analytics["energy_optimization"]:
        st.table(pd.DataFrame(analytics["energy_optimization"]))
    else:
        st.info("No energy optimization recommendations at this time.")

    # Alerts as Highlighted List or Table
    st.subheader("Alerts")
    if analytics["alerts"]:
        for alert in analytics["alerts"]:
            st.error(f"⚠️ {alert}")
    else:
        st.success("No critical alerts detected.")

    # Optionally, show all Insights & Optimization data as a comprehensive dashboard/table
    with st.expander("View Full Analytics as Dashboard Table"):
        # Combine all main analytics into a single dashboard format
        dashboard_dict = analytics["kpis"].copy()
        dashboard_dict["predicted_scrap_rate"] = analytics["predicted_scrap_rate"]
        st.table(pd.DataFrame([dashboard_dict]))
        st.write("### Energy Optimization Recommendations")
        st.table(pd.DataFrame(analytics["energy_optimization"]))
        st.write("### Alerts")
        if analytics["alerts"]:
            st.table(pd.DataFrame({"Alerts": analytics["alerts"]}))
        else:
            st.write("No critical alerts.")

    # For transparency, allow expanding to see raw JSON if desired
    with st.expander("View Full Analytics JSON"):
        st.json(analytics)

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
