import config
from aiohttp import web
from aiohttp_metrics import setup as setup_metrics  # type: ignore
from aiohttp_micro import (
    AppConfig as BaseConfig,
    setup as setup_micro,
)
from prometheus_client import Counter  # type: ignore

from apollo.handlers import alerts


class TelegramConfig(config.Config):
    chat = config.StrField(env="TELEGRAM_CHAT")
    token = config.StrField(env="TELEGRAM_TOKEN")


class AppConfig(BaseConfig):
    telegram = config.NestedField[TelegramConfig](TelegramConfig)


def init(app_name: str, cfg: AppConfig) -> web.Application:
    app = web.Application()

    setup_micro(app, app_name, cfg)
    setup_metrics(
        app,
        metrics={
            "alerts_total": Counter(
                "alerts_total",
                "Total alerts count",
                ("app_name", "alert_name", "status"),
            ),
        },
    )

    app.router.add_routes(
        [web.post("/alerts", alerts.receiver, name="alerts.receiver")]
    )

    app["logger"].info("Initialize application")

    return app
