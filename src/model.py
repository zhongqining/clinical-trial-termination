import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import roc_auc_score, average_precision_score

def train():
    X = pd.read_parquet("data/processed/features.parquet")
    y = pd.read_parquet("data/processed/target.parquet")["terminated"]
    df = pd.read_parquet("data/processed/trials.parquet")

    #train pre-2018, test 2018+
    train_mask = df["start_date"].dt.year < 2018
    X_train, X_test = X[train_mask], X[~train_mask]
    y_train, y_test = y[train_mask], y[~train_mask]

    #11% positive rate, requires balanced sample weight
    weights = compute_sample_weight("balanced", y_train)
    hgb = HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.06,
        early_stopping=True, validation_fraction=0.15, random_state=42
    ).fit(X_train, y_train, sample_weight=weights)

    #evaluate
    probs = hgb.predict_proba(X_test)[:, 1]
    print(f"ROC-AUC: {roc_auc_score(y_test, probs):.3f}")
    print(f"PR-AUC:  {average_precision_score(y_test, probs):.3f}")

    joblib.dump(hgb, "app/model.joblib")
    joblib.dump(list(X.columns), "app/feature_names.joblib")
    print(f"saved hgb model ({X.shape[1]} features)")

if __name__ == "__main__":
    train()