import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend/database.log'),
        logging.StreamHandler()
    ]
)

DB_PATH = Path(__file__).parent / 'momo_transactions.db'

class Database:
    """Database connection manager with context support"""
    
    def __init__(self):
        self.conn = None
        self._ensure_db_dir()
        
    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        os.makedirs(DB_PATH.parent, exist_ok=True)
    
    def __enter__(self):
        """Context manager entry point"""
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn.cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
            logging.error(f"Database error: {exc_val}")
        self.conn.close()

def initialize_database() -> bool:
    """Create database tables and seed initial data"""
    try:
        with Database() as cursor:
            # Transaction types reference table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_types (
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT UNIQUE NOT NULL,
                description TEXT
            )
            ''')
            
            # Transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                recipient TEXT,
                sender TEXT,
                message_body TEXT,
                readable_date TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_type) REFERENCES transaction_types(type_name)
            )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(transaction_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trans_type ON transactions(transaction_type)')
            
            # Seed transaction types
            cursor.executemany('''
            INSERT OR IGNORE INTO transaction_types (type_name, description)
            VALUES (?, ?)
            ''', [
                ('incoming', 'Money received from another user'),
                ('payment', 'Payment to a merchant or code holder'),
                ('transfer', 'Transfer to another mobile number'),
                ('deposit', 'Bank deposit to MoMo account'),
                ('airtime', 'Airtime purchase'),
                ('cash_power', 'Cash power payment'),
                ('withdrawal', 'Cash withdrawal from agent'),
                ('bundle', 'Internet/voice bundle purchase'),
                ('other', 'Other transaction types')
            ])
            
        logging.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logging.critical(f"Database initialization failed: {e}")
        return False

def insert_transactions(transactions: List[Dict[str, Any]]) -> bool:
    """Insert multiple transactions into the database"""
    if not transactions:
        logging.warning("Empty transactions list received")
        return False
        
    try:
        with Database() as cursor:
            cursor.executemany('''
            INSERT INTO transactions 
            (transaction_date, transaction_type, amount, recipient, sender, message_body, readable_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [(
                t.get('date'),
                t.get('type'),
                t.get('amount', 0),
                t.get('recipient'),
                t.get('sender'),
                t.get('body'),
                t.get('readable_date')
            ) for t in transactions])
            
        logging.info(f"Successfully inserted {len(transactions)} transactions")
        return True
        
    except Exception as e:
        logging.error(f"Failed to insert transactions: {e}")
        return False

def get_transaction_count() -> int:
    """Get total number of transactions"""
    try:
        with Database() as cursor:
            return cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    except Exception as e:
        logging.error(f"Failed to get transaction count: {e}")
        return 0
