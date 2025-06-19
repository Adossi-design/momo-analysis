#!/usr/bin/env python3
import sys
from backend.data_processing import parse_xml
from backend.database import insert_transactions
import logging

def main(xml_file: str):
    logging.info(f"Processing XML file: {xml_file}")
    
    transactions = parse_xml(xml_file)
    if not transactions:
        logging.error("Failed to parse transactions from XML")
        return False
        
    if not insert_transactions(transactions):
        logging.error("Failed to insert transactions into database")
        return False
        
    logging.info("Data processing completed successfully")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_data.py <path_to_xml_file>")
        sys.exit(1)
        
    if not main(sys.argv[1]):
        sys.exit(1)
