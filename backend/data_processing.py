import xml.etree.ElementTree as ET
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename='momo_processing.log', level=logging.INFO)

TRANSACTION_PATTERNS = {
    'incoming': r'received (\d+,?\d*) RWF from',
    'payment': r'Your payment of (\d+,?\d*) RWF to',
    'transfer': r'transferred (\d+,?\d*) RWF to',
    'deposit': r'bank deposit of (\d+,?\d*) RWF',
    'airtime': r'payment of (\d+,?\d*) RWF to Airtime',
    'cash_power': r'payment of (\d+,?\d*) RWF to MTN Cash Power',
    'withdrawal': r'withdrawn (\d+,?\d*) RWF from',
    'bundle': r'purchased (.*) bundle of'
}

def parse_amount(amount_str):
    """Convert amount string to integer"""
    try:
        return int(amount_str.replace(',', ''))
    except (ValueError, AttributeError):
        return None

def parse_date(timestamp):
    """Convert epoch timestamp to datetime"""
    try:
        return datetime.fromtimestamp(int(timestamp)/1000)
    except (ValueError, TypeError):
        return None

def categorize_transaction(body):
    """Categorize transaction based on message content"""
    if not body:
        return 'other'
    
    body = body.lower()
    for t_type, pattern in TRANSACTION_PATTERNS.items():
        if re.search(pattern, body):
            return t_type
    return 'other'

def process_sms(sms_element):
    """Process individual SMS element"""
    try:
        body = sms_element.get('body', '')
        date = parse_date(sms_element.get('date'))
        amount = None
        transaction_type = categorize_transaction(body)
        
        # Extract amount based on transaction type
        if transaction_type in TRANSACTION_PATTERNS:
            match = re.search(TRANSACTION_PATTERNS[transaction_type], body.lower())
            if match:
                amount = parse_amount(match.group(1))
        
        # Extract recipient/sender
        recipient = None
        sender = None
        
        if transaction_type == 'incoming':
            match = re.search(r'from (.*?) \(', body)
            if match:
                sender = match.group(1).strip()
        elif transaction_type in ['payment', 'transfer']:
            match = re.search(r'to (.*?)( \d|$)', body)
            if match:
                recipient = match.group(1).strip()
        
        return {
            'date': date,
            'body': body,
            'type': transaction_type,
            'amount': amount,
            'recipient': recipient,
            'sender': sender,
            'readable_date': sms_element.get('readable_date')
        }
    except Exception as e:
        logging.error(f"Error processing SMS: {e}")
        return None

def parse_xml(xml_file):
    """Parse the XML file and return processed transactions"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        transactions = []
        for sms in root.findall('sms'):
            processed = process_sms(sms)
            if processed:
                transactions.append(processed)
        
        logging.info(f"Successfully processed {len(transactions)} transactions")
        return transactions
    except Exception as e:
        logging.error(f"Error parsing XML: {e}")
        return []
                ]
