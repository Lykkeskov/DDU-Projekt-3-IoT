import os
import base64
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ------------------ CONFIG ------------------ #
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
ESP32_URL = "http://10.147.138.223/print"  # Change to your ESP32 IP
MAX_LINE_LENGTH = 32  # Adjust to printer width
# -------------------------------------------- #

def get_credentials():
    """Authenticate with Gmail and return credentials."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def extract_plain_text(payload):
    """Recursively extract plain text from email payload."""
    mime = payload.get("mimeType", "")
    body = payload.get("body", {}).get("data")

    if mime == "text/plain" and body:
        return base64.urlsafe_b64decode(body).decode("utf-8")

    if payload.get("parts"):
        for part in payload["parts"]:
            text = extract_plain_text(part)
            if text:
                return text

    return None


def format_for_printer(text):
    """Split text into lines that fit printer width."""
    lines = []
    for paragraph in text.splitlines():
        while len(paragraph) > 0:
            line = paragraph[:MAX_LINE_LENGTH]
            lines.append(line)
            paragraph = paragraph[MAX_LINE_LENGTH:]
    return "\n".join(lines)


def calculate_co2(email_sizes):
    """
    Estimate CO2 emission based on email size.
    Uses:
        - 0.3 g CO2 per KB
        - 50 g CO2 per MB
    Returns total in grams.
    """
    total = 0
    for size in email_sizes:
        if size < 1000:  # KB
            total += 0.3
        else:  # MB
            total += 50
    return round(total, 2)


def fetch_emails(service, max_results=10):
    """Fetch the latest emails from Gmail inbox."""
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    emails = []
    sizes = []

    for msg in messages:
        msg_id = msg["id"]
        email = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        plain_text = extract_plain_text(email["payload"])
        if plain_text:
            emails.append(format_for_printer(plain_text))
            sizes.append(email.get("sizeEstimate", 0))
        else:
            emails.append("[No plain text found]")
            sizes.append(email.get("sizeEstimate", 0))

    return emails, sizes


def send_to_esp32(email_text, co2_text):
    """Send email text and CO2 info to ESP32 via HTTP POST."""
    data = {
        "plain": email_text,
        "co2": co2_text
    }
    try:
        response = requests.post(ESP32_URL, data=data, timeout=5)
        if response.status_code == 200:
            print("✅ Sent to ESP32 successfully")
        else:
            print(f"⚠️ ESP32 responded with status: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Failed to send to ESP32: {e}")


def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    emails, sizes = fetch_emails(service, max_results=10)
    total_co2 = calculate_co2(sizes)
    co2_text = f"CO2: {total_co2} g"

    for i, email in enumerate(emails):
        print(f"\n--- Printing email {i+1} ---\n")
        print(email)
        send_to_esp32(email, co2_text)


if __name__ == "__main__":
    from googleapiclient.discovery import build
    main()
