"""Tiny serial CSV logger for the SevenT STM32 IMU.

Use this when you only want a CSV file and do not need Foxglove/MCAP.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import sys
from pathlib import Path

import serial

from .schema import CSV_HEADER


def make_filename() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"sevent_{timestamp}.csv"


def run(args: argparse.Namespace) -> None:
    output_path = Path(args.output) if args.output else Path(make_filename())
    output_path.parent.mkdir(parents=True, exist_ok=True)

    active_header = CSV_HEADER.copy()

    try:
        ser = serial.Serial(args.serial_port, args.baud, timeout=2)
    except serial.SerialException as e:
        print(f"[ERROR] Could not open {args.serial_port}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[serial] logging {args.serial_port} at {args.baud} to {output_path}")

    lines_written = 0

    try:
        with ser, output_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(active_header)
            f.flush()

            while True:
                try:
                    raw = ser.readline()
                except serial.SerialException as e:
                    print(f"[ERROR] Serial read error: {e} — attempting to continue", file=sys.stderr)
                    continue
                except OSError as e:
                    print(f"[ERROR] OS-level serial error: {e} — device may have disconnected", file=sys.stderr)
                    break

                if not raw:
                    print("[WARN] No data received — check MCU is running and baud rate matches", file=sys.stderr)
                    continue

                try:
                    line = raw.decode("utf-8").rstrip("\r\n")
                except UnicodeDecodeError:
                    print(f"[WARN] Garbled line skipped: {raw!r}", file=sys.stderr)
                    continue

                if not line:
                    continue

                if line.startswith("event,"):
                    # Firmware header is the source of truth once it appears.
                    active_header = next(csv.reader([line]))
                    continue

                if not line.startswith("imu_data,"):
                    if args.verbose:
                        print(f"[ignored] {line}", file=sys.stderr)
                    continue

                try:
                    row = next(csv.reader([line]))
                except csv.Error:
                    if args.verbose:
                        print(f"[bad csv] {line}", file=sys.stderr)
                    continue

                if len(row) < len(active_header):
                    row = row + [""] * (len(active_header) - len(row))
                elif len(row) > len(active_header):
                    row = row[: len(active_header)]

                try:
                    writer.writerow(row)
                    f.flush()
                except OSError as e:
                    print(f"[ERROR] Failed to write row: {e}", file=sys.stderr)
                    break

                lines_written += 1
                if args.print_rows:
                    print(",".join(row))

    except KeyboardInterrupt:
        print(f"\nStopped. {lines_written} data rows written to {output_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Record SevenT STM32 IMU serial CSV to a file.")
    p.add_argument("serial_port", help="Serial port for the Nucleo board, e.g. COM11 or /dev/ttyUSB0")
    p.add_argument("output", nargs="?", help="Output CSV path (default: sevent_<timestamp>.csv)")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--print-rows", action="store_true")
    p.add_argument("--verbose", action="store_true")
    return p


def cli() -> None:
    try:
        run(build_arg_parser().parse_args())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()