import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


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


def extract_html_part(payload):
    """Extracts HTML part recursively."""
    mime = payload.get("mimeType", "")
    body = payload.get("body", {}).get("data")

    if mime == "text/html" and body:
        return base64.urlsafe_b64decode(body).decode("utf-8")

    if payload.get("parts"):
        for part in payload["parts"]:
            html = extract_html_part(part)
            if html:
                return html

    return None


def list_emails_in_inbox(service):
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=50
    ).execute()

    messages = results.get("messages", [])

    for msg in messages:
        msg_id = msg["id"]
        email = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        html = extract_html_part(email["payload"])

        if html:
            filename = f"email_{msg_id}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✓ Saved HTML: {filename}")
        else:
            print("No HTML found in this email.")


def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    list_emails_in_inbox(service)


if __name__ == "__main__":
    main()
