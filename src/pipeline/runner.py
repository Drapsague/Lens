from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path

from src.pipeline.config import LoadConfig
from src.codeql.generator import generate_qll_file
from src.codeql.runner import (
    CodeQLConfig,
    DatabaseCreator,
    DetectCWEsRunner,
    InternalFunctionRunner,
    ExternalApisRunner,
)
from src.llm.clients import LLMClient, LLMConfig
from src.llm.prompts import PROMPTS_DICT, NaivePrompt, Prompts
from src.processing.processor import (
    PROCESSOR_REGISTRY,
    DataProcessor,
    BasicCSVProcessing,
)


@dataclass
class Iteration:
    """Data representing an iteration in an config YAML file"""

    path: Path
    name: str


@dataclass
class PipelineContext:
    """Define every path or static variable name for a given pipeline"""

    iteration_config: LoadConfig
    codeql_config: CodeQLConfig

    output_dir: Path
    working_dir: Path = field(init=False)
    clean_data_path: Path = field(init=False)
    qll_path: Path = field(init=False)
    queries_dir: Path = field(init=False)
    llm_response_path: Path = field(init=False)

    QUERIES_DIR: Path = Path("queries")
    CLEAN_DATA_FILE: Path = Path("clean_context_data.json")
    QLL_FILE: Path = Path("custom_query.qll")
    LLM_RESPONSE_FILE: Path = Path("llm_repsonse.json")

    def __post_init__(self):
        self.working_dir = self.output_dir  # Might be useless
        self.queries_dir = self.output_dir / self.QUERIES_DIR
        self.clean_data_path = self.output_dir / self.CLEAN_DATA_FILE
        self.qll_path = self.queries_dir / self.QLL_FILE
        self.llm_response_path = self.output_dir / self.LLM_RESPONSE_FILE

    def _setup(self):
        """
        Creating the iteration folders
            /[iteration_name]_uuid # output_dir
                /queries           # queries_dir
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.queries_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class PipelineRunner(ABC):
    """Base class: In charge of anything related to a pipeline"""

    context: PipelineContext = field(init=False)

    # File needed to scan the code
    REQUIRED_QUERY_FILES: list[str] = [
        "detect_cwes.ql",
        "codeql-pack.lock.yml",
        "qlpack.yml",
    ]
    SHARED_QUERIES_FILES_DIR: Path = Path("queries")

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

    prompt_template: Prompts = field(init=False)

    def __post_init__(self):
        # Load the config from the YAML file
        self.config = LoadConfig.from_yaml(
            path=self.iteration.path, iteration_name=self.iteration.name
        )

        # We generate a unique folder name for this iteration
        self.output_dir = self.codeql_config.get_output_dir(
            iteration_name=self.iteration.name
        )

        # If the prompt is not found, the default prompt is the naive one
        prompt_class = PROMPTS_DICT.get(str(self.config.prompt), NaivePrompt)
        self.prompt = prompt_class()

    def run(self) -> None:
        # Runs context queries
        InternalFunctionRunner(config=self.codeql_config).execute(
            output_dir=self.output_dir
        )
        ExternalApisRunner(config=self.codeql_config).execute(
            output_dir=self.output_dir
        )

        # We get the "Processor" instance from the registry
        basic_processor: type[DataProcessor] = PROCESSOR_REGISTRY.get(
            str(self.config.processor), BasicCSVProcessing
        )

        # Get the context data in JSON
        context_data: str = basic_processor().process(working_dir=self.output_dir)
        basic_processor().write_file(self.output_dir, data=context_data)

        llm_config = LLMConfig(
            output_dir=self.output_dir,
            model=self.config.model,
            prompt=self.prompt.render(str(context_data)),
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_token=self.config.max_tokens,
        )

        llm_client = LLMClient(config=llm_config)
        llm_response = llm_client.send()
        llm_client.save(content=llm_response)

        # Generate qll query
        generate_qll_file(working_dir=self.output_dir)

        # Scan code
        DetectCWEsRunner(config=self.codeql_config).execute(output_dir=self.output_dir)


if __name__ == "__main__":
    iteration: Iteration = Iteration(
        path=Path("./configs/iterations.yaml"), name="naive"
    )
    # Create the CodeQL config
    config = CodeQLConfig(
        working_dir=Path("./data/test/"),
        codeql_language="python",
        report_format="csv",
        source_root=Path(
            "/home/drapsague/Devoteam/4_CodeQL/zero_to_hero/Playground/python/test-python/"
        ),
    )
    DatabaseCreator(config=config).execute()

    test = PipelineCIR(iteration=iteration, codeql_config=config)
    test.run()
