import streamlit as st
import pandas as pd
from pathlib import Path
import sqlite3
import base64
import os
import bcrypt

from utils_db import add_dataset, list_datasets, log_event, list_alerts, add_alert
from predictors import predict
from model_utils import load_model

# ----------------------------
# PATH CONFIG
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "disaster_alert.db"

# ----------------------------
# STREAMLIT CONFIG
# ----------------------------
st.set_page_config(
    page_title="Disaster Management & Alert System",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# LIGHT WHITE/LIGHT-GRAY THEME
# ----------------------------
st.markdown("""
<style>
body, .block-container {background-color: #ffffff; color: #000000;}
[data-testid="stSidebar"] {background-color: #f8f9fa; color: #000000;}
h1, h2, h3, h4, h5, h6, p {color: #000000;}
.stButton>button {background-color: #ffffff; color: #000000; border: 1px solid #ccc;}
.stMetric {color: #000000;}
.stDataFrame, .stFrame {background-color: #ffffff; color: #000000;}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# ADMIN AUTH HELPERS
# ----------------------------
def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id,username,password_hash,role FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def require_admin():
    return st.session_state.get("admin_user")

def admin_login_form():
    st.subheader("Admin Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        row = get_user(uname)
        if row and bcrypt.checkpw(pwd.encode(), row[2]):
            st.session_state["admin_user"] = {
                "id": row[0],
                "username": row[1],
                "role": row[3]
            }
            st.success("Logged in successfully.")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# ----------------------------
# SIDEBAR
# ----------------------------
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Admin", "Alerts"]
)

# ----------------------------
# BRANDING HEADER
# ----------------------------
logo_path = BASE_DIR / "src" / "assets" / "logo.png"
if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
else:
    logo_b64 = ""

st.markdown(f"""
<div style="display:flex; align-items:center; padding:10px 0;">
    <img src="data:image/png;base64,{logo_b64}" height="60">
    <div style="margin-left: 16px;">
        <h1 style="margin:0; color:#222;">Disaster Management & Alert System</h1>
        <p style="margin:0; color:#555;">AI-powered prediction and admin-controlled alerts</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# HOME PAGE
# ----------------------------
if menu == "Home":
    st.header("Home Dashboard")

    # Admin alerts
    st.subheader("Recent Alerts")
    alerts = list_alerts(unhandled_only=False)
    if alerts:
        for i, a in enumerate(alerts):
            aid, disaster, prob, msg, ts, handled = a
            row_color = "#ffffff" if i % 2 == 0 else "#f2f2f2"

            col1, col2 = st.columns([1, 5])  # Left side delete button
            with col1:
                if st.button("Delete", key=f"delete_{aid}"):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("DELETE FROM alerts WHERE id=?", (aid,))
                    conn.commit()
                    conn.close()
                    st.experimental_rerun()
            with col2:
                st.markdown(f"""
                    <div style='border:1px solid #ccc; padding:10px; margin-bottom:8px; border-radius:8px; background-color:{row_color}'>
                        <b>Disaster:</b> {disaster.capitalize()}<br>
                        <b>Message:</b> {msg}<br>
                        <b>Probability:</b> {prob:.2%}<br>
                        <b>Timestamp:</b> {ts}<br>
                        <b>Handled:</b> {'Yes' if handled else 'No'}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No alerts yet.")

    st.markdown("---")

    # Disaster prediction
    st.subheader("Predict Disaster Risk")
    disaster = st.selectbox("Select disaster type", ["landslide", "wildfire", "cyclone", "earthquake", "flood"])
    model, meta = load_model(disaster) or (None, {})
    if model is None:
        st.warning("Model missing. Train your models using train_models.py.")
    else:
        features = meta.get("features", [])
        model_acc = meta.get("accuracy", None)
        cols = st.columns(2)
        values = {}
        for i, feat in enumerate(features):
            values[feat] = cols[i % 2].number_input(f"{feat}", value=0.0)
        if st.button("Predict"):
            res = predict(disaster, values)
            prob = res["probability"]

            st.metric("Prediction Probability", f"{prob:.2%}")
            if model_acc:
                st.metric("Model Accuracy", f"{model_acc:.2%}")

            if res["alert"]:
                st.error(f"🚨 HIGH RISK — {res['message']}")
            else:
                st.success(f"Safe — {res['message']}")

# ----------------------------
# ADMIN PAGE
# ----------------------------
elif menu == "Admin":
    if not require_admin():
        admin_login_form()
    else:
        st.header("Admin Dashboard")
        st.markdown(f"**Logged in as:** {st.session_state['admin_user']['username']}")
        st.markdown("---")

        # Send manual alert
        st.subheader("Send Manual Alert")
        md = st.selectbox("Disaster type", ["landslide", "wildfire", "cyclone", "earthquake", "flood"])
        mp = st.number_input("Probability", min_value=0.0, max_value=1.0, step=0.01)
        mm = st.text_input("Alert message", value=f"{md.capitalize()} alert")
        if st.button("Send Alert"):
            add_alert(md, mp, mm)
            log_event("manual_alert", f"{md}, prob={mp}, msg={mm}")
            st.success("Alert sent successfully.")

        st.markdown("---")

        # Dataset management
        st.subheader("Dataset Management")
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded:
            fname = uploaded.name
            path = DATA_DIR / fname
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())
            add_dataset(fname.replace(".csv", ""), fname)
            log_event("dataset_upload", fname)
            st.success("Dataset uploaded successfully.")

        st.markdown("### Existing Datasets")
        rows = list_datasets()
        if rows:
            for i, row in enumerate(rows):
                row_color = "#ffffff" if i % 2 == 0 else "#f2f2f2"
                col1, col2 = st.columns([1,5])
                with col1:
                    if st.button("Delete", key=f"delete_dataset_{row[2]}"):
                        file_path = DATA_DIR / row[2]
                        try:
                            if file_path.exists():
                                os.remove(file_path)
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("DELETE FROM datasets WHERE filename=?", (row[2],))
                            conn.commit()
                            conn.close()
                            log_event("dataset_delete", row[2])
                            st.success(f"{row[2]} deleted successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error deleting dataset: {e}")
                with col2:
                    st.markdown(f"""
                        <div style='border:1px solid #ccc; padding:10px; margin-bottom:4px; border-radius:6px; background-color:{row_color}'>
                            <b>Name:</b> {row[1]} | <b>Filename:</b> {row[2]} | <b>Uploaded:</b> {row[3]}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No datasets uploaded.")

# ----------------------------
# ALERTS PAGE
# ----------------------------
elif menu == "Alerts":
    st.header("All Alerts")
    alerts = list_alerts(unhandled_only=False)
    if alerts:
        for i, a in enumerate(alerts):
            aid, disaster, prob, msg, ts, handled = a
            row_color = "#ffffff" if i % 2 == 0 else "#f2f2f2"

            col1, col2 = st.columns([1,5])
            with col1:
                if st.button("Delete", key=f"alert_delete_{aid}"):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("DELETE FROM alerts WHERE id=?", (aid,))
                    conn.commit()
                    conn.close()
                    st.experimental_rerun()
            with col2:
                st.markdown(f"""
                    <div style='border:1px solid #ccc; padding:10px; margin-bottom:8px; border-radius:8px; background-color:{row_color}'>
                        <b>Disaster:</b> {disaster.capitalize()}<br>
                        <b>Message:</b> {msg}<br>
                        <b>Probability:</b> {prob:.2%}<br>
                        <b>Timestamp:</b> {ts}<br>
                        <b>Handled:</b> {'Yes' if handled else 'No'}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No alerts available.")

