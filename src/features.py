import numpy as np
import pandas as pd

CONDITION_BUCKETS = {
    "oncology":       ["cancer", "carcinoma", "tumor", "neoplasm", "lymphoma",
                       "leukemia", "melanoma", "sarcoma"],
    "cardiovascular": ["heart", "cardiac", "hypertension", "stroke", "coronary", "atrial"],
    "neuro":          ["alzheimer", "parkinson", "epilepsy", "multiple sclerosis",
                       "migraine", "neuropath"],
    "psych":          ["depression", "anxiety", "schizophrenia", "bipolar", "ptsd", "addiction"],
    "infectious":     ["hiv", "hepatitis", "influenza", "covid", "tuberculosis",
                       "malaria", "infection"],
    "metabolic":      ["diabetes", "obesity", "metabolic", "thyroid", "cholesterol"],
    "respiratory":    ["asthma", "copd", "pulmonary", "respiratory"],
    "musculoskeletal":["arthritis", "osteoporosis", "back pain", "fracture"],
}

def bucket_conditions(conditions):
    conds_text = " ".join(conditions).lower() if isinstance(conditions, (list, np.ndarray)) else "" #turns conditions into one continuous string
    for bucket, keys in CONDITION_BUCKETS.items():
        if any(k in conds_text for k in keys):
            return bucket
    return "other"

def feature_engineering(df):
    X = pd.DataFrame(index = df.index)
    
    #numerical transformations
    X["log_sites"] = np.log1p(df["sites_count"])
    X["log_collaborators"] = np.log1p(df["collaborator_count"])
    X["countries_count"] = df["countries_count"]
    X["min_age"] = df["min_age"].fillna(0)
    X["max_age"] = df["max_age"].fillna(120)
    X["criteria_len"] = df["eligibility_criteria"].str.len()
    
    #boolean flags
    X["multi_site"] = (df["sites_count"] > 1).astype(int) #multi-sites are better resourced
    X["multi_national"] = (df["countries_count"] > 1).astype(int) #multi national trials are better resourced
    X["has_collab"] = (df["collaborator_count"] > 0).astype(int) #collabs means more resources/funds
    X["randomized"] = (df["allocation"] == "RANDOMIZED").astype(int)
    X["is_masked"] = (~df["masking"].isin(["NONE", None])).astype(int)
    X["healthy_volunteers"] = (df["healthy_volunteers"]).fillna(False).astype(int)
    
    #categorical
    #one-hot encoding
    X = pd.concat([
        X,
        pd.get_dummies(df["phase"].fillna("NA"), prefix="phase"),
        pd.get_dummies(df["sponsor_class"].fillna("UNKNOWN"), prefix="sponsor"),
        pd.get_dummies(df["sex"].fillna("ALL"), prefix="sex"),
    ], axis=1)
    
    X = pd.concat([
        X,
        pd.get_dummies(df["intervention_types"].apply(
            lambda v: v[0] if isinstance(v, (list, np.ndarray)) and len(v) else "NONE"),
                       prefix="intervention"),
        pd.get_dummies(df["conditions"].apply(bucket_conditions), prefix="condition"),
    ], axis=1)
    
    return X.astype(float) #consistency between values

if __name__ == "__main__":
    df = pd.read_parquet("data/processed/trials.parquet")
    X = feature_engineering(df)
    y = df["terminated"]
    X.to_parquet("data/processed/features.parquet", index=False)
    y.to_frame().to_parquet("data/processed/target.parquet", index=False)
    print(f"features: {X.shape}, target: {y.shape}")