# Test kode der printer mail i emails mappe (der er ikke tilføjet co2 lcd endnu)

import requests
import os

# ESP32 AP IP (always 192.168.4.1 in AP mode)
PRINT_URL = "http://192.168.4.1/print"

# Folder where your emails (txt files) are stored
EMAIL_FOLDER = "emails"

for filename in os.listdir(EMAIL_FOLDER):
    if not filename.endswith(".txt"):
        continue

    path = os.path.join(EMAIL_FOLDER, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    print(f"Printing: {filename}")

    # POST as raw plain text
    r = requests.post(PRINT_URL, data=text, headers={"Content-Type": "text/plain"})

    if r.status_code != 200:
        print("❌ Failed:", r.text)

print("✅ All emails sent to printer.")
