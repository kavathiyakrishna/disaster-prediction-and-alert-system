# Utilities for saving/loading sklearn models and columns
import pickle
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def save_model(name: str, model, meta: dict = None):
    path = os.path.join(MODELS_DIR, f"{name}_model.pkl")
    with open(path, "wb") as f:
        pickle.dump({"model": model, "meta": meta or {}}, f)

def load_model(name: str):
    path = os.path.join(MODELS_DIR, f"{name}_model.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["model"], data.get("meta", {})
