import os
import base64
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

ESP32_URL = "http://192.168.4.1/print"  # ESP32 AP IP

EMAIL_FOLDER = "emails"  # local folder to save emails

def get_credentials():
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

def wrap_text(text, width=32):
    lines = []
    for paragraph in text.splitlines():
        while len(paragraph) > width:
            lines.append(paragraph[:width])
            paragraph = paragraph[width:]
        lines.append(paragraph)
    return "\n".join(lines)

def list_emails(service):
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=50).execute()
    messages = results.get("messages", [])
    email_texts = []
    total_bytes = 0
    for msg in messages:
        msg_id = msg["id"]
        email = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        text = extract_plain_text(email["payload"])
        if text:
            text = wrap_text(text)
            email_texts.append(text)
            total_bytes += len(text.encode("utf-8"))
            # save locally
            with open(f"{EMAIL_FOLDER}/email_{msg_id}.txt", "w", encoding="utf-8") as f:
                f.write(text)
    return email_texts, total_bytes

def co2_from_bytes(num_bytes):
    # 0.004 g CO2 per byte (adjust if needed)
    return num_bytes * 0.004

def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    emails, total_bytes = list_emails(service)
    co2_grams = co2_from_bytes(total_bytes)
    co2_message = f"CO2e: {co2_grams:.1f} g"

    # Send to printer
    for text in emails:
        r = requests.post(ESP32_URL, data=text, headers={"Content-Type": "text/plain"})
        if r.status_code != 200:
            print("Printer error:", r.text)

    # Send CO2 to LCD (optional arg)
    # Here we append co2_message to request; the ESP32 uses it to scroll line 2
    requests.post(ESP32_URL, data=" ", headers={"Content-Type": "text/plain"}, params={"co2": co2_message})

    print(f"✅ Printed {len(emails)} emails, total {total_bytes} bytes, CO2: {co2_grams:.1f} g")

if __name__ == "__main__":
    from googleapiclient.discovery import build
    main()
