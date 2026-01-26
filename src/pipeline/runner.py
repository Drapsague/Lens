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
class PipelineRunner(ABC):
    """Base class: In charge of anything related to a pipeline"""

    iteration: Iteration

    def setup_queries(self, run_dir: Path):
        """
        Create a symlink in the created folder fo the detect query
        queries/detect_cwes.ql
                codeql-pack.lock.yml # MANDATORY
                qlpack.yml           # MANDATORY

        """
        queries = run_dir / "queries"
        queries.mkdir(parents=True, exist_ok=True)

        shared_query = Path("queries/detect_cwes.ql").resolve()
        shared_conf_file_1 = Path("queries/codeql-pack.lock.yml").resolve()
        shared_conf_file_2 = Path("queries/qlpack.yml").resolve()

        link_path = queries / "detect_cwes.ql"
        link_param_1_path = queries / "codeql-pack.lock.yml"
        link_param_2_path = queries / "qlpack.yml"

        # Creating Symlink for detect_cwes.ql
        if not link_path.exists():
            link_path.symlink_to(shared_query)

        # Creating Symlink for codeql-pack.lock.yml
        if not link_param_1_path.exists():
            link_param_1_path.symlink_to(shared_conf_file_1)

        # Creating Symlink for qlpack.yml
        if not link_param_2_path.exists():
            link_param_2_path.symlink_to(shared_conf_file_2)

    @abstractmethod
    def run(self):
        raise NotImplementedError()


@dataclass
class PipelineCIR(PipelineRunner):
    """In charge of building the pipeline for the CIR"""

    codeql_config: CodeQLConfig
    config: LoadConfig = field(init=False)
    output_dir: Path = field(init=False)
    prompt: Prompts = field(init=False)

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
        self.prompt = PROMPTS_DICT.get(str(self.config.prompt), NaivePrompt())

        # Creating a Symlink to the detect_cwes query from the working dir
        # The detect_cwes.ql and custom_query.qll need to be in the same dir to perform the scan
        self.setup_queries(run_dir=self.output_dir)

    def run(self):
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
