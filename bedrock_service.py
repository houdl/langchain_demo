import os
from enum import Enum

import litellm
from langchain_community.chat_models import ChatLiteLLM

# 确保环境变量被正确加载
from dotenv import load_dotenv
load_dotenv()

# 设置 AWS 凭证
os.environ["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID", "")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
os.environ["AWS_REGION_NAME"] = os.environ.get("AWS_REGION_NAME", "us-west-2")

litellm.drop_params = True
litellm.modify_params = True
litellm.telemetry = False
# litellm._turn_on_debug()


class BedrockModel(str, Enum):
    EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"
    EMBEDDING_MODEL_ID_V2 = "amazon.titan-embed-text-v2:0"
    PLUS_MODEL_ID = (
        "us.anthropic.claude-3-5-haiku-20241022-v1:0"  # cross-region inference enabled
    )
    PRO_MODEL_ID = (
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # cross-region inference enabled
    )
    REASONING_MODEL_ID = (
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # cross-region inference enabled
    )
    NOVA_LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"  # cross-region inference enabled


class BedrockAIService:
    AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME", "us-west-2")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

    def llm_converse(self, model: str, temperature: int = 0, max_tokens: int = 4096):
        model_id = f"bedrock/converse/{model}"
        return ChatLiteLLM(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            aws_region_name=self.AWS_REGION_NAME,
            model_kwargs={
                # "thinking": {"type": "enabled", "budget_tokens": 1024},
            },
        )
