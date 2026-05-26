from fastapi import FastAPI
from processor import process_tvs_ticket

app = FastAPI()

# =========================
# HEALTH CHECK
# =========================

@app.get("/")

def home():

    return {
        "status": "TVS DND API Running"
    }

# =========================
# PROCESS TICKET
# =========================

@app.post("/process_tvs_ticket")

def process_ticket(payload: dict):

    ticket_id = payload.get(
        "ticket_id"
    )

    if not ticket_id:

        return {
            "success": False,
            "message": "ticket_id missing"
        }

    result = process_tvs_ticket(
        ticket_id
    )

    return {
        "success": result,
        "ticket_id": ticket_id
    }