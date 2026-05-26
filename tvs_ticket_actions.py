# Shared/tvs_ticket_actions.py

import os
import requests
import logging

from pathlib import Path
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from tvs_constants import TVS_CUSTOM_FIELDS

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
# ENV VARIABLES
# =========================

FRESHDESK_DOMAIN = os.getenv(
    "FRESHDESK_DOMAIN",
    ""
).strip()

FRESHDESK_API_KEY = os.getenv(
    "FRESHDESK_API_KEY",
    ""
).strip()

TVS_AI_AGENT_ID = int(
    os.getenv(
        "FRESHDESK_PROV_AI_AGENT_ID",
        "0"
    ).strip()
)

AUTH = HTTPBasicAuth(
    FRESHDESK_API_KEY,
    "X"
)

# =========================
# ASSIGN TVS AGENT
# =========================

def assign_tvs_agent(ticket_id: int):

    try:

        url = (
            f"https://{FRESHDESK_DOMAIN}"
            f"/api/v2/tickets/{ticket_id}"
        )

        payload = {

            "responder_id":
                TVS_AI_AGENT_ID,

            "type":
                "Service Request",

            "custom_fields":
                TVS_CUSTOM_FIELDS
        }

        print("\n======================")
        print("ASSIGNING TVS AGENT")
        print("======================")

        print("Payload:", payload)

        res = requests.put(
            url,
            json=payload,
            auth=AUTH
        )

        print("Status Code:", res.status_code)
        print("Response:", res.text)

        logging.info(
            f"Assign TVS Agent Response: "
            f"{res.status_code} - {res.text}"
        )

        return res.status_code == 200

    except Exception as e:

        logging.error(
            f"Assign TVS Agent Exception: {e}"
        )

        return False


# =========================
# SEND TVS REPLY
# =========================

def send_tvs_reply(
    ticket_id: int,
    reply_text: str
):

    try:

        ticket_url = (
            f"https://{FRESHDESK_DOMAIN}"
            f"/api/v2/tickets/{ticket_id}"
        )

        reply_url = (
            f"https://{FRESHDESK_DOMAIN}"
            f"/api/v2/tickets/{ticket_id}/reply"
        )

        # =========================
        # FETCH TICKET
        # =========================

        ticket_resp = requests.get(
            ticket_url,
            auth=AUTH
        )

        if ticket_resp.status_code != 200:

            logging.error(
                f"Failed fetching ticket "
                f"{ticket_id}"
            )

            return False

        ticket_data = ticket_resp.json()

        requester_email = ticket_data.get(
            "email"
        )

        cc_emails = ticket_data.get(
            "cc_emails",
            []
        )

        logging.info(
            f"Requester Email: "
            f"{requester_email}"
        )

        logging.info(
            f"CC Emails: "
            f"{cc_emails}"
        )

        # =========================
        # PREPARE PAYLOAD
        # =========================

        payload = {

            "body":
                reply_text.replace(
                    "\n",
                    "<br>"
                )
        }

        if requester_email:

            payload["to_emails"] = [
                requester_email
            ]

        if cc_emails:

            payload["cc_emails"] = cc_emails

        # =========================
        # SEND REPLY
        # =========================

        resp = requests.post(
            reply_url,
            auth=AUTH,
            json=payload
        )

        logging.info(
            f"TVS Reply Response: "
            f"{resp.status_code} - {resp.text}"
        )

        return resp.status_code in (200, 201)

    except Exception as e:

        logging.error(
            f"TVS Reply Exception: {e}"
        )

        return False

# =========================
# FINALIZE TVS TICKET
# =========================

def finalize_tvs_ticket(ticket_id: int):

    try:

        # =========================
        # FETCH EXISTING TICKET
        # =========================

        get_url = (
            f"https://{FRESHDESK_DOMAIN}"
            f"/api/v2/tickets/{ticket_id}"
        )

        get_res = requests.get(
            get_url,
            auth=AUTH
        )

        if get_res.status_code != 200:

            logging.error(
                f"Unable to fetch ticket "
                f"before resolve: "
                f"{get_res.text}"
            )

            return False

        ticket = get_res.json()

        existing_type = ticket.get(
            "type"
        ) or "Service Request"

        existing_priority = ticket.get(
            "priority"
        ) or 2

        # =========================
        # FINALIZE PAYLOAD
        # =========================

        payload = {

            # RESOLVED
            "status": 4,

            # KEEP EXISTING PRIORITY
            "priority":
                existing_priority,

            # KEEP EXISTING TYPE
            "type":
                existing_type,

            # AGENT
            "responder_id":
                TVS_AI_AGENT_ID,

            # CUSTOM FIELDS
            "custom_fields":
                TVS_CUSTOM_FIELDS
        }

        print("\n======================")
        print("FINALIZING TVS TICKET")
        print("======================")

        print("Payload:", payload)

        put_url = (
            f"https://{FRESHDESK_DOMAIN}"
            f"/api/v2/tickets/{ticket_id}"
        )

        res = requests.put(
            put_url,
            json=payload,
            auth=AUTH
        )

        print("Status Code:", res.status_code)
        print("Response:", res.text)

        logging.info(
            f"Finalize TVS Ticket Response: "
            f"{res.status_code} - {res.text}"
        )

        return res.status_code == 200

    except Exception as e:

        logging.error(
            f"Finalize TVS Ticket Exception: {e}"
        )

        return False