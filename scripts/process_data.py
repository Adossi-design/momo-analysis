from backend.data_processing import parse_xml
from backend.database import insert_transactions
import logging

logging.basicConfig(level=logging.INFO)

def main(xml_file_path):
    logging.info(f"Processing XML file: {xml_file_path}")
    
    # Parse XML
    transactions = parse_xml(xml_file_path)
    if not transactions:
        logging.error("No transactions were processed")
        return False
    
    logging.info(f"Successfully processed {len(transactions)} transactions")
    
    # Insert into database
    logging.info("Inserting transactions into database...")
    if insert_transactions(transactions):
        logging.info("Data loading completed successfully")
        return True
    else:
        logging.error("Data loading failed")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python process_data.py <path_to_xml_file>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    if not main(xml_file):
        sys.exit(1)
