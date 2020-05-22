from aiohttp import web
from aiohttp_micro.handlers import get_payload
from aiohttp_micro.schemas import EnumField
from marshmallow import EXCLUDE, fields, Schema

from apollo.entities.alerts import Alert, AlertStatus
from apollo.gateways.telegram import TelegramGateway


class AlertSchema(Schema):
    annotations = fields.Dict(keys=fields.Str, values=fields.Str, required=True)
    labels = fields.Dict(keys=fields.Str, values=fields.Str, required=True)
    status = EnumField(AlertStatus, default=AlertStatus.firing, required=True)

    class Meta:
        unknown = EXCLUDE


class PayloadSchema(Schema):
    alerts = fields.List(fields.Nested(AlertSchema))

    class Meta:
        unknown = EXCLUDE


async def receiver(request: web.Request) -> web.Response:
    payload = await get_payload(request=request)

    schema = PayloadSchema()
    document = schema.load(payload)

    alerts = []
    for item in document["alerts"]:
        alert = Alert(
            name=item["labels"]["alertname"],
            summary=item["annotations"]["summary"],
            description=item["annotations"]["description"],
            severity=item["labels"]["severity"],
            status=item["status"],
        )

        request.app["metrics"]["alerts_total"].labels(
            request.app["app_name"], alert.name, alert.status
        ).inc()

        request.app["logger"].info(
            "Receive alert",
            alert_name=alert.name,
            summary=alert.summary,
            status=alert.status.value,
        )

        alerts.append(alert)

    config = request.app["config"]
    gateway = TelegramGateway(
        config.telegram.chat,
        config.telegram.token,
        logger=request.app["logger"],
    )
    await gateway.send(alerts)

    return web.Response(status=200)
