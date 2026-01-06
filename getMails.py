import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from bs4 import BeautifulSoup
import re
import textwrap

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# AUTH
def get_credentials():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


# EMAIL PARSING
def extract_html_part(payload):
    """Recursively extracts HTML part from email payload."""
    mime = payload.get("mimeType", "")
    body = payload.get("body", {}).get("data")

    if mime == "text/html" and body:
        return base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")

    if payload.get("parts"):
        for part in payload["parts"]:
            html = extract_html_part(part)
            if html:
                return html

    return None


def html_to_text(html, line_width=32):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts and styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Get raw text
    text = soup.get_text(separator="\n")

    # Remove zero-width and non-breaking junk
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)

    # Collapse excessive whitespace
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            wrapped = textwrap.fill(line, width=line_width)
            lines.append(wrapped)

    return "\n".join(lines)


def estimate_co2_grams(bytes_used, g_per_gb=100):
    """
    Estimer CO2 udledning fra data i gram.

    Args:
        bytes_used: total størrelse af emails i bytes
        g_per_gb: gram af CO2 per GB (default 0.1 kg/GB = 100 g/GB)
    """
    gb = bytes_used / 1_000_000_000  # convert bytes → GB
    return gb * g_per_gb


# GMAIL
def list_emails_in_inbox(service, max_results=10):
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])

    total_bytes = 0

    if not messages:
        print("No emails found.")
        return

    for msg in messages:
        msg_id = msg["id"]

        email = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full",
        ).execute()

        size_bytes = email.get("sizeEstimate", 0)
        total_bytes += size_bytes

        html = extract_html_part(email["payload"])

        if html:
            text = html_to_text(html)

            filename = f"email_{msg_id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✓ Saved TEXT: {filename}")
        else:
            print(f"✗ No HTML found for message {msg_id}")

    co2_g = estimate_co2_grams(total_bytes)

    print("\n===== SUMMARY =====")
    print(f"Emails processed: {len(messages)}")
    print(f"Total storage: {total_bytes} bytes")
    print(f"Estimated CO₂: {co2_g:.3f} g")


# MAIN
def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    list_emails_in_inbox(service, max_results=5)


if __name__ == "__main__":
    main()
