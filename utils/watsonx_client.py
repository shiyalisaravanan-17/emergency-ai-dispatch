import os
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()


def get_model() -> ModelInference:
    """Return a configured watsonx.ai ModelInference instance."""
    credentials = Credentials(
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.getenv("WATSONX_API_KEY"),
    )
    project_id = os.getenv("WATSONX_PROJECT_ID")

    model = ModelInference(
        model_id="ibm/granite-13b-instruct-v2",
        credentials=credentials,
        project_id=project_id,
        params={
            "max_new_tokens": 500,
            "temperature": 0.1,   # low temperature = more deterministic / factual
            "stop_sequences": ["###"],
        },
    )
    return model
