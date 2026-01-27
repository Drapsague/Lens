from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path

from src.pipeline.config import LoadConfig
from src.llm.prompts import PROMPTS_DICT, NaivePrompt, Prompts
from src.codeql.generator import generate_qll_file
from src.codeql.runner import (
    DetectCWEsRunner,
    InternalFunctionRunner,
    ExternalApisRunner,
    CodeQLConfig,
    DatabaseCreator,
)
from src.llm.clients import LLMClient, LLMConfig
from src.processing.processor import (
    PROCESSOR_REGISTRY,
    DataProcessor,
    BasicCSVProcessing,
)


@dataclass
class PipelineContext:
    """Define every path or static variable name for a given pipeline"""

    codeql_config: CodeQLConfig

    iteration_config: LoadConfig = field(init=False)

    # Need to rework
    run_dir: Path = field(init=False)

    clean_data_path: Path = field(init=False)
    qll_path: Path = field(init=False)
    queries_dir: Path = field(init=False)
    llm_response_path: Path = field(init=False)
    context_data: str = field(init=False)
    prompt_template: Prompts = field(init=False)

    QUERIES_DIR: Path = Path("queries")
    CLEAN_DATA_FILE: Path = Path("clean_context_data.json")
    QLL_FILE: Path = Path("custom_query.qll")
    LLM_RESPONSE_FILE: Path = Path("llm_repsonse.json")

    def _setup_path(self):
        """
        Set different variables for the pipeline context

        For the _setup_dir()
            - run_dir must be defined to run this function

        """
        if self.run_dir is None:
            return "[*] The output directory must be set before calling the _setup_path function"

        self.queries_dir = self.run_dir / self.QUERIES_DIR
        self.clean_data_path = self.run_dir / self.CLEAN_DATA_FILE
        self.qll_path = self.queries_dir / self.QLL_FILE
        self.llm_response_path = self.run_dir / self.LLM_RESPONSE_FILE

    def _setup_dir(self):
        """
        Creating the iteration folders
            /[iteration_name]_uuid # output_dir
                /queries           # queries_dir
        """
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.queries_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class PipelineStep(ABC):
    """
    Class to define a pipeline step

    Current Step:
        - Context Extraction
        - Get/Write Json Context Data
        - Create and Send prompt
        - Generate QLL
        - Scan code
    """

    @abstractmethod
    def execute(self, cfg: PipelineContext) -> None:
        raise NotImplementedError()


@dataclass
class RunSteps:
    cfg: PipelineContext
    steps_list: list[PipelineStep]

    def execute_steps(self):
        """Execute all the steps in a given steps list using the given config"""
        for step in self.steps_list:
            try:
                step.execute(self.cfg)
            except Exception as e:
                print(f"Step execution failed for {step}")
                raise e


@dataclass
class ContextExtractionStep(PipelineStep):
    """Perform the extraction of every context data"""

    def execute(self, cfg: PipelineContext) -> None:
        print("[*] Extracting context data")
        # Runs context queries
        InternalFunctionRunner(config=cfg.codeql_config).execute(output_dir=cfg.run_dir)
        ExternalApisRunner(config=cfg.codeql_config).execute(output_dir=cfg.run_dir)


@dataclass
class ProcessDataStep(PipelineStep):
    """
    Process the context data, encode it in JSON and write it to the working directory
    """

    def execute(self, cfg: PipelineContext) -> None:
        print("[*] Processing context data")
        # We get the "Processor" instance from the registry
        basic_processor: type[DataProcessor] = PROCESSOR_REGISTRY.get(
            str(cfg.iteration_config.processor), BasicCSVProcessing
        )
        processor = basic_processor()  # Creates the BasicCSVProcessing instance

        # Get the context data in JSON
        context_data: str = processor.process(working_dir=cfg.run_dir)

        # Set the config value, we need the context data in the LLMAnalysis step
        cfg.context_data = str(context_data)

        # Write the JSON file to the working directory
        processor.write_file(output_path=cfg.clean_data_path, data=context_data)


@dataclass
class LLMAnalysisStep(PipelineStep):
    """Set the LLM config, send the prompt and write it to the working directory"""

    def execute(self, cfg: PipelineContext) -> None:
        print("[*] Starting the LLM analysis")
        llm_config = LLMConfig(
            output_dir=cfg.run_dir,
            model=cfg.iteration_config.model,
            prompt=cfg.prompt_template.render(cfg.context_data),
            temperature=cfg.iteration_config.temperature,
            top_p=cfg.iteration_config.top_p,
            max_token=cfg.iteration_config.max_tokens,
        )

        llm_client = LLMClient(config=llm_config)
        llm_response = llm_client.send()
        llm_client.save(content=llm_response)


@dataclass
class GenerateQLLStep(PipelineStep):
    """Generate any QLL file"""

    def execute(self, cfg: PipelineContext) -> None:
        print("[*] Generating the QLL query")
        generate_qll_file(
            input_file_path=cfg.clean_data_path, output_file_path=cfg.qll_path
        )


@dataclass
class RunScanStep(PipelineStep):
    """Run the final CodeQL scan"""

    def execute(self, cfg: PipelineContext) -> None:
        print("[*] Scanning the code")
        DetectCWEsRunner(config=cfg.codeql_config).execute(output_dir=cfg.run_dir)
