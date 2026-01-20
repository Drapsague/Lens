from openai import OpenAI
from dotenv import load_dotenv
import os


def send_prompt(model: str, prompt: str, max_token: int):
    load_dotenv()

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.getenv("NVIDIA_API_KEY"),
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0.1,
        top_p=0.9,
        max_tokens=max_token,
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
