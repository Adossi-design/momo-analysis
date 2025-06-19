import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
import logging
import re
from datetime import datetime

def parse_sms_body(body: str) -> Dict[str, Any]:
    """Extract transaction details from SMS body text"""
    # Patterns to match different transaction types
    received_pattern = r"received (\d+,?\d*) RWF from (.+?) \("
    payment_pattern = r"payment of (\d+,?\d*) RWF to (.+?) (\d+)"
    transfer_pattern = r"(\d+,?\d*) RWF transferred to (.+?) \((\d+)\)"
    deposit_pattern = r"bank deposit of (\d+,?\d*) RWF"
    
    amount = None
    recipient = None
    sender = None
    tx_type = "other"
    
    try:
        if "received" in body:
            match = re.search(received_pattern, body)
            if match:
                tx_type = "incoming"
                amount = float(match.group(1).replace(",", ""))
                sender = match.group(2)
        elif "payment of" in body:
            match = re.search(payment_pattern, body)
            if match:
                tx_type = "payment"
                amount = float(match.group(1).replace(",", ""))
                recipient = f"{match.group(2)} {match.group(3)}"
        elif "transferred to" in body:
            match = re.search(transfer_pattern, body)
            if match:
                tx_type = "transfer"
                amount = float(match.group(1).replace(",", ""))
                recipient = f"{match.group(2)} ({match.group(3)})"
        elif "bank deposit" in body:
            match = re.search(deposit_pattern, body)
            if match:
                tx_type = "deposit"
                amount = float(match.group(1).replace(",", ""))
                
        # Extract date from body (present in all formats)
        date_match = re.search(r"at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", body)
        tx_date = datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S") if date_match else None
        
        return {
            'type': tx_type,
            'amount': amount,
            'recipient': recipient,
            'sender': sender,
            'date': tx_date.isoformat() if tx_date else None,
            'body': body
        }
        
    except Exception as e:
        logging.warning(f"Failed to parse SMS body: {e}")
        return None

def parse_xml(xml_file: str) -> Optional[List[Dict[str, Any]]]:
    """Parse SMS backup XML into transaction format"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        transactions = []
        for sms in root.findall('.//sms'):
            try:
                # Parse the SMS attributes and body
                tx_data = {
                    'protocol': sms.get('protocol'),
                    'address': sms.get('address'),
                    'date': datetime.fromtimestamp(int(sms.get('date'))/1000).isoformat(),
                    'type': sms.get('type'),
                    'body': sms.get('body'),
                    'readable_date': sms.get('readable_date')
                }
                
                # Extract transaction details from SMS body
                parsed = parse_sms_body(tx_data['body'])
                if not parsed:
                    continue
                    
                transaction = {
                    'date': parsed['date'] or tx_data['date'],
                    'type': parsed['type'],
                    'amount': parsed['amount'],
                    'recipient': parsed['recipient'],
                    'sender': parsed['sender'],
                    'body': tx_data['body'],
                    'readable_date': tx_data['readable_date']
                }
                
                if transaction['amount'] and transaction['date']:
                    transactions.append(transaction)
                    
            except Exception as e:
                logging.warning(f"Skipping malformed SMS: {e}")
                continue
                
        if not transactions:
            logging.error("No valid transactions found in XML file")
            return None
            
        logging.info(f"Successfully parsed {len(transactions)} transactions")
        return transactions
        
    except ET.ParseError as e:
        logging.error(f"XML parsing error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None
