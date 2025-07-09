import yaml
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

DEFAULT_CONFIG_PATH = os.path.join(Path(__file__).resolve().parents[1] , "config", "settings.yaml")

def get_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def load_env_vars(config):
    env_var = config['AWS_CRED_ENV_FILE_VAR']
    env_file = os.environ.get(env_var)
    if env_file:
        load_dotenv(env_file)
    else:
        raise EnvironmentError(f"Env variable {env_var} not found")