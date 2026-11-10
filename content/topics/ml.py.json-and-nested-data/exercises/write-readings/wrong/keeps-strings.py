import json
from dataclasses import asdict, dataclass


@dataclass
class Reading:
    sensor: str
    value: float


def parse_readings(text):
    return [Reading(r["sensor"], r["value"]) for r in json.loads(text)]


def to_json(readings):
    return json.dumps([asdict(r) for r in readings])


readings = parse_readings('[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]')
print(readings)
print(to_json(readings))
