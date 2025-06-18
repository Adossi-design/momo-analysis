from database import setup_database
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
