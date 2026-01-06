import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from bs4 import BeautifulSoup

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ---------- AUTH ----------
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


# ---------- EMAIL PARSING ----------
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


def html_to_text(html):
    """Convert HTML to clean plain text."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Clean excessive blank lines
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)

    return cleaned


# ---------- GMAIL ----------
def list_emails_in_inbox(service, max_results=10):
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])

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

        html = extract_html_part(email["payload"])

        if html:
            text = html_to_text(html)

            filename = f"email_{msg_id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✓ Saved TEXT: {filename}")
        else:
            print(f"✗ No HTML found for message {msg_id}")


# ---------- MAIN ----------
def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    list_emails_in_inbox(service, max_results=5)


if __name__ == "__main__":
    main()
