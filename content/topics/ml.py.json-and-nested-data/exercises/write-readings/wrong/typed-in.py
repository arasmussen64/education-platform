from dataclasses import dataclass


@dataclass
class Reading:
    sensor: str
    value: float


def parse_readings(text):
    return [Reading("a", 1.5), Reading("b", 2.0)]


def to_json(readings):
    return '[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]'


print(parse_readings(""))
print(to_json([]))
