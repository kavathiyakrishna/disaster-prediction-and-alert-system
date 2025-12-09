import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, roc_auc_score, make_scorer
from model_utils import save_model

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def train_generic(csv_path, features, label_col="label", model_name="model"):
    print("\n==============================")
    print(f" Training: {model_name}")
    print("==============================")

    df = pd.read_csv(csv_path)
    df = df.dropna()
    print("Label distribution:", df[label_col].value_counts().to_dict())

    if df[label_col].dtype == "object":
        df[label_col] = df[label_col].astype("category").cat.codes

    X = df[features]
    y = df[label_col].astype(int)

    # Stratified split
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        print("⚠ Stratified split failed: dataset may contain only one class!")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    # Hyperparameter grid
    param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
    }

    # Optimize for AUC
    auc_scorer = make_scorer(roc_auc_score, needs_proba=True)

    clf = GridSearchCV(
        RandomForestClassifier(random_state=42, class_weight="balanced", n_jobs=-1),
        param_grid,
        cv=StratifiedKFold(n_splits=5),
        scoring=auc_scorer,
        n_jobs=-1
    )

    clf.fit(X_train, y_train)

    best_model = clf.best_estimator_
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"{model_name} trained. Test Accuracy: {acc:.2%}")

    auc = None
    if len(set(y_test)) > 1:
        try:
            proba = best_model.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, proba)
        except Exception:
            pass
    if auc:
        print(f"Test AUC: {auc:.3f}")

    # Save model with accuracy and auc
    save_model(model_name, best_model, meta={"features": features, "accuracy": acc, "auc": auc})
    return best_model


def main():
    datasets = [
        ("landslide_dataset.csv", ["rainfall_mm", "slope_degree", "soil_moisture",
                                  "population_density", "infrastructure_index"], "landslide"),
        ("wildfire_dataset.csv", ["temperature_c", "humidity_pct", "vegetation_index",
                                  "soil_moisture", "population_density"], "wildfire"),
        ("cyclone_dataset.csv", ["wind_speed_kmph", "pressure_hpa", "humidity_pct",
                                 "tide_height_m", "population_density"], "cyclone"),
        ("earthquake_dataset.csv", ["magnitude", "depth_km", "population_density",
                                    "infrastructure_index", "historical_quakes_50km",
                                    "aftershock_risk_score"], "earthquake"),
        ("flood_dataset.csv", ["rainfall_mm", "river_level_m", "soil_moisture",
                               "population_density", "infrastructure_index"], "flood"),
    ]

    for csv_name, features, model_name in datasets:
        csv_path = os.path.join(DATA_DIR, csv_name)
        if os.path.exists(csv_path):
            train_generic(csv_path, features, model_name=model_name)
        else:
            print("Missing", csv_path)


if __name__ == "__main__":
    main()
