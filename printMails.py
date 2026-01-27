import serial
import time
import glob
import os

# CHANGE THIS if needed
SERIAL_PORT = "COM4"   # Windows example
BAUD_RATE = 115200
PRINTER_LINE_DELAY = 0.05  # seconds

def print_file(filepath, ser):
    print(f"Printing: {filepath}")

    ser.write(b"\n============================\n")
    ser.write(b"NEW EMAIL\n")
    ser.write(b"============================\n")

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            ser.write((line.strip() + "\n").encode("utf-8", errors="ignore"))
            time.sleep(PRINTER_LINE_DELAY)

    ser.write(b"\n-------- END EMAIL --------\n\n")
    time.sleep(0.5)


def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    time.sleep(2)  # allow ESP32 to reset

    files = sorted(glob.glob("email_*.txt"))

    if not files:
        print("No email files found.")
        return

    for file in files:
        print_file(file, ser)

    ser.close()
    print("All emails sent to printer.")


if __name__ == "__main__":
    main()
