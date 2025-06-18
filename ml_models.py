import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def predict_scrap_rate(df: pd.DataFrame):
    features = ["furnace_temp", "power_usage", "gas_consumption", "cycle_time", "die_temp"]
    if all(f in df.columns for f in features) and len(df) > 10:
        X = df[features].fillna(df[features].mean())
        y = ((df["material_input"] - df["production_output"]) / df["material_input"]).fillna(0)
        model = RandomForestRegressor()
        model.fit(X, y)
        pred = model.predict(X)
        return float(pred.mean()) * 100
    return "Insufficient data for prediction."

def recommend_optimizations(df: pd.DataFrame):
    recs = []
    if df["power_usage"].mean() > 130:
        recs.append({"action": "Reduce power usage", "suggested_value": "<130 kWh"})
    if df["gas_consumption"].mean() > 70:
        recs.append({"action": "Reduce gas consumption", "suggested_value": "<70 Nm3/hr"})
    if (df["material_input"] - df["production_output"]).mean() > 15:
        recs.append({"action": "Reduce scrap", "suggested_value": "Target <15 kg per batch"})
    if not recs:
        recs.append({"action": "No critical optimizations needed", "suggested_value": "Maintain current parameters"})
    return recs
