from re import sub
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from pathlib import Path
import textwrap

from utils import encode_and_clean_to_json, generate_qll_file


def run(iteration: int):
    apis_path = "./test/report/test_externalAPIs.csv"
    funcs_path = "./test/report/test_internalFunc.csv"
    internalFunc = Path(funcs_path).read_text(encoding="utf-8")
    externalAPIs = Path(apis_path).read_text(encoding="utf-8")

    match iteration:
        case 1:
            NAIVE_PROMPT = f"""
            I have extracted two CSV files from a Python Codebase. 
            Analyze them and identify:
            1. Dangerous Sinks (SQL Injection, Command Injection, Code Injection).
            2. User-Controlled Sources (Entry points functions).

            {externalAPIs}
            {internalFunc}
            """

            # print(NAIVE_PROMPT)

            model = ""
            try:
                llm_findings = send_prompt(
                    model="meta/llama-3.3-70b-instruct",
                    prompt=NAIVE_PROMPT,
                    max_token=8192,
                )
            except Exception as e:
                print(f"[*] Error with the model {model}: \n{e}")

            with open(
                "./test/results/naive_llm_findings.txt", "w", encoding="utf-8"
            ) as f:
                f.write(llm_findings)
        case 2:
            json_clean_data = encode_and_clean_to_json(apis_path, funcs_path)

            with open("./test/test_llm_clean_.json", "w", encoding="utf-8") as f:
                f.write(json_clean_data)

            NAIVE_PROMPT = f"""
            I have extracted two CSV files from a Python Codebase. 
            Analyze them and identify:
            1. Dangerous Sinks (SQL Injection, Command Injection, Code Injection).
            2. User-Controlled Sources (Entry points functions).

            {json_clean_data}
            """
            # print(NAIVE_PROMPT)
            model = ""
            try:
                llm_findings = send_prompt(
                    model="meta/llama-3.3-70b-instruct",
                    prompt=NAIVE_PROMPT,
                    max_token=8192,
                )
            except Exception as e:
                print(f"[*] Error with the model {model}: \n{e}")

            with open(
                "./test/results/json_clean_llm_findings.txt", "w", encoding="utf-8"
            ) as f:
                f.write(llm_findings)
            json.dump(json.loads(llm_findings), f, indent=2)

        case 3:
            json_clean_data = encode_and_clean_to_json(apis_path, funcs_path)

            with open(
                "./test/clean_data/test_llm_clean_.json", "w", encoding="utf-8"
            ) as f:
                f.write(json_clean_data)

            NAIVE_PROMPT = f"""
            I have extracted a JSON file from a Python Codebase. 
            Analyze it and identify:
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
                {{"function": "profile", "parameter": "username" }},
                {{"function": "download", "parameter": "filename" }}
                // ... add only confirmed user-controlled sources
              ]
            }}
            
            JSON_FILE:
            {json_clean_data}
            """
            # print(NAIVE_PROMPT)
            model = ""
            try:
                llm_findings = send_prompt(
                    model="meta/llama-3.3-70b-instruct",
                    prompt=NAIVE_PROMPT,
                    max_token=8192,
                )
            except Exception as e:
                print(f"[*] Error with the model {model}: \n{e}")

            with open(
                "./test/results/json_clean_llm_findings.json", "w", encoding="utf-8"
            ) as f:
                f.write(llm_findings)
            # json.dump(json.loads(llm_findings), f, indent=2)
        case 4:
            apis_path = "./target/report/externalAPIs.csv"
            funcs_path = "./target/report/internalFunc.csv"
            internalFunc = Path(funcs_path).read_text(encoding="utf-8")
            externalAPIs = Path(apis_path).read_text(encoding="utf-8")

            json_clean_data = encode_and_clean_to_json(apis_path, funcs_path)

            with open(
                "./target/clean_data/llm_clean_.json", "w", encoding="utf-8"
            ) as f:
                f.write(json_clean_data)

            NAIVE_PROMPT = f"""
            I have extracted a JSON file from a Python Codebase. 
            Analyze it and identify:
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
                {{"function": "profile", "parameter": "username" }},
                {{"function": "download", "parameter": "filename" }}
                // ... add only confirmed user-controlled sources
              ]
            }}
            
            JSON_FILE:
            {json_clean_data}
            """
            # print(NAIVE_PROMPT)
            model = ""
            try:
                llm_findings = send_prompt(
                    model="meta/llama-3.3-70b-instruct",
                    prompt=NAIVE_PROMPT,
                    max_token=8192,
                )
            except Exception as e:
                print(f"[*] Error with the model {model}: \n{e}")

            with open(
                "./target/results/json_clean_llm_findings.json", "w", encoding="utf-8"
            ) as f:
                f.write(llm_findings)
            # json.dump(json.loads(llm_findings), f, indent=2)
        case 5:
            apis_path = "./target/report/externalAPIs.csv"
            funcs_path = "./target/report/internalFunc.csv"
            internalFunc = Path(funcs_path).read_text(encoding="utf-8")
            externalAPIs = Path(apis_path).read_text(encoding="utf-8")

            json_clean_data = encode_and_clean_to_json(apis_path, funcs_path)

            with open(
                "./target/clean_data/llm_clean_.json", "w", encoding="utf-8"
            ) as f:
                f.write(json_clean_data)

            PROMPT = f"""
            You are a Senior Security Researcher and CodeQL Expert.
            I am analyzing a Python application for **CWE-639: Authorization Bypass Through User-Controlled Key**.

            I have extracted a list of "Potential Sources" (internal function parameters) and "Potential Sinks" (external API calls) from the codebase.
            Your goal is to identify which of these are relevant to CWE-639.


            **Instructions:**
            1. Analyze the "internal_functions" and "external_apis": 
                - Identify functions that execute system commands (e.g., os.system, subprocess, popen).
                - Identify parameters that are likely user-controlled entry points.
            2. STRICTLY return a single JSON object. Do not include markdown formatting or explanations outside the JSON.

            **Required JSON Output Format:**
            {{"confirmed_sinks": [
                "os.system",
                "subprocess.call"
                // ... add only confirmed dangerous sinks
              ],
              "confirmed_sources": [
                {{"function": "profile", "parameter": "username" }},
                {{"function": "download", "parameter": "filename" }}
                // ... add only confirmed user-controlled sources
              ]
            }}

            **Input Data:**
            {json_clean_data}
            """
            # print(NAIVE_PROMPT)
            model = ""
            try:
                llm_findings = send_prompt(
                    model="meta/llama-3.3-70b-instruct",
                    prompt=PROMPT,
                    max_token=8192,
                )
            except Exception as e:
                print(f"[*] Error with the model {model}: \n{e}")

            with open(
                "./target/results/5_json_clean_llm_findings.json", "w", encoding="utf-8"
            ) as f:
                f.write(llm_findings)


