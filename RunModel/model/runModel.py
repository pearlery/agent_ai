import os
import joblib
import pandas as pd
from model.convert_input_format import convert_input_format
from model.MatchMitre import optimized_match

# Load the trained pipeline only once (on import)
model_path = os.getenv("MODEL_PATH", "./model/model80.pkl")
pipeline = joblib.load(model_path)

# Expected input columns
expected_columns = [
    'severity', 'alert_status', 'log_source', 'tags', 'objectMarking',
    'alert_name', 'sla_mttv', 'hostname', 'endpoint_type', 'os', 'src_ip'
]

def predict_top7_labels(input_df: pd.DataFrame) -> dict:
    """
    Predicts top-7 labels per output (tactic, technique, subtechnique) 
    for a single input record in DataFrame format. Filters results by confidence ≥ 0.05.

    Args:
        input_df (pd.DataFrame): A DataFrame with exactly one row and expected columns.

    Returns:
        dict: Dictionary with 'tactic', 'technique', and 'subtechnique' keys.
              Each value is a list of (label, score) tuples.
    """
    if not isinstance(input_df, pd.DataFrame):
        input_df = pd.DataFrame(input_df)

    if input_df.shape[0] != 1:
        raise ValueError("Input DataFrame must contain exactly one row.")

    missing_cols = [col for col in expected_columns if col not in input_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    input_df = input_df[expected_columns]

    # Predict probabilities (multi-output)
    probas = pipeline.predict_proba(input_df)

    # Extract label sets
    tactic_labels = pipeline.classes_[0]
    technique_labels = pipeline.classes_[1]
    subtechnique_labels = pipeline.classes_[2]

    # Filter top-7 by score ≥ 0.05
    top7_results = {
        "tactic": [(label, float(score)) for label, score in sorted(zip(tactic_labels, probas[0][0]), key=lambda x: x[1], reverse=True)[:7] if score >= 0.05],
        "technique": [(label, float(score)) for label, score in sorted(zip(technique_labels, probas[1][0]), key=lambda x: x[1], reverse=True)[:7] if score >= 0.05],
        "subtechnique": [(label, float(score)) for label, score in sorted(zip(subtechnique_labels, probas[2][0]), key=lambda x: x[1], reverse=True)[:7] if score >= 0.05],
    }

    return top7_results

def clean_run_prediction(data: dict) -> dict:
    cleaned = convert_input_format(data)
    prediction = predict_top7_labels(cleaned)

    result_dict = {
        "prediction": prediction
    }

    # No need to re-parse JSON
    matched = optimized_match("./model/MitreMatch.csv", result_dict)
    return matched