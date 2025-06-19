#!/usr/bin/env python3
from backend.database import initialize_database
import logging
import sys

def main():
    logging.info("Starting database setup...")
    if initialize_database():
        logging.info("Database setup completed successfully")
        sys.exit(0)
    else:
        logging.error("Database setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
