"""
csv_logger.py
Captures IMU CSV data from STM32F411RE over UART (via ST-Link USB).
Header is written once on the first row, data fills the rest.
Port: COM11 | Baud: 115200
"""

import csv
import serial
import datetime
import sys
import os

# ── Configuration ─────────────────────────────────────────────────────────────
PORT      = "COM11"
BAUD_RATE = 115200
TIMEOUT_S = 2
# ──────────────────────────────────────────────────────────────────────────────

EXPECTED_FIELDS = [
    "event", "timestamp_ms",
    "accel_x_ms2", "accel_y_ms2", "accel_z_ms2",
    "gyro_x_dps",  "gyro_y_dps",  "gyro_z_dps",
]
EXPECTED_HEADER = ",".join(EXPECTED_FIELDS)


def make_filename() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"khoa_{timestamp}.csv"


def parse_row(line: str) -> list[str] | None:
    try:
        rows = list(csv.reader([line]))
        if rows:
            return rows[0]
    except csv.Error:
        return None


def main():
    filename = make_filename()

    print(f"Opening {PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT_S)
    except serial.SerialException as e:
        print(f"[ERROR] Could not open {PORT}: {e}")
        print("  - Check the port is correct (Device Manager → Ports)")
        print("  - Make sure no other program (e.g. PuTTY) has it open")
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] Invalid serial parameters: {e}")
        sys.exit(1)

    print(f"Connected. Saving to: {os.path.abspath(filename)}")

    lines_written  = 0
    header_written = False

    try:
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)

            while True:

                try:
                    raw = ser.readline()
                except serial.SerialException as e:
                    print(f"[ERROR] Serial read error: {e} — attempting to continue")
                    continue
                except OSError as e:
                    print(f"[ERROR] OS-level serial error: {e} — device may have disconnected")
                    break

                if not raw:
                    print("[WARN] No data received — check MCU is running and baud rate matches")
                    continue

                try:
                    line = raw.decode("utf-8").rstrip("\r\n")
                except UnicodeDecodeError:
                    print(f"[WARN] Garbled line skipped: {raw!r}")
                    continue

                if not line:
                    continue

                fields = parse_row(line)
                if fields is None:
                    print(f"[WARN] Malformed CSV line skipped: {line!r}")
                    continue

                # ── First line must be the header ─────────────────────────────
                if not header_written:
                    if fields[0] == "event":
                        if fields != EXPECTED_FIELDS:
                            print(f"[WARN] Header mismatch:")
                            print(f"       got:      {','.join(fields)}")
                            print(f"       expected: {EXPECTED_HEADER}")
                        try:
                            writer.writerow(fields)
                            f.flush()
                        except OSError as e:
                            print(f"[ERROR] Failed to write header: {e}")
                            break
                        header_written = True
                        print(f"  [HEADER] {','.join(fields)}\n")
                    else:
                        # Data arrived before header — write expected header first
                        print("[WARN] Data received before header — inserting expected header")
                        try:
                            writer.writerow(EXPECTED_FIELDS)
                            f.flush()
                        except OSError as e:
                            print(f"[ERROR] Failed to write fallback header: {e}")
                            break
                        header_written = True
                        # fall through to write this line as data below

                # ── Data rows ─────────────────────────────────────────────────
                if header_written and fields[0] == "imu_data":
                    if len(fields) != len(EXPECTED_FIELDS):
                        print(f"[WARN] Unexpected field count ({len(fields)}), skipping: {line!r}")
                        continue

                    try:
                        writer.writerow(fields)
                        f.flush()
                    except OSError as e:
                        print(f"[ERROR] Failed to write data row: {e}")
                        break
                    lines_written += 1

                    if lines_written == 1 or lines_written % 20 == 0:
                        print(f"  [{lines_written:>6} rows] {','.join(fields)}")

    except KeyboardInterrupt:
        print(f"\n\nStopped. {lines_written} data rows written to {filename}")
    except OSError as e:
        print(f"[ERROR] Could not open output file '{filename}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        sys.exit(1)
    finally:
        try:
            if ser.is_open:
                ser.close()
                print("Serial port closed.")
        except Exception as e:
            print(f"[WARN] Error closing serial port: {e}")


if __name__ == "__main__":
    main()