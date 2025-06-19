import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database import initialize_database
import logging

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("Starting database setup...")
    if initialize_database():
        logging.info("Database setup completed successfully")
    else:
        logging.error("Database setup failed")

if __name__ == "__main__":
    main()
