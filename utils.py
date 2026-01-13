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


def generate_qll_file(input_path, output_path):
    try:
        with open(input_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: File not found.")
        data = {"confirmed_sources": [], "confirmed_sinks": []}

    sources = data.get("confirmed_sources", [])
    sinks = data.get("confirmed_sinks", [])

    def format_conditions(conditions, indent_level=12):
        if not conditions:
            return " " * indent_level + "none()"
        separator = "\n" + " " * indent_level + "or "
        return " " * indent_level + separator.join(conditions)

    param_conds = []
    api_src_conds = []
    for src in sources:
        f_name = src.get("function")
        p_identifier = src.get("parameter")
        if not f_name or not p_identifier:
            continue

        if "." in p_identifier:
            # API Call Source logic
            parts = p_identifier.split(".")
            chain = f'API::moduleImport("{parts[0]}")'
            for part in parts[1:]:
                chain += f'.getMember("{part}")'
            chain += ".getACall()"
            cond = f'(call = {chain} and call.getScope().getName() = "{f_name}")'
            api_src_conds.append(cond)
        else:
            # Parameter logic
            cond = f'(p.getScope().getName() = "{f_name}" and p.getParameter().getName() = "{p_identifier}")'
            param_conds.append(cond)

    formatted_params = format_conditions(param_conds)
    formatted_api_srcs = format_conditions(api_src_conds)

    sink_conds = []
    for signature in sinks:
        parts = signature.split(".")
        if len(parts) < 2:
            continue

        module = parts[0]
        final_method = parts[-1]
        intermediates = parts[1:-1]  # Everything between Module and Final Function

        # Condition 1: Simple chains (os.system) don't need complex logic
        if not intermediates:
            sink_conds.append(
                f'(call = API::moduleImport("{module}").getMember("{final_method}").getACall())'
            )
            continue

        # Condition 2: Deep chains (django.db.connection.cursor.execute)
        # We generate an 'exists' block that chains variables using fuzzy logic

        # We need N+1 variables: n0 (module), n1..nK (intermediates), final (call)
        # We build the 'and' clauses dynamically.

        clauses = []
        # Start: n0 = module
        clauses.append(f'n0 = API::moduleImport("{module}")')

        # Intermediates: check fuzzy member for each step
        for i, part in enumerate(intermediates):
            prev = f"n{i}"
            curr = f"n{i + 1}"
            # checks: prev.part OR prev.part()
            clauses.append(f'isFuzzyMember({prev}, "{part}", {curr})')

        # Final Step: check the actual sink call on the last node
        last_node = f"n{len(intermediates)}"
        clauses.append(f'call = {last_node}.getMember("{final_method}").getACall()')

        # Construct the full exists(...) block
        # vars_list needs to declare n0, n1, ... up to the last intermediate
        vars_decl = ", ".join(
            [f"API::Node n{i}" for i in range(len(intermediates) + 1)]
        )

        full_query = f"exists({vars_decl} | {' and '.join(clauses)})"
        sink_conds.append(f"({full_query})")

    formatted_sinks = format_conditions(sink_conds)

    # 5. Build QLL Content
    # We add the 'isFuzzyMember' predicate at the top.
    qll_content = textwrap.dedent(f"""/**
* AUTO-GENERATED - Generic Chain Support
*/
import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs

/** * Helper to match both attributes and method returns.
 * e.g. matches 'obj.prop' AND 'obj.prop()' 
 */
predicate isFuzzyMember(API::Node base, string name, API::Node results) {{
    results = base.getMember(name)
    or
    results = base.getMember(name).getReturn()
}}

// --- SOURCES ---
predicate isLLMGeneratedSource(DataFlow::Node source) {{
    exists(DataFlow::ParameterNode p |
        source = p and (
{formatted_params}
        )
    )
    or
    exists(API::CallNode call |
        source = call and (
{formatted_api_srcs}
        )
    )
}}

// --- SINKS ---
predicate isLLMGeneratedSink(DataFlow::Node sink) {{
    exists(API::CallNode call |
        (
{formatted_sinks}
        )
        and sink = call.getArg(_)
    )
}}
""")

    with open(output_path, "w") as f:
        f.write(qll_content)
    print(f" Generated Generic QLL at {output_path}")
