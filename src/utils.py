import pandas as pd
import json
import textwrap


def encode_and_clean_to_json(apis_path: str, funcs_path: str):
    apis_df = pd.read_csv(apis_path).fillna(value="")
    funcs_df = pd.read_csv(funcs_path).fillna(value="")

    # Drop decorators for iteration 2
    # funcs_df = funcs_df.drop(columns=["decorators", "docstring"])

    # print(funcs_df.head(5).to_json(orient="records", indent=2))

    # Concat both CSV files
    json_data = {
        "internal_functions": funcs_df.to_dict(orient="records"),
        "external_apis": apis_df.to_dict(orient="records"),
    }

    return json.dumps(json_data, indent=2)
