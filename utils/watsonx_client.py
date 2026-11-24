import os
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

MODEL_ID = "meta-llama/llama-3-3-70b-instruct"


def get_model() -> ModelInference:
    """Return a configured watsonx.ai ModelInference instance."""
    # Strip any ?context= suffix accidentally copied from the browser URL
    project_id = os.getenv("WATSONX_PROJECT_ID", "").split("?")[0].strip()
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    credentials = Credentials(
        url=url,
        api_key=os.getenv("WATSONX_API_KEY"),
    )

    model = ModelInference(
        model_id=MODEL_ID,
        credentials=credentials,
        project_id=project_id,
        params={
            "max_new_tokens": 600,
            "temperature": 0.1,
            "stop_sequences": ["###"],
        },
        validate=False,
    )
    return model
