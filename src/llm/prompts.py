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

{data}
"""
