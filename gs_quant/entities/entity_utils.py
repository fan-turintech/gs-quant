import pandas as pd

from typing import Union


def _explode_data(data: pd.Series,
                  parent_label: str) -> Union[pd.DataFrame, pd.Series]:
    parent_to_child_map = {
        "factorCategories": "factors",
        "factors": "byAsset",
        "sectors": "industries",
        "industries": None,
        "countries": None,
        "direction": None
    }

    labels_to_ignore_map = {
        "factorCategories": ["factorExposure", "estimatedPnl", "factors"],
        "factors": ["factorExposure", "estimatedPnl", "byAsset"],
        "sectors": ["exposure", "estimatedPnl", "industries"],
        "industries": [],
        "countries": [],
        "direction": [],
        "byAsset": []
    }

    data = data.rename({'name': parent_label}) if parent_label in parent_to_child_map.keys() else data
    child_label = parent_to_child_map.get(parent_label)

    if child_label and child_label in data.index.values:
        # Convert the child data to a list of dictionaries before creating the DataFrame
        child_data = data[child_label]
        if isinstance(child_data, dict):
            child_data = [child_data]  # Wrap in a list if it's a single dictionary
        child_df = pd.DataFrame(child_data)
        child_df = child_df.apply(_explode_data, axis=1, parent_label=child_label)

        data = data.drop(labels=labels_to_ignore_map.get(parent_label))
        if isinstance(child_df, pd.Series):
            child_df = pd.concat(child_df.values, ignore_index=True)
        child_df = child_df.assign(**data.to_dict())

        return child_df

    return data