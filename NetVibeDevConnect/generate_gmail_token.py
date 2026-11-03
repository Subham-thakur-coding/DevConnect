import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "gmail_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
]


def main():
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            "credentials.json was not found. "
            "Download your OAuth client JSON and save it "
            "beside this script."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES,
    )

    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )

    token_data = json.loads(credentials.to_json())

    with TOKEN_FILE.open("w", encoding="utf-8") as file:
        json.dump(token_data, file, indent=2)

    print("\nAuthorization completed.")
    print(f"Token file created: {TOKEN_FILE}")
    print("Keep gmail_token.json private.")


if __name__ == "__main__":
    main()