import os
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()


class AzureOpenAIClient:

    def __init__(self):

        # Read Azure OpenAI configuration
        key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        generator_deployment = os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        )

        evaluator_deployment = os.getenv(
            "AZURE_OPENAI_EVALUATOR_DEPLOYMENT_NAME"
        )

        # Check required variables
        missing = []

        if not key:
            missing.append("AZURE_OPENAI_API_KEY")

        if not endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")

        if not generator_deployment:
            missing.append(
                "AZURE_OPENAI_DEPLOYMENT_NAME"
            )

        if missing:

            raise ValueError(
                "Missing Azure configuration: "
                + ", ".join(missing)
            )

        # Remove trailing slash
        endpoint = endpoint.rstrip("/")

        # Azure OpenAI v1 endpoint
        endpoint = endpoint + "/openai/v1/"

        # Create OpenAI client for Azure
        self.client = OpenAI(
            base_url=endpoint,
            api_key=key
        )

        # Generator deployment
        self.generator_deployment = (
            generator_deployment
        )

        # Evaluator deployment
        # If not provided, use generator deployment
        self.evaluator_deployment = (
            evaluator_deployment
            or generator_deployment
        )


    # =====================================
    # GENERATE TEXT
    # =====================================

    def generate_text(
        self,
        system_prompt,
        user_prompt
    ):

        response = (
            self.client.chat.completions.create(

                model=self.generator_deployment,

                temperature=0.4,

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_prompt
                    }

                ]

            )
        )

        return response.choices[0].message.content


    # =====================================
    # STRUCTURED EVALUATION
    # =====================================

    def evaluate_structured(
        self,
        system_prompt,
        user_prompt,
        schema
    ):

        response = (
            self.client.beta.chat.completions.parse(

                model=self.evaluator_deployment,

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_prompt
                    }

                ],

                response_format=schema

            )
        )

        # Get evaluator response
        message = response.choices[0].message


        # Handle refusal
        if message.refusal:

            raise RuntimeError(
                "Evaluator refused the request: "
                + message.refusal
            )


        # Ensure structured output exists
        if message.parsed is None:

            raise RuntimeError(
                "Evaluator did not return "
                "structured output."
            )


        return message.parsed
