# TVS_DND/dnd_api.py

import os
import requests

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


DND_API_URL = os.getenv("DND_API_URL")
DND_USERNAME = os.getenv("DND_USERNAME")
DND_PASSWORD = os.getenv("DND_PASSWORD")


def upload_dnd_file(file_path):
    """
    Upload cleaned DND file to blacklist API.
    """

    try:

        print("\nREQUEST DATA:")

        data = {
            "account": DND_USERNAME,
            "pin": DND_PASSWORD,
            "action": "activate"
        }

        print(data)

        print("\nFILE NAME:")
        print(os.path.basename(file_path))

        with open(file_path, "rb") as file_data:

            files = {
                "file": (
                    os.path.basename(file_path),
                    file_data,
                    "text/csv"
                )
            }

            print("\nUploading file to DND API...")

            response = requests.post(
                DND_API_URL,
                data=data,
                files=files,
                headers={
                    "Accept": "application/json"
                },
                timeout=120
            )

            print(f"Status Code: {response.status_code}")

            response_json = response.json()

            print("\nAPI Response:")
            print(response_json)

            return response_json

    except Exception as e:

        print(f"DND API Error: {e}")

        return None