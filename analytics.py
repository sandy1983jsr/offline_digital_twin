import pandas as pd
from ml_models import predict_scrap_rate, recommend_optimizations

def get_sample_data():
    # Generates a sample DataFrame similar to forging batch records
    # 20 rows, values are randomized but realistic for forging operations
    import numpy as np
    np.random.seed(42)
    n = 20
    df = pd.DataFrame({
        "furnace_temp": np.random.uniform(1150, 1250, n),
        "power_usage": np.random.uniform(100, 150, n),
        "gas_consumption": np.random.uniform(50, 80, n),
        "water_usage": np.random.uniform(0.8, 1.2, n),
        "material_input": np.random.uniform(500, 600, n),
        "production_output": lambda d: d["material_input"] - np.random.uniform(10, 20, n),
        "downtime": np.random.uniform(0, 0.2, n),
        "runtime": lambda d: 1 - d["downtime"],
        "cycle_time": np.random.uniform(1, 4, n),
        "die_temp": np.random.uniform(200, 400, n),
    })
    df["production_output"] = df["material_input"] - np.random.uniform(10, 20, n)
    df["runtime"] = 1 - df["downtime"]
    return df

def run_full_analytics(df: pd.DataFrame):
    kpis = {
        "mean_furnace_temp": df["furnace_temp"].mean(),
        "mean_power_usage": df["power_usage"].mean(),
        "mean_gas_consumption": df["gas_consumption"].mean(),
        "mean_water_usage": df["water_usage"].mean(),
        "mean_scrap_rate": ((df["material_input"] - df["production_output"]) / df["material_input"]).mean() * 100,
        "downtime_pct": df["downtime"].mean() * 100 if "downtime" in df else None,
        "runtime_pct": df["runtime"].mean() * 100 if "runtime" in df else None,
    }
    scrap_pred = predict_scrap_rate(df)
    energy_opt = recommend_optimizations(df)
    return {
        "kpis": kpis,
        "predicted_scrap_rate": scrap_pred,
        "energy_optimization": energy_opt,
        "alerts": _basic_alerts(df, kpis)
    }

def _basic_alerts(df, kpis):
    alerts = []
    if kpis["mean_scrap_rate"] > 5:
        alerts.append("High average scrap rate detected.")
    if kpis["mean_power_usage"] > 140:
        alerts.append("High power usage.")
    if kpis["mean_gas_consumption"] > 75:
        alerts.append("Gas usage above optimal.")
    return alerts

def run_closed_loop_optimization(df: pd.DataFrame):
    kpis = run_full_analytics(df)["kpis"]
    oee = kpis.get("runtime_pct", 80)
    scrap = kpis.get("mean_scrap_rate", 2)
    curr_setpoint = kpis.get("mean_furnace_temp", 1200)
    rec = {}
    if oee < 80:
        rec["furnace_temp_setpoint"] = curr_setpoint + 10
        rec["reason"] = "OEE low, slight increase in temperature"
    elif scrap > 3:
        rec["furnace_temp_setpoint"] = curr_setpoint - 10
        rec["reason"] = "Scrap rate high, slight decrease in temperature"
    else:
        rec["furnace_temp_setpoint"] = curr_setpoint
        rec["reason"] = "Current settings optimal"
    return rec

def run_ai_sop_recommendation(df: pd.DataFrame):
    scrap_trend = df["material_input"] - df["production_output"]
    if (scrap_trend > 15).sum() > 2:
        return "Review material input quality and adjust process parameters to reduce scrap."
    if "downtime" in df and df["downtime"].mean() > 0.15:
        return "High downtime detected. Review maintenance schedules and operator SOP."
    return "Process is stable. Maintain current SOP, but monitor trends."

def digital_worker_assistant(query: str, df: pd.DataFrame):
    q = query.lower()
    if "scrap" in q:
        return f"Average scrap rate is {((df['material_input'] - df['production_output']) / df['material_input']).mean() * 100:.2f}%"
    if "oee" in q or "uptime" in q:
        return f"Average runtime is {df['runtime'].mean() * 100:.1f}%"
    if "recommend" in q or "improve" in q:
        return run_ai_sop_recommendation(df)
    return "I'm your digital assistant. Ask about scrap, downtime, optimization or best practices!"
