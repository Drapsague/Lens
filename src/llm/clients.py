from dataclasses import dataclass, field
from openai import OpenAI
from openai import OpenAIError
from dotenv import load_dotenv
from pathlib import Path
import os


@dataclass
class LLMConfig:
    output_dir: Path
    model: str
    prompt: str
    temperature: float
    top_p: float
    max_token: int


@dataclass
class LLMClient:
    config: LLMConfig
    client: OpenAI = field(init=False)

    def __post_init__(self):
        load_dotenv()

        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY"),
        )

    def send(self) -> str:
        """Send the prompt set in the config instance"""
        try:
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": f"{self.config.prompt}"}],
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_token,
            )
            print(completion.choices[0].message.content)
            return completion.choices[0].message.content

        except OpenAIError as e:
            print(f"Error: {e}")
            return ""

    def save(self, content) -> None:
        """Function to save the LLM response in the output directory, in JSON"""
        with open(
            self.config.output_dir / "llm_response.json", "w", encoding="utf-8"
        ) as f:
            f.write(content)
