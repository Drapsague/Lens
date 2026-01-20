from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
import subprocess


@dataclass
class CodeQLConfig:
    database_path: Path
    codeql_language: str
    report_format: str
    source_root: Path | None = None  # Useful when the project is finished


@dataclass
class Query:
    path: Path
    name: str


class CodeQL:
    def __init__(self, config: CodeQLConfig):
        """Initialize the instance with the CodeQLConfig dataclass"""
        self.config = config

    def _run(self, cmd: list[str]) -> None:
        """Short function to handle the subprocess.run(cmd)"""
        try:
            subprocess.run(cmd, check=True, text=True)
        except subprocess.SubprocessError as e:
            raise ValueError(f"Invalid subprocess or command: {cmd}") from e

    def create_database(self, overwrite: bool = False) -> None:
        """Create a CodeQL Database of the source code

        codeql database create flask-db --language=python --source-root=simple_flask_app --threads=4 --ram=4096"""
        cmd = [
            "codeql",
            "database",
            "create",
            str(self.config.database_path),
            f"--language={self.config.codeql_language}",
            f"--source-root={self.config.source_root}",
            "--threads=4",
            "--ram=4096",
        ]

        if overwrite:
            # Add this flag to overwrite the current DB
            cmd.append("--overwrite")

        # Run the command to create the DB
        self._run(cmd)

    def _run_single_query(self, query: Query, output_dir: Path):
        """Run CodeQL query, usually context related query

        CodeQL needs to firt export the query report in .bqrs and then we have to manually convert them to the appropriate format.
        """

        # We have no use of the bqrs file afterward, so we use /tmp
        temp_path = f"/tmp/{query.name}.bqrs"
        # We run the query on the db we want, and export the report in .bqrs
        export_bqrs = [
            "codeql",
            "query",
            "run",
            f"--database={self.config.database_path}",
            str(query.path),
            "--threads=4",
            "--ram=4096",
            "--no-default-compilation-cache",  # To avoid using cache, thus re-running the query like it was never ran
            f"--output={temp_path}",
        ]

        output_file: str = f"{str(output_dir)}/{query.name}.{self.config.report_format}"
        # We convert the query report from .bqrs to the chosen format
        decode_bqrs = [
            "codeql",
            "bqrs",
            "decode",
            temp_path,
            f"--format={self.config.report_format}",
            f"--output={output_file}",
        ]

        # Run the commands to export and decode the results
        self._run(export_bqrs)
        self._run(decode_bqrs)

    def run_queries(self, queries: list[Query], output_dir: Path):
        """Run multiple queries from a Query list"""
        # Creating the folder if it does not exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Maybe add some logs
        for query in queries:
            self._run_single_query(query=query, output_dir=output_dir)


if __name__ == "__main__":
    config = CodeQLConfig(
        database_path=Path("./data/test/test-codeql-db"),
        codeql_language="python",
        report_format="csv",
    )
    runner = CodeQL(config=config)
    context_queries: list[Query] = [
        Query(path=Path("./queries/internalFunc.ql"), name="internal_functions")
    ]

    runner.run_queries(queries=context_queries, output_dir=Path("./data/test/runs/2/"))
