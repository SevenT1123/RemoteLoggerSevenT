"""JSON Schema definitions and topic map for SevenT IMU telemetry."""

from __future__ import annotations

TOPICS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "imu_data": (
        "/imu",
        [
            ("timestamp_ms", "number"),
            ("accel_x_ms2", "number"),
            ("accel_y_ms2", "number"),
            ("accel_z_ms2", "number"),
            ("gyro_x_dps", "number"),
            ("gyro_y_dps", "number"),
            ("gyro_z_dps", "number"),
        ],
    ),
}

CSV_HEADER: list[str] = ["event"] + [name for name, _ in TOPICS["imu_data"][1]]


def json_schema_for_fields(packet_type: str, fields: list[tuple[str, str]]) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": packet_type,
        "type": "object",
        "properties": {
            name: {"type": json_type}
            for name, json_type in fields
        },
        "required": [name for name, _ in fields],
    }