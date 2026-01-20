from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path

from config import LoadConfig
from codeql.runner import CodeQLConfig, InternalFunctionRunner, ExternalApisRunner
from llm.clients import send_prompt
from llm.prompts import PROMPTS_DICT, NaivePrompt, Prompts


@dataclass
class Iteration:
    """Data representing an iteration in an config YAML file"""

    path: Path
    name: str


@dataclass
class PipelineRunner(ABC):
    """Base class: In charge of anything related to a pipeline"""

    iteration: Iteration

    @abstractmethod
    def run(self):
        raise NotImplementedError()


@dataclass
class PipelineCIR(PipelineRunner):
    """In charge of building the pipeline for the CIR"""

    def run(self):
        # Load the config from the YAML file
        config = LoadConfig.from_yaml(
            path=self.iteration.path, iteration_name=self.iteration.name
        )
        # Create the CodeQL config
        codeql_config = CodeQLConfig(
            database_path=Path("./data/test/test-codeql-db"),
            codeql_language="python",
            report_format="csv",
        )

        # This should be changed, needs an automatic uuid generation for each new runs
        output_dir: Path = Path("./data/test/runs/6/")

        # Runs context queries
        InternalFunctionRunner(config=codeql_config).execute(output_dir=output_dir)
        ExternalApisRunner(config=codeql_config).execute(output_dir=output_dir)

        # If the prompt is not found, the default prompt is the naive one
        prompt: Prompts = PROMPTS_DICT.get(str(config.prompt), NaivePrompt())

        llm_response: str = send_prompt(
            model=config.model,
            prompt=prompt.render("test"),
            max_token=config.max_tokens,
        )


if __name__ == "__main__":
    iteration: Iteration = Iteration(
        path=Path("./configs/iterations.yaml"), name="naive"
    )
    test = PipelineCIR(iteration=iteration)
    test.run()
