from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class LoadConfig:
    """Load the config for an iteration, from the YAML file"""

    data: str
    processor: str
    prompt: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int

    @classmethod
    def from_yaml(cls, path: Path, iteration_name: str) -> "LoadConfig":
        """
        We parse the YAML file, and return a dict of the 'iteration_name' params.

        Output Example:

            LoadConfig(data='test', prompt='naive', model='meta/llama-3.3-70b-instruct', temperature=0.1, top_p=0.9, max_tokens=8192)

        """

        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            try:
                config_file = yaml.safe_load(f)
                params = config_file["iterations"][iteration_name]
                # Load all the params at once
                # The keys must have the same name as the class attributes
                return cls(**params)  # OP
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {path}") from e
