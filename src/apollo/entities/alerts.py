from enum import Enum

import attr


class AlertStatus(Enum):
    firing = "firing"
    resolved = "resolved"


@attr.dataclass(slots=True, kw_only=True)
class Alert:
    name: str
    summary: str
    description: str
    severity: str
    status: AlertStatus = AlertStatus.firing
