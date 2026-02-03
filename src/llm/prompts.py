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


@dataclass
class FewShot(Prompts):
    """Class for the Few-Shot prompt"""

    def render(self, data: str) -> str:
        return f"""
You are an expert code analysis assistant specialized in application security. 
You are given structured data about internal functions and external APIs used in a codebase. 

Your task is to correlate internal function parameters and API usage to identify:

  - Sources: function parameters that may receive user-controlled input 
             (e.g., `filename`, `query`, `input`, etc.)

  - Sinks: dangerous or sensitive operations 
           (e.g., `eval`, `exec`, `os.system`, SQL execution functions, etc.)

**IMPORTANT RULES:**
  - Only confirm a source or sink if it can be directly inferred from the data.
  - NEVER invent or assume a source or sink.
  - Your output must be a JSON object in the following format:

{{  
  "confirmed_sinks": [ list of dangerous sink function names ],
  "confirmed_sources": [ {{ "function": "...", "parameter": "..." }} ]
}}

---

## Example 1: SQL Injection

Input:
{{
  "internal_functions": [
    {{
      "filename": "user_data.py",
      "linenumber": 12,
      "funcname": "get_user_by_name",
      "funcparams": "request, name",
      "decorators": "app.route",
      "docstring": ""
    }}
  ],
  "external_apis": [
    {{
      "filename": "user_data.py",
      "linenumber": 2,
      "extapis": "django.db.connection.cursor"
    }}
  ]
}}

Output:
{{
  "confirmed_sinks": [
    "django.db.connection.cursor"
  ],
  "confirmed_sources": [
    {{
      "function": "get_user_by_name",
      "parameter": "name"
    }}
  ]
}}

---

## Example 2: Command Injection

Input:
{{
  "internal_functions": [
    {{
      "filename": "run_cmd.py",
      "linenumber": 6,
      "funcname": "execute_command",
      "funcparams": "request, cmd",
      "decorators": "app.route",
      "docstring": ""
    }}
  ],
  "external_apis": [
    {{
      "filename": "run_cmd.py",
      "linenumber": 3,
      "extapis": "os.system"
    }}
  ]
}}

Output:
{{
  "confirmed_sinks": [
    "os.system"
  ],
  "confirmed_sources": [
    {{
      "function": "execute_command",
      "parameter": "cmd"
    }}
  ]
}}

---

## Example 3: Unsafe Deserialization

Input:
{{
  "internal_functions": [
    {{
      "filename": "deserialize.py",
      "linenumber": 9,
      "funcname": "load_data",
      "funcparams": "request, raw_data",
      "decorators": "",
      "docstring": ""
    }}
  ],
  "external_apis": [
    {{
      "filename": "deserialize.py",
      "linenumber": 2,
      "extapis": "pickle.loads"
    }}
  ]
}}

Output:
{{
  "confirmed_sinks": [
    "pickle.loads"
  ],
  "confirmed_sources": [
    {{
      "function": "load_data",
      "parameter": "raw_data"
    }}
  ]
}}


## Now you must analyze the following:

Input:
{data}

Output:
"""


@dataclass
class ChainOfThought(Prompts):
    """Class for the COT prompt"""

    def render(self, data: str) -> str:
        return f"""
You are an expert code analysis assistant specialized in application security.

You are given structured input that contains:
  - internal_functions: definitions of internal code functions, including their parameters.
  - external_apis: external or built-in APIs used in the code.

Your job is to:
  - Identify function parameters that represent **user-controlled input** (sources).
  - Identify usage of **dangerous APIs or functions** (sinks).
  - Explain your reasoning step-by-step before giving the final output.

[!] Only use what is present in the input. Never invent or assume a source or sink.

Follow this structure:

1. For each internal function:
   - Check if it accepts parameters that look like user input (e.g., 'request', 'filename', 'query', etc.).
   - Mark these as potential sources.

2. For each external API:
   - Check if it is a known sink (e.g., os.system, eval, pickle.loads, SQL execution, etc.).
   - If yes, mark it as a confirmed sink.

3. Try to correlate function parameters (sources) to the same file where dangerous APIs (sinks) appear.

**Think step-by-step internally before answering, but DO NOT include your reasoning in the output.**

Your final output must be ONLY the following JSON structure:
{{  
  "confirmed_sinks": [ list of dangerous sink function names ],
  "confirmed_sources": [ {{ "function": "...", "parameter": "..." }} ]
}}

---

## Example 1: SQL Injection

Input:
{{
  "internal_functions": [
    {{
      "filename": "user_data.py",
      "linenumber": 12,
      "funcname": "get_user_by_name",
      "funcparams": "request, name",
      "decorators": "app.route",
      "docstring": ""
    }}
  ],
  "external_apis": [
    {{
      "filename": "user_data.py",
      "linenumber": 2,
      "extapis": "django.db.connection.cursor"
    }}
  ]
}}


Output:
{{
  "confirmed_sinks": [
    "django.db.connection.cursor"
  ],
  "confirmed_sources": [
    {{
      "function": "get_user_by_name",
      "parameter": "name"
    }}
  ]
}}

---

## Example 2: Command Injection

Input:
{{
  "internal_functions": [
    {{
      "filename": "runner.py",
      "linenumber": 8,
      "funcname": "run_tool",
      "funcparams": "request, tool_name",
      "decorators": "app.route",
      "docstring": ""
    }}
  ],
  "external_apis": [
    {{
      "filename": "runner.py",
      "linenumber": 3,
      "extapis": "subprocess.Popen"
    }}
  ]
}}

Output:
{{
  "confirmed_sinks": [
    "subprocess.Popen"
  ],
  "confirmed_sources": [
    {{
      "function": "run_tool",
      "parameter": "tool_name"
    }}
  ]
}}

---

## Now analyze the following:

Input:
{data}

Output:
"""


# This prompt dict allows us to load these prompts from the YAML config file
PROMPTS_DICT: dict[str, type[Prompts]] = {
    "naive": NaivePrompt,
    "role_prompting": RolePrompting,
    "fewshot": FewShot,
    "cot": ChainOfThought,
}