def test_pipeline():
    # PoC Pipeline
    import subprocess

    # Run the CodeQL queries to get context data
    subprocess.run(["bash", "./test/test_scan.sh"], check=True)

    # Send the prompt and get the LLM's findings
    run(iteration=3)

    # Generate qll query
    generate_qll_file(
        "./test/results/json_clean_llm_findings.json", "./test/ql/test_custom_query.qll"
    )

    # Scan code
    result = subprocess.run(
        ["bash", "./test/f_test_scan.sh"], capture_output=True, text=True
    )
    print(result.stdout)
    print(result.stderr)


def pipeline():
    # PoC Pipeline
    import subprocess

    # Run the CodeQL queries to get context data
    subprocess.run(["bash", "./target/scan.sh"], check=True)

    # Send the prompt and get the LLM's findings
    run(iteration=5)

    # Generate qll query
    generate_qll_file(
        "./target/results/5_json_clean_llm_findings.json",
        "./target/ql/custom_query_5.qll",
    )

    # Scan code
    result = subprocess.run(
        ["bash", "./target/f_scan.sh"], capture_output=True, text=True
    )
    print(result.stdout)
    print(result.stderr)


if __name__ == "__main__":
    # send_prompt("meta/llama-3.3-70b-instruct", "simple quick sort function", 1024)
    # run(iteration=3)
    pipeline()
