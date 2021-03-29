import os
import base

base.config.load_from_yaml(f'config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')
TORTOISE_ORM = base.config.tortoise_config()
