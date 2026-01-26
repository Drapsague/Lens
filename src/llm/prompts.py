from dataclasses import dataclass
from abc import ABC, abstractmethod


class Prompts(ABC):
    """Abstract Class that holds different prompts"""

    @abstractmethod
    def render(self, data: str) -> str:
        """To render the prompts"""
        raise NotImplementedError()


@dataclass
class NaivePrompt(Prompts):
    """Class for the Naive prompt"""

    def render(self, data: str) -> str:
        return f"""
I have extracted two CSV files from a Python Codebase. 
Analyze them and identify:
1. Dangerous Sinks (SQL Injection, Command Injection, Code Injection).
2. User-Controlled Sources (Entry points functions).
3. STRICTLY return a single JSON object. Do not include markdown formatting or explanations outside the JSON.

        **Required JSON Output Format:**
        {{"confirmed_sinks": [
            "os.system",
            "subprocess.call"
            // ... add only confirmed dangerous sinks
          ],
          "confirmed_sources": [
            {{"function": "run", "parameter": "username" }},
            {{"function": "process", "parameter": "filename" }}
            // ... add only confirmed user-controlled sources
          ]
        }}
JSON_FILE:
{data}
"""


# This prompt dict allows us to load these prompts from the YAML config file
PROMPTS_DICT: dict[str, Prompts] = {"naive": NaivePrompt()}
