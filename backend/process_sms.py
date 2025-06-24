import xml.etree.ElementTree as ET
import re
import json
import logging
from datetime import datetime

# Logging for ignored messages
logging.basicConfig(filename='unprocessed_messages.log', level=logging.INFO)

CATEGORIES = {
    "received": r"You have received (\d+) RWF from (.+?)\. Transaction ID: (\d+)\. Date: (.+?)\.",
    "payment": r"Your payment of (\d+) RWF to (.+?) has been completed\. Date: (.+?)\.",
    "airtime": r"\*162\*TxId:\d+\*S\*Your payment of (\d+) RWF to Airtime has been completed\. Fee: \d+ RWF\. Date: (.+?)\.",
    "withdrawal": r"withdrawn (\d+) RWF on ([0-9\-: ]+)",
    "bundle": r"purchased an internet bundle of (.+?) for (\d+) RWF",
    "cashpower": r"Cash Power token .* worth (\d+) RWF",
    "bank": r"Bank transfer of (\d+) RWF .* Date: (.+?)\.",
}

def parse_sms_body(body):
    for category, pattern in CATEGORIES.items():
        match = re.search(pattern, body)
        if match:
            return extract_fields(category, match)
    logging.info(f"Ignored SMS: {body}")
    return None

def extract_fields(category, match):
    if category == "received":
        amount, sender, tx_id, date = match.groups()
        return {
            "type": "Incoming Money",
            "amount": int(amount),
            "party": sender,
            "tx_id": tx_id,
            "date": format_date(date)
        }
    elif category == "payment":
        amount, receiver, date = match.groups()
        return {
            "type": "Payment",
            "amount": int(amount),
            "party": receiver,
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "airtime":
        amount, date = match.groups()
        return {
            "type": "Airtime Purchase",
            "amount": int(amount),
            "party": "Airtime",
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "withdrawal":
        amount, date = match.groups()
        return {
            "type": "Withdrawal",
            "amount": int(amount),
            "party": "Agent",
            "tx_id": None,
            "date": format_date(date)
        }
    elif category == "bundle":
        bundle, amount = match.groups()
        return {
            "type": "Bundle Purchase",
            "amount": int(amount),
            "party": bundle,
            "tx_id": None,
            "date": None
        }
    elif category == "cashpower":
        amount = match.group(1)
        return {
            "type": "Cash Power Payment",
            "amount": int(amount),
            "party": "Cash Power",
            "tx_id": None,
            "date": None
        }
    elif category == "bank":
        amount, date = match.groups()
        return {
            "type": "Bank Transfer",
            "amount": int(amount),
            "party": "Bank",
            "tx_id": None,
            "date": format_date(date)
        }
    return None

def format_date(raw_date):
    try:
        return datetime.strptime(raw_date.strip(), "%Y-%m-%d %H:%M:%S").isoformat()
    except:
        return None

def process_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    records = []

    for sms in root.findall('sms'):
        body = sms.find('body').text.strip()
        parsed = parse_sms_body(body)
        if parsed:
            records.append(parsed)

    with open('cleaned_data.json', 'w') as f:
        json.dump(records, f, indent=4)

if _name_ == "_main_":
    process_xml("DataWorld/Data/modified_sms_v2.xml")

