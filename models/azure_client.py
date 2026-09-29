import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)


MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def generate_response(prompt: str) -> str:

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text