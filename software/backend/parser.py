"""Parser for SevenT STM32 UART CSV telemetry.

OutputTask.c emits:
  Header (once):
    event,timestamp_ms,accel_x_ms2,accel_y_ms2,accel_z_ms2,gyro_x_dps,gyro_y_dps,gyro_z_dps\r\n

  Data rows (50 Hz):
    imu_data,<timestamp_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>\r\n
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

_IMU_FIELDS = (
    "timestamp_ms", "accel_x_ms2", "accel_y_ms2", "accel_z_ms2", "gyro_x_dps", "gyro_y_dps", "gyro_z_dps",
)

_CSV_HEADER_PREFIX = "event"


@dataclass
class ParsedTelemetry:
    topic: str
    packet_type: str
    payload: dict
    timestamp_ns: int


class TelemetryCsvParser:
    def parse_line(self, raw: bytes) -> ParsedTelemetry | None:
        try:
            text = raw.decode("utf-8", errors="replace").strip()
        except UnicodeDecodeError:
            return None

        if not text:
            return None

        if text.startswith(_CSV_HEADER_PREFIX):
            return None

        parts = text.split(",")
        if len(parts) < 2:
            return None

        event = parts[0]

        if event == "imu_data":
            return self._parse_imu(parts[1:])

        return None


    def _parse_imu(self, values: list[str]) -> ParsedTelemetry | None:
        if len(values) != len(_IMU_FIELDS):
            return None
        try:
            payload: dict = {}
            for field, raw_val in zip(_IMU_FIELDS, values):
                if field == "timestamp_ms":
                    payload[field] = int(raw_val)
                else:
                    payload[field] = float(raw_val)
        except ValueError:
            return None

        timestamp_ns = _nanoseconds()

        return ParsedTelemetry(
            topic="/imu",
            packet_type="imu_data",
            payload=payload,
            timestamp_ns=timestamp_ns,
        )


def _nanoseconds() -> int:
    return int(dt.datetime.now(tz=dt.timezone.utc).timestamp() * 1_000_000_000)