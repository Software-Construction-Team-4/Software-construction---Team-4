import os
from typing import Optional


class Environment:
    _PATH: str = ".env"

    _vars: dict[str, str]
    _defaults: dict[str, str] = {
        "BASE_URL": "http://localhost:8000",

        "DB_HOST": "localhost",
        "DB_PORT": "8001",
        "DB_NAME": "mobypark",
        "DB_USER": "admin",
        "DB_PASSWORD": "admin"
    }

    _is_setup: bool = False


    @staticmethod
    def _parse_env(path: str) -> dict[str, str]:
        env: dict[str, str] = Environment._defaults.copy()
        with open(path, 'r') as contents:
            vars: list[list[str]] = [var.split('=') for var in contents.readlines()]

            for var in vars:
                name, value = var
                if (name is not None) and (value is not None):
                    env[name.strip()] = value.strip()

        return env


    @staticmethod
    def get_var(var: str, default: Optional[str] = None) -> Optional[str]:
        # pytest doesn't like it if we don't do it this way
        Environment._setup()
        # some vars only exist in the vm's path, some in the .env
        return Environment._vars.get(var, os.getenv(var, default))


    @staticmethod
    def _setup() -> None: # python doesn't have static initialisers for classes, sigh
        if Environment._is_setup:
            return

        try:
            Environment._vars = Environment._parse_env(Environment._PATH)
            Environment._is_setup = True
        except FileNotFoundError:
            print("`.env` does not exist, defaulting...")
