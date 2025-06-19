import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import logging
from datetime import datetime

def parse_xml(xml_file: str) -> Optional[List[Dict[str, Any]]]:
    """Parse XML transaction data into Python dictionaries"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        transactions = []
        for item in root.findall('.//transaction'):
            try:
                transaction = {
                    'date': item.find('date').text if item.find('date') is not None else None,
                    'type': item.find('type').text if item.find('type') is not None else 'other',
                    'amount': float(item.find('amount').text) if item.find('amount') is not None else 0.0,
                    'recipient': item.find('recipient').text if item.find('recipient') is not None else None,
                    'sender': item.find('sender').text if item.find('sender') is not None else None,
                    'body': item.find('body').text if item.find('body') is not None else None,
                    'readable_date': item.find('readable_date').text if item.find('readable_date') is not None else None
                }
                
                # Validate required fields
                if transaction['date'] and transaction['amount']:
                    transactions.append(transaction)
                    
            except Exception as e:
                logging.warning(f"Skipping malformed transaction: {e}")
                continue
                
        if not transactions:
            logging.error("No valid transactions found in XML file")
            return None
            
        logging.info(f"Successfully parsed {len(transactions)} transactions from XML")
        return transactions
        
    except ET.ParseError as e:
        logging.error(f"XML parsing error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error parsing XML: {e}")
        return None
