# Disaster Prediction & Alert System

## Overview
Web app (Streamlit) + backend ML models to predict 5 disaster types:
- Landslide
- Wildfire
- Cyclone
- Earthquake
- Flood

Features:
- Train models from CSVs
- Admin login and dataset management (upload/delete)
- Predict UI: pick disaster, enter fields, get probability & alert
- SQLite DB for users, logs, alerts
- Real-time-ish alerts using periodic refresh
- Attractive dashboard with charts

## Quick start
1. Put your CSVs in `data/` with these filenames:
   - `landslide_dataset.csv`
   - `wildfire_dataset.csv`
   - `cyclone_dataset.csv`
   - `earthquake_dataset.csv`
   - `flood_dataset.csv`

2. Create virtualenv, install:
