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


@dataclass
class RolePrompting(Prompts):
    """Class for the Role prompting prompt"""

    def render(self, data: str) -> str:
        return f"""
User: From now on, you are an experienced and highly analytical **Application Security Engineer** with deep expertise in secure software analysis and vulnerability discovery. Your specialty is identifying complex inter-procedural and intra-procedural vulnerabilities in Python code, especially related to data flow, taint analysis, and identifying **sources** (user-controlled inputs) and **sinks** (dangerous execution points).

You will be shown Python code or code representations in different formats (e.g., ASTs, IR, pseudocode, or raw Python). Your task is to:
- Analyze the code for security vulnerabilities involving data flow from sources to sinks
- Precisely identify **confirmed user-controlled sources** (e.g., function parameters, input handlers)
- Precisely identify **confirmed dangerous sinks** (e.g., code execution, file access, command injection)
- Ensure inter-procedural flows are considered when analyzing the paths

Your output must be strictly in the following JSON format:

```json
{{"confirmed_sinks": [
    "os.system",
    "subprocess.call"
    // ... only confirmed dangerous sinks
  ],
  "confirmed_sources": [
    {{"function": "run", "parameter": "username" }},
    {{"function": "process", "parameter": "filename" }}
    // ... only confirmed user-controlled sources
  ]
}}

**Do not say anything else. Do not wrap the output in a code block. Do not include any text before or after. Output must be a raw JSON object only.**

Assistant: Understood. As an Application Security Engineer, I will thoroughly examine the provided code representations to identify confirmed user-controlled sources and dangerous sinks. I will trace both intra-procedural and inter-procedural data flows to determine whether untrusted input can reach sensitive operations. Only those elements I can confirm based on the given code will be included in the final output. I will output my findings using raw JSON object ONLY, listing confirmed sources (function name and parameter) and confirmed sinks (fully qualified dangerous functions). Please provide the code you'd like me to analyze.

User: Here is the code you must analyze

{data}
"""


# This prompt dict allows us to load these prompts from the YAML config file
PROMPTS_DICT: dict[str, type[Prompts]] = {
    "naive": NaivePrompt,
    "role_prompting": RolePrompting,
}
