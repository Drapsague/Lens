from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
import uuid

from src.codeql import (
    CodeQLConfig,
    DatabaseCreator,
)
from src.llm import PROMPTS_DICT, NaivePrompt

from src.pipeline import (
    PipelineContext,
    PipelineStep,
    RunSteps,
    ContextExtractionStep,
    ProcessDataStep,
    LLMAnalysisStep,
    GenerateQLLStep,
    RunScanStep,
    LoadConfig,
)


@dataclass
class Iteration:
    """Data representing an iteration in an config YAML file"""

    path: Path
    name: str


@dataclass
class PipelineRunner(ABC):
    """Base class: In charge of anything related to a pipeline"""

    context: PipelineContext
    iteration: Iteration

    # File needed to scan the code
    REQUIRED_QUERY_FILES: list[str] = field(
        default_factory=lambda: [  # default_factory must be a zero argument callable, so we use lambda to create the list for each new instances
            "detect_cwes.ql",
            "codeql-pack.lock.yml",
            "qlpack.yml",
        ]
    )
    SHARED_QUERIES_FILES_DIR: Path = Path("queries")

    @property
    def runs_path(self) -> Path:
        # Use it like: self.config.runs_path
        return self.context.codeql_config.working_dir / "runs"

    def _create_run_id(self, iteration_name: str = "iteration") -> str:
        """Generate unique UUID to name runs folder"""
        unique_id = uuid.uuid4().hex[:8]
        return f"{iteration_name}_{unique_id}"

    def get_output_dir(self, iteration_name: str = "iteration") -> Path:
        folder_name: str = self._create_run_id(iteration_name)
        return self.runs_path / folder_name

    def _setup_queries(self) -> None:
        """
        Create a symlink in the created folder for different file, to avoid copying them into each iteration folder
        queries/detect_cwes.ql
                codeql-pack.lock.yml # MANDATORY
                qlpack.yml           # MANDATORY

        """

        # The detect_cwes.ql and custom_query.qll need to be in the same dir to perform the scan
        for file in self.REQUIRED_QUERY_FILES:
            shared_path: Path = self.SHARED_QUERIES_FILES_DIR / file
            shared_file = shared_path.resolve()

            # Symlink to the /queries dir in the working directory
            link_path = self.context.queries_dir / file

            if not link_path.exists():
                link_path.symlink_to(shared_file)

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError()


@dataclass
class PipelineCIR(PipelineRunner):
    """In charge of building the pipeline for the CIR"""

    def __post_init__(self):
        # Load the config from the YAML file
        self.context.iteration_config = LoadConfig.from_yaml(
            path=self.iteration.path, iteration_name=self.iteration.name
        )
        # We generate a unique folder name for this iteration
        self.context.run_dir = self.get_output_dir(iteration_name=self.iteration.name)

        # Set the context paths, after defining the run_dir
        self.context._setup_path()

        # If the prompt is not found, the default prompt is the naive one
        prompt_class = PROMPTS_DICT.get(
            str(self.context.iteration_config.prompt), NaivePrompt
        )
        self.context.prompt_template = prompt_class()

        # Initialize the directories
        self.context._setup_dir()

        # Create Symlinks for CodeQL required files
        self._setup_queries()

    def run(self) -> None:
        # The steps are executed in this order
        pipeline_steps: list[PipelineStep] = [
            ContextExtractionStep(),
            ProcessDataStep(),
            LLMAnalysisStep(),
            GenerateQLLStep(),
            RunScanStep(),
        ]

        # Execute the steps one by one
        RunSteps(cfg=self.context, steps_list=pipeline_steps).execute_steps()


if __name__ == "__main__":
    iteration: Iteration = Iteration(
        path=Path("./configs/iterations.yaml"), name="naive"
    )
    # Create the CodeQL config
    codeql_config = CodeQLConfig(
        working_dir=Path("./data/test/"),
        codeql_language="python",
        report_format="csv",
        source_root=Path(
            "/home/drapsague/Devoteam/4_CodeQL/zero_to_hero/Playground/python/test-python/"
        ),
    )
    DatabaseCreator(config=codeql_config).execute()

    context = PipelineContext(codeql_config=codeql_config)

    test = PipelineCIR(context=context, iteration=iteration)
    test.run()
