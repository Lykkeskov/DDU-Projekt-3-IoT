import os.path

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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def list_emails_in_inbox(service):
    # Fetch all messages in INBOX
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=1000  # adjust as needed
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return

    print(f"Found {len(messages)} emails:\n")

    # Loop through each email
    for msg in messages:
        msg_id = msg["id"]

        # Get the full email message
        email = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        headers = email["payload"].get("headers", [])
        snippet = email.get("snippet", "")

        # Extract common fields
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "(No Date)")

        print("============================================")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Snippet: {snippet}")
        print("============================================\n")


def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    list_emails_in_inbox(service)


if __name__ == "__main__":
    main()
