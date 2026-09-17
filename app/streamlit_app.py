import streamlit as sl
import joblib
import numpy as np
import pandas as pd

sl.title("Clinical Trial Termination Prediction")
sl.caption("Intervention Trial Data pulled from ClinicalTrials.gov, 2010-2022")

model = joblib.load("app/model.joblib")
cols = joblib.load("app/feature_names.joblib")

col1, col2 = sl.columns(2)
with col1:
    phase = sl.selectbox("Phase", ["PHASE1", "PHASE2", "PHASE3", "PHASE4", "EARLY_PHASE1", "NA"])
    sites = sl.number_input("Number of sites", 1, 500, 5)
    countries = sl.number_input("Number of countries", 1, 50, 1)
    collaborators = sl.number_input("Number of collaborators", 0, 50, 0)
    criteria_len = sl.number_input("Eligibility criteria length (char count)", 50, 10000, 1500)
with col2:
    sponsor = sl.selectbox("Sponsor class", 
                           ["INDUSTRY", "OTHER", "NIH", "OTHER_GOV", "NETWORK", "FED", "INDIV"])
    randomized = sl.checkbox("Randomized", value=True)
    masked = sl.checkbox("Masked/Blinded", value=True)
    healthy_vols = sl.checkbox("Accepts healthy volunteers", value=False)
    
#popluate features with user input
row = pd.DataFrame(np.zeros((1, len(cols))), columns=cols)
row["log_sites"] = np.log1p(sites)
row["countries_count"] = countries
row["log_collaborators"] = np.log1p(collaborators)
row["criteria_len"] = criteria_len

row["multi_site"] = int(sites > 1)
row["multi_national"] = int(countries > 1)
row["has_collab"] = int(collaborators > 0)
row["randomized"] = int(randomized)
row["is_masked"] = int(masked)
row["healthy_volunteers"] = int(healthy_vols)

row["min_age"] = 18
row["max_age"] = 65
for col, val in [(f"phase_{phase}", 1), (f"sponsor_{sponsor}", 1)]:
    if col in row.columns:
        row[col] = val
        
prob = model.predict_proba(row)[0, 1]
sl.metric("Predicted termination probability", f"{prob:.1%}")
sl.progress(min(float(prob), 1.0))
sl.caption("Base termination rate in training data: ~11%. Personal project prototype, not a decision tool.")
