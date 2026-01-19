from enum import StrEnum
import os
from typing import Union
import requests # should probably use aiohttp
import datetime
from environment import Environment


class Logger:
    class Level(StrEnum):
        INFO = "info"
        WARN = "warn"
        ERROR = "error"

    FORMAT_TIMESTAMP: str = "<t:{timestamp}:R>"
    FORMAT_ERROR: str = "```py\n{exception}\n```"


    @staticmethod
    def log(message: str, level: Level = Level.INFO, mention: bool = False, colour: int = 0x252525) -> None:
        if (Environment.get_var("discord_webhook_url") is None): # webhook isn't configured
            return

        timestamp: int = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        body = {
            "content": "@everyone" if mention else None,
            "embeds": [
                {
                    "title": f"[{level.upper()}]",
                    "color": colour,
                    "fields": [
                        {
                            "name": "When?",
                            "value": Logger.FORMAT_TIMESTAMP.format(timestamp = timestamp)
                        },
                        {
                            "name": "Details",
                            "value": message
                        }
                    ]
                }
            ]
        }

        requests.post(Environment.get_var("discord_webhook_url"), json=body)

    @staticmethod
    def warn(message: str) -> None:
        Logger.log(message, level = Logger.Level.WARN, colour = 0xF9BB37)

    @staticmethod
    def error(message: str, exception: Union[Exception, str]) -> None:
        Logger.log(f"{message}\n{Logger.FORMAT_ERROR.format(exception = str(exception))}",
                   level = Logger.Level.ERROR, mention = True, colour = 0xDB3C1D)
