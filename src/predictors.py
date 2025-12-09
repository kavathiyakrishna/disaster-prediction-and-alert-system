import numpy as np
from model_utils import load_model
from utils_db import add_alert, log_event

# Thresholds for high probability
THRESHOLDS = {
    "landslide": 0.6,
    "wildfire": 0.6,
    "cyclone": 0.5,
    "earthquake": 0.5,
    "flood": 0.6,
}

def predict(disaster: str, features_dict: dict):
    model_meta = load_model(disaster)
    if not model_meta:
        raise ValueError(f"Model for {disaster} not found. Train models first.")
    model, meta = model_meta
    feat_list = meta.get("features", [])
    X = np.array([[features_dict.get(f, 0) for f in feat_list]])

    proba = model.predict_proba(X)[0][1]
    threshold = THRESHOLDS.get(disaster, 0.6)
    alert_flag = proba >= threshold

    message = f"{disaster.capitalize()} probability {proba:.3f}"
    if alert_flag:
        add_alert(disaster, float(proba), message)
        log_event("alert_generated", f"{disaster} prob={proba}")
    else:
        log_event("prediction", f"{disaster} prob={proba}")

    return {
        "probability": float(proba),
        "threshold": threshold,
        "alert": alert_flag,
        "message": message
    }
