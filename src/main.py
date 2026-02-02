import argparse
import textwrap
from pathlib import Path

from src.pipeline import Iteration, PipelineCIR, PipelineContext
from src.codeql import CodeQLConfig, DatabaseCreator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="Lens_CLI",
        description="Lens is a SAST tool designed to detect context-based vulnerabilties",
        epilog=textwrap.dedent("""\
            Example:
              python3 -m src.main --config_file configs/iterations.yaml --iteration_name naive --working_dir data/test --source_root /path/to/code/

            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config_file", required=True, help="The YAML config file")
    parser.add_argument(
        "--iteration_name",
        required=True,
        help="The name of the iteration in the YAML file",
    )

    parser.add_argument(
        "--working_dir",
        required=True,
        help="The directory where you will run the pipeline",
    )
    parser.add_argument(
        "--source_root",
        required=True,
        help="Path to the directory of the code you want to scan",
    )
    parser.add_argument(
        "--report_format",
        required=False,
        help="For now useless, only CSV",
    )
    parser.add_argument(
        "-l",
        "--language",
        required=False,
        help="The programming language of your code, ONLY Python for now",
    )

    args = parser.parse_args()

    iteration: Iteration = Iteration(
        path=Path(args.config_file), name=args.iteration_name
    )
    # Create the CodeQL config
    codeql_config = CodeQLConfig(
        working_dir=Path(args.working_dir),
        codeql_language=args.language,
        report_format=args.report_format,
        source_root=Path(args.source_root),
    )
    # Create the CodeQL DB
    DatabaseCreator(config=codeql_config).execute()

    # Set the pipeline's context
    context = PipelineContext(codeql_config=codeql_config)

    # Create a Pipeline
    pipeline = PipelineCIR(context=context, iteration=iteration)
    pipeline.run()


if __name__ == "__main__":
    main()
