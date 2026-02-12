# Disaster Prediction & Alert System

## Overview

This project is a **Streamlit-based Disaster Prediction & Alert System** that uses machine learning models to predict the likelihood of various natural disasters and log alerts in a local database. The system supports multiple disaster types (earthquake, flood, cyclone, wildfire, landslide) and provides a simple UI for dataset management, prediction, and alert tracking.

The goal of the project is to demonstrate an end‑to‑end ML pipeline:

* data ingestion
* model training
* prediction
* alert logging
* user interaction through a web interface

This is not a production‑ready early‑warning system, but a functional prototype suitable for academic projects, demos, or further extension.

---

## Key Features

* Streamlit web interface
* Multiple disaster predictors
* Pretrained ML models loaded on demand
* Dataset upload and tracking
* Alert logging and history
* SQLite database for persistence
* Basic authentication support (bcrypt)

---

## Tech Stack

**Frontend / UI**

* Streamlit

**Backend / Logic**

* Python 3
* Pandas
* Scikit‑learn (models)

**Database**

* SQLite (`disaster_alert.db`)

**Security**

* bcrypt (password hashing)

---

## Project Structure

```
disaster-alert-system/
│
├── data/
│   ├── earthquake_dataset.csv
│   ├── flood_dataset.csv
│   ├── cyclone_dataset.csv
│   ├── wildfire_dataset.csv
│   └── landslide_dataset.csv
│
├── models/
│   └── (trained ML models saved here)
│
├── src/
│   ├── app.py              # Streamlit application entry point
│   ├── train_models.py     # Model training scripts
│   ├── predictors.py       # Prediction logic per disaster type
│   ├── model_utils.py      # Model loading utilities
│   ├── utils_db.py         # Database helper functions
│   └── db_init.py          # Database initialization
│
├── disaster_alert.db       # SQLite database
├── requirements.txt        # Python dependencies
└── README.md
```

---

## How It Works

1. **Data**

   * Disaster‑specific CSV datasets are stored in the `data/` directory.

2. **Model Training**

   * `train_models.py` trains ML models for each disaster type and saves them in `models/`.

3. **Prediction**

   * `predictors.py` selects the appropriate model and performs predictions.
   * `model_utils.py` handles loading serialized models.

4. **Web App**

   * `app.py` provides the Streamlit UI for interacting with the system.
   * Users can upload datasets, run predictions, and generate alerts.

5. **Database**

   * SQLite stores datasets, alerts, and logs using helper functions in `utils_db.py`.

---

## Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd disaster-alert-system
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Initialize the database (if needed)**

```bash
python src/db_init.py
```

---

## Running the Application

```bash
streamlit run src/app.py
```

Then open the provided local URL in your browser.

---

## Limitations (Be Honest)

* Models are only as good as the datasets provided
* No real‑time sensor or API integration
* No automated alert delivery (SMS, email, etc.)
* Security is minimal and not production‑grade
* SQLite limits scalability

This is a **prototype**, not a real disaster‑warning system.

---

## Possible Improvements

* Integrate live data APIs (weather, seismic feeds)
* Replace SQLite with PostgreSQL or MongoDB
* Add role‑based authentication
* Improve model evaluation and validation
* Deploy with Docker and cloud hosting
* Add real alert channels (SMS, email, push notifications)

---

## Intended Use

* Academic projects
* ML pipeline demonstrations
* Disaster analytics prototypes



