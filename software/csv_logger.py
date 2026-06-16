"""
csv_logger.py
Captures IMU CSV data from STM32F411RE over UART (via ST-Link USB).
Header is written once on the first row, data fills the rest.
Port: COM11 | Baud: 115200
"""

import serial
import datetime
import sys
import os

# ── Configuration ─────────────────────────────────────────────────────────────
PORT      = "COM11"
BAUD_RATE = 115200
TIMEOUT_S = 2
# ──────────────────────────────────────────────────────────────────────────────

EXPECTED_HEADER = "event,timestamp_ms,accel_x_ms2,accel_y_ms2,accel_z_ms2,gyro_x_dps,gyro_y_dps,gyro_z_dps"


def make_filename() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"khoa_{timestamp}.csv"


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

    print(f"Connected. Saving to: {os.path.abspath(filename)}")
    print("Waiting for MCU header...\n")
    print("Press Ctrl+C to stop.\n")

    lines_written  = 0
    header_written = False

    try:
        with open(filename, "w", newline="") as f:
            while True:
                raw = ser.readline()

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

                # ── First line must be the header ─────────────────────────────
                if not header_written:
                    if line.startswith("event,"):
                        if line != EXPECTED_HEADER:
                            print(f"[WARN] Header mismatch:")
                            print(f"       got:      {line}")
                            print(f"       expected: {EXPECTED_HEADER}")
                        f.write(line + "\n")
                        f.flush()
                        header_written = True
                        print(f"  [HEADER] {line}\n")
                    else:
                        # Data arrived before header — write expected header first
                        print("[WARN] Data received before header — inserting expected header")
                        f.write(EXPECTED_HEADER + "\n")
                        f.flush()
                        header_written = True
                        # fall through to write this line as data below

                # ── Data rows ─────────────────────────────────────────────────
                if header_written and line.startswith("imu_data,"):
                    f.write(line + "\n")
                    f.flush()
                    lines_written += 1

                    if lines_written == 1 or lines_written % 20 == 0:
                        print(f"  [{lines_written:>6} rows] {line}")

    except KeyboardInterrupt:
        print(f"\n\nStopped. {lines_written} data rows written to {filename}")

    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed.")


if __name__ == "__main__":
    main()