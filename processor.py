# TVS_DND/processor.py

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import os
import requests
import logging

from dotenv import load_dotenv

from excel_handler import (
    process_csv,
    export_cleaned_file
)

from dnd_api import upload_dnd_file

from reply_generator import generate_reply

from tvs_ticket_actions import (
    assign_tvs_agent,
    send_tvs_reply,
    finalize_tvs_ticket
)

# =========================
# LOAD ENV
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# =========================
# LOGGING
# =========================

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# =========================
# ENV
# =========================

FRESHDESK_DOMAIN = os.getenv(
    "FRESHDESK_DOMAIN"
)

FRESHDESK_API_KEY = os.getenv(
    "FRESHDESK_API_KEY"
)

# =========================
# DOWNLOAD ATTACHMENT
# =========================

def download_attachment(
    attachment_url,
    file_name
):

    try:

        download_dir = "downloads"

        os.makedirs(
            download_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            download_dir,
            file_name
        )

        response = requests.get(
            attachment_url
        )

        with open(file_path, "wb") as f:

            f.write(response.content)

        logging.info(
            f"Attachment downloaded: "
            f"{file_path}"
        )

        return file_path

    except Exception as e:

        logging.error(
            f"Download Error: {e}"
        )

        return None


# =========================
# CLEANUP FILES
# =========================

def cleanup_files(*files):

    for file_path in files:

        try:

            if file_path and os.path.exists(file_path):

                os.remove(file_path)

                logging.info(
                    f"Deleted file: {file_path}"
                )

        except Exception as e:

            logging.error(
                f"Cleanup failed: {e}"
            )


# =========================
# FETCH TICKET
# =========================

def fetch_ticket(ticket_id):

    try:

        url = (
            f"https://{FRESHDESK_DOMAIN}"
            f"/api/v2/tickets/{ticket_id}"
        )

        response = requests.get(
            url,
            auth=(
                FRESHDESK_API_KEY,
                "X"
            )
        )

        if response.status_code != 200:

            logging.error(
                f"Failed fetching ticket: "
                f"{ticket_id}"
            )

            return None

        return response.json()

    except Exception as e:

        logging.error(
            f"Fetch Ticket Error: {e}"
        )

        return None


# =========================
# MAIN PROCESSOR
# =========================

def process_tvs_ticket(ticket_id):

    logging.info(
        "TVS DND PROCESS STARTED"
    )

    logging.info(
        f"Processing Ticket ID: "
        f"{ticket_id}"
    )

    # =========================
    # FETCH TICKET
    # =========================

    ticket = fetch_ticket(ticket_id)

    if not ticket:

        logging.error(
            "Ticket fetch failed"
        )

        return False

    # =========================
    # ASSIGN AGENT
    # =========================

    assign_tvs_agent(ticket_id)

    logging.info(
        "TVS Agent Assigned"
    )

    # =========================
    # FETCH ATTACHMENT
    # =========================

    attachments = ticket.get(
        "attachments",
        []
    )

    if not attachments:

        logging.error(
            "No attachment found"
        )

        return False

    attachment = attachments[0]

    attachment_url = attachment.get(
        "attachment_url"
    )

    file_name = attachment.get(
        "name"
    )

    logging.info(
        f"Attachment Found: "
        f"{file_name}"
    )

    # =========================
    # DOWNLOAD FILE
    # =========================

    downloaded_file = download_attachment(
        attachment_url,
        file_name
    )

    if not downloaded_file:

        logging.error(
            "Attachment download failed"
        )

        return False

    # =========================
    # PROCESS FILE
    # =========================

    numbers = process_csv(
        downloaded_file
    )

    logging.info(
        f"Total Numbers Found: "
        f"{len(numbers)}"
    )

    if not numbers:

        logging.error(
            "No numbers found"
        )

        cleanup_files(downloaded_file)

        return False

    # =========================
    # EXPORT CLEAN FILE
    # =========================

    cleaned_file = export_cleaned_file(
        numbers
    )

    logging.info(
        f"Cleaned File Created: "
        f"{cleaned_file}"
    )

    # =========================
    # DND API UPLOAD
    # =========================

    api_response = upload_dnd_file(
        cleaned_file
    )

    logging.info(
        f"DND Response: "
        f"{api_response}"
    )

    if not api_response:

        logging.error(
            "DND API Failed"
        )

        cleanup_files(
            downloaded_file,
            cleaned_file
        )

        return False

    # =========================
    # RESPONSE COUNTS
    # =========================

    response_data = api_response.get(
        "response",
        {}
    )

    inserted_count = response_data.get(
        "Inserted Rows",
        0
    )

    existing_count = response_data.get(
        "Existing Rows Updated",
        0
    )

    logging.info(
        f"Inserted Rows: "
        f"{inserted_count}"
    )

    logging.info(
        f"Existing Rows Updated: "
        f"{existing_count}"
    )

    # =========================
    # GENERATE REPLY
    # =========================

    reply_text = generate_reply(
        inserted_count,
        existing_count
    )

    logging.info(
        "Reply Generated"
    )

    # =========================
    # SEND REPLY
    # =========================

    reply_status = send_tvs_reply(
        ticket_id,
        reply_text
    )

    logging.info(
        f"Reply Sent Status: "
        f"{reply_status}"
    )

    # =========================
    # FINALIZE TICKET
    # =========================

    finalize_status = finalize_tvs_ticket(
        ticket_id
    )

    logging.info(
        f"Ticket Finalized: "
        f"{finalize_status}"
    )

    # =========================
    # CLEANUP FILES
    # =========================

    cleanup_files(
        downloaded_file,
        cleaned_file
    )

    logging.info(
        "TVS DND PROCESS COMPLETED"
    )

    return True