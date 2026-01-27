from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path

from src.codeql.generator import generate_qll_file
from src.codeql.runner import (
    CodeQLConfig,
    DatabaseCreator,
    DetectCWEsRunner,
    InternalFunctionRunner,
    ExternalApisRunner,
)
from src.pipeline.config import LoadConfig
from src.llm.clients import LLMClient, LLMConfig
from src.processing.processor import (
    PROCESSOR_REGISTRY,
    DataProcessor,
    BasicCSVProcessing,
)
from src.pipeline.runner import PipelineContext
from src.llm.prompts import PROMPTS_DICT, NaivePrompt, Prompts


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
class ContextExtractionStep(PipelineStep):
    """Perform the extraction of every context data"""

    def execute(self, cfg: PipelineContext) -> None:
        print("[*] Extracting context data")
        # Runs context queries
        InternalFunctionRunner(config=cfg.codeql_config).execute(
            output_dir=cfg.output_dir
        )
        ExternalApisRunner(config=cfg.codeql_config).execute(output_dir=cfg.output_dir)


class ProcessDataStep(PipelineStep):
    """Process the context data, encode it in JSON and write it to the working directory"""

    def execute(self, cfg: PipelineContext) -> None:
        # We get the "Processor" instance from the registry
        basic_processor: type[DataProcessor] = PROCESSOR_REGISTRY.get(
            str(cfg.iteration_config.processor), BasicCSVProcessing
        )
        processor = basic_processor()  # Creates the BasicCSVProcessing instance

        # Get the context data in JSON
        context_data: str = processor.process(working_dir=cfg.working_dir)
        # Write the JSON file to the working directory
        processor.write_file(output_path=cfg.output_dir, data=context_data)


class LLMAnalysisStep(PipelineStep):
    """Set the LLM config, send the prompt and write it to the working directory"""

    prompt: Prompts
    context_data: str

    def execute(self, cfg: PipelineContext) -> None:
        llm_config = LLMConfig(
            output_dir=cfg.output_dir,
            model=cfg.iteration_config.model,
            prompt=self.prompt.render(self.context_data),
            temperature=cfg.iteration_config.temperature,
            top_p=cfg.iteration_config.top_p,
            max_token=cfg.iteration_config.max_tokens,
        )

        llm_client = LLMClient(config=llm_config)
        llm_response = llm_client.send()
        llm_client.save(content=llm_response)


class GenerateQLLStep(PipelineStep):
    """Generate any QLL file"""

    def execute(self, cfg: PipelineContext) -> None:
        generate_qll_file(
            input_file_path=cfg.clean_data_path, output_file_path=cfg.qll_path
        )


class RunScanStep(PipelineStep):
    """Run the final CodeQL scan"""

    def execute(self, cfg: PipelineContext) -> None:
        DetectCWEsRunner(config=cfg.codeql_config).execute(output_dir=cfg.output_dir)
