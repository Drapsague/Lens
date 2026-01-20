from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
import subprocess


@dataclass
class CodeQLConfig:
    """Environment configuration"""

    database_path: Path
    codeql_language: str
    report_format: str
    source_root: Path | None = None  # Useful when the project is finished


@dataclass
class Query:
    """Data representing a .ql file"""

    path: Path
    name: str


@dataclass
class CodeQLOperator(ABC):
    """Abstract base: Any operation involving the CodeQl CLI"""

    config: CodeQLConfig

    def _run(self, cmd: list[str]) -> None:
        """Helper to handle the subprocess.run(cmd)"""
        try:
            subprocess.run(cmd, check=True, text=True)
        except subprocess.SubprocessError as e:
            raise ValueError(f"Invalid subprocess or command: {cmd}") from e

    @abstractmethod
    def execute(self, output_dir: Path | None = None) -> None:
        """Abstract method to execute codeql query"""
        raise NotImplementedError()


@dataclass
class DatabaseCreator(CodeQLOperator):
    """In charge of building the codeql database"""

    overwrite: bool = False

    def execute(self, output_dir: Path | None = None) -> None:
        """Creates a CodeQL Database of the source code

        The output_dir param is not used, because the config already holds the 'database_path'.

        CLI Use :
            codeql database create db --language=python --source-root=simple_flask_app --threads=4 --ram=4096
        """

        # Command to create the DB
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

        if self.overwrite:
            # Add this flag to overwrite the current DB
            cmd.append("--overwrite")

        # Run the command to create the DB
        self._run(cmd)


@dataclass
class QueryExecutor(CodeQLOperator):
    """
    Run ANY CodeQL query, usually context related query

    CodeQL needs to firt export the query report in .bqrs
    and then we have to manually convert them to the appropriate format.
    """

    query: Query | None = None

    def execute(self, output_dir: Path | None = None) -> None:
        """Execute and export a CodeQL query"""

        # Error handling
        if not self.query:
            raise ValueError(f"The query is invalid or null: {self.query}")
        if not output_dir:
            raise ValueError(f"The output directory is invalid or null: {output_dir}")

        # Creating the folder if it does not exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # We have no use of the bqrs file afterward, so we use /tmp
        temp_path: str = f"/tmp/{self.query.name}.bqrs"

        export_bqrs: list[str] = [
            "codeql",
            "query",
            "run",
            f"--database={self.config.database_path}",
            str(self.query.path),
            "--threads=4",
            "--ram=4096",
            "--no-default-compilation-cache",  # To avoid using cache, thus re-running the query like it was never ran
            f"--output={temp_path}",
        ]

        output_file: str = (
            f"{str(output_dir)}/{self.query.name}.{self.config.report_format}"
        )
        # We convert the query report from .bqrs to the chosen format
        decode_bqrs: list[str] = [
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


@dataclass
class InternalFunctionRunner(QueryExecutor):
    """
    Inherit from the SimpleQuery class
    Specific implementation for the Internal Function query
    Uses hardcoded query path
    """

    def __post_init__(self):
        """Set the query path to the Internal Function query"""
        query: Query = Query(
            path=Path("./queries/internalFunc.ql"), name="internal_functions"
        )
        self.query = query


@dataclass
class ExternalApisRunner(QueryExecutor):
    """
    Specific implementation for the External Apis query
    """

    def __post_init__(self):
        """Set the query path to the External Apis query"""
        query: Query = Query(
            path=Path("./queries/externalApis.ql"), name="external_apis"
        )
        self.query = query


@dataclass
class DetectCWEsRunner(QueryExecutor):
    """
    This class is a specific implementation for the Detect CWEs query
    """

    def __post_init__(self):
        """Set the query path to the Detect CWEs query"""
        query: Query = Query(path=Path("./queries/detect_cwes.ql"), name="detect_cwes")
        self.query = query


if __name__ == "__main__":
    config = CodeQLConfig(
        database_path=Path("./data/test/test-codeql-db"),
        codeql_language="python",
        report_format="csv",
    )
    InternalFunctionRunner(config=config).execute(
        output_dir=Path("./data/test/runs/5/")
    )
    ExternalApisRunner(config=config).execute(output_dir=Path("./data/test/runs/5/"))
