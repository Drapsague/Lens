from dataclasses import dataclass, field
from openai import OpenAI
from openai import OpenAIError
from dotenv import load_dotenv
from pathlib import Path
import os
import json


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
    _client: OpenAI = field(init=False)

    def __post_init__(self):
        load_dotenv()

        self._client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY"),
        )

    def send(self) -> str:
        """Send the prompt set in the config instance"""

        try:
            completion = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": f"{self.config.prompt}"}],
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_token,
            )
            content = completion.choices[0].message.content
            # print(self._to_json(str(content)))

        except OpenAIError as e:
            content = "Error"
            raise e

        return str(content)

    def save(self, content: str) -> None:
        """Function to save the LLM response in the output directory, in JSON"""
        with open(
            self.config.output_dir / "llm_response.json", "w", encoding="utf-8"
        ) as f:
            # Write the llm response in JSON
            f.write(self._to_json(content))

    def _to_json(self, content: str):
        try:
            return json.dumps(json.loads(content), indent=2)

        except json.JSONDecodeError:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.dumps(json.loads(content.strip()), indent=2)
