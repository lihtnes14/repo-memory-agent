from backend.models.azure_client import generate_response


response = generate_response(
    "Explain what a Python virtual environment is in one sentence."
)


print(response)