import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database import setup_database
import logging

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("Starting database setup...")
    if setup_database():
        logging.info("Database setup completed successfully")
    else:
        logging.error("Database setup failed")

if __name__ == "__main__":
    main()
