from logging import Logger
from typing import Iterable

import aiohttp
from sentry_sdk import capture_exception

from apollo.entities.alerts import Alert, AlertStatus


class TelegramGateway:
    __slots__ = ("chat", "url", "logger")

    def __init__(self, chat: str, token: str, logger: Logger) -> None:
        self.chat = chat
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.logger = logger

    async def send(self, alerts: Iterable[Alert]) -> bool:
        done = True

        try:
            async with aiohttp.ClientSession() as session:
                for alert in alerts:
                    if alert.status == AlertStatus.firing:
                        params = {
                            "chat_id": self.chat,
                            "text": f"Firing: {alert.description}",
                        }
                    elif alert.status == AlertStatus.resolved:
                        params = {
                            "chat_id": self.chat,
                            "text": f"Resolved: {alert.description}",
                        }

                    async with session.get(self.url, params=params) as resp:
                        if resp.status != 200:
                            done = False

                            self.logger.error(
                                "Send alert to telegram failed",
                                summary=alert.summary,
                                http_status=resp.status,
                            )
        except aiohttp.client_exceptions.ClientConnectorError:
            self.logger.error("Telegram could not be reached")
            capture_exception()

            done = False

        return done
