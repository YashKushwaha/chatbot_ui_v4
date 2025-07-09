
from llama_index.llms.bedrock_converse import BedrockConverse
import botocore.session
from pathlib import Path
from src.config_loader import get_config, load_env_vars

def get_bedrock_llm():
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    config = get_config(config_path)
    load_env_vars(config)
    botocore_session = botocore.session.get_session()
    #https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/llms/llama-index-llms-bedrock/llama_index/llms/bedrock/base.py

    full_arn = 'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0'
    MODEL_ID = full_arn.split("/")[-1]
    MAX_TOKENS = 512
    TEMPERATURE = 0.7
    REGION = 'us-east-1'
    TOP_P = 0.9
    CONTEXT_SIZE = 512 # max length of input
    init_args = dict(model=MODEL_ID, temperature= TEMPERATURE, max_tokens = MAX_TOKENS)
    bedrock_llm = BedrockConverse(botocore_session = botocore_session, **init_args)
    return bedrock_llm