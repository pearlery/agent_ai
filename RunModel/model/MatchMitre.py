import pandas as pd
import json

def optimized_match(csv_path: str, prediction_dict: dict) -> dict:
    full_dict = dict(prediction_dict)
    pred_dict = full_dict.get('prediction', {})

    # Load and clean CSV
    df = pd.read_csv(csv_path).fillna("")
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()
    
    tactic_candidates = [t[0] for t in pred_dict.get('tactic', [])]
    technique_candidates = set(t[0] for t in pred_dict.get('technique', []))
    subtechnique_candidates = set(t[0] for t in pred_dict.get('subtechnique', []))

    matched_rows = []

    for tactic in tactic_candidates:
        df_tactic = df[df["tactic"] == tactic]
        if df_tactic.empty:
            continue

        df_tech = df_tactic[df_tactic["technique"].isin(technique_candidates)]

        df_final = df_tech[
            ((df_tech["subtechnique"] != "") & df_tech["subtechnique"].isin(subtechnique_candidates)) |
            (df_tech["subtechnique"] == "")
        ]

        if not df_final.empty:
            for _, row in df_final.iterrows():
                matched_rows.append({
                    "tactic": row["tactic"],
                    "technique": row["technique"],
                    "subtechnique": row["subtechnique"],
                    "Detection": row["Detection"]
                })

    # Add matches to original JSON under "Mitre_Match"
    full_dict["Mitre_Match"] = matched_rows
    return full_dict    
  
  
  
# if __name__ == "__main__":
#     # === Paste your JSON string here ===
#     prediction_json = '''
#     {
#       "prediction": {
#         "tactic": [
#           [
#             "Privilege Escalation",
#             0.8073485842635361
#           ],
#           [
#             "Defense Evasion",
#             0.1913660317755721
#           ]
#         ],
#         "technique": [
#           [
#             "Abuse Elevation Control Mechanism",
#             0.9999484878515933
#           ]
#         ],
#         "subtechnique": [
#           [
#             "Bypass User Account Control",
#             0.999921352605669
#           ]
#         ]
#       }
#     }
#     '''

#     # === Set the path to your detection CSV ===
#     csv_path = "./model/MitreMatch.csv"
    
#     # Parse input string into dict
#     prediction_dict = json.loads(prediction_json)

#     # Run the matching
#     result_json = optimized_match(csv_path, prediction_json)

#     # Print final JSON with Mitre_Match included
#     print(result_json)
