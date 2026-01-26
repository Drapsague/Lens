from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import json


class DataProcessor(ABC):
    """Abstract Class that holds different data processing classes"""

    def write_file(self, path: Path, data):
        with open(path / "clean_context_data.json", "w", encoding="utf-8") as f:
            f.write(data)

    @abstractmethod
    def process(self, working_dir: Path) -> str:
        """To process the data"""
        raise NotImplementedError()


@dataclass
class BasicCSVProcessing(DataProcessor):
    """
    Perform a basic processing
    Only on two files hardcoded: external_apis.csv and internal_functions.csv
    """

    def process(self, working_dir: Path) -> str:
        apis_df = pd.read_csv(working_dir / "external_apis.csv").fillna(value="")
        funcs_df = pd.read_csv(working_dir / "internal_functions.csv").fillna(value="")
        # Concat both CSV files
        json_data = {
            "internal_functions": funcs_df.to_dict(orient="records"),
            "external_apis": apis_df.to_dict(orient="records"),
        }

        return json.dumps(json_data, indent=2)


# This processor dict allows us to use different processing techniques upon our iterations
PROCESSOR_REGISTRY: dict[str, type[DataProcessor]] = {"basic": BasicCSVProcessing}
