import sqlite3
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    filename='backend/database_operations.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
DB_PATH = str(Path(__file__).parent / 'momo_transactions.db')
DEFAULT_TRANSACTION_TYPES = [
    ('incoming', 'Money received from another user'),
    ('payment', 'Payment to a merchant or code holder'),
    ('transfer', 'Transfer to another mobile number'),
    ('deposit', 'Bank deposit to MoMo account'),
    ('airtime', 'Airtime purchase'),
    ('cash_power', 'Cash power payment'),
    ('withdrawal', 'Cash withdrawal from agent'),
    ('bundle', 'Internet/voice bundle purchase'),
    ('other', 'Other transaction types')
]

def create_connection(db_file: str = DB_PATH) -> Optional[sqlite3.Connection]:
    """Create and return a database connection"""
    try:
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        logging.error(f"Connection error: {str(e)}", exc_info=True)
        return None

def execute_query(query: str, params: tuple = (), commit: bool = False) -> bool:
    """Generic query executor"""
    conn = create_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return True
    except Exception as e:
        logging.error(f"Query failed: {str(e)}")
        return False
    finally:
        conn.close()

def setup_database() -> bool:
    """Initialize database tables"""
    queries = [
        '''CREATE TABLE IF NOT EXISTS transaction_types (
            type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE NOT NULL,
            description TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS transactions (
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
        )''',
        '''CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(transaction_date)''',
        '''CREATE INDEX IF NOT EXISTS idx_trans_type ON transactions(transaction_type)'''
    ]
    
    try:
        # Execute schema creation
        for query in queries:
            if not execute_query(query, commit=True):
                return False
                
        # Insert default types
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.executemany('''
            INSERT OR IGNORE INTO transaction_types (type_name, description)
            VALUES (?, ?)
            ''', DEFAULT_TRANSACTION_TYPES)
            conn.commit()
            return True
        finally:
            conn.close()
            
    except Exception as e:
        logging.critical(f"Setup failed: {str(e)}")
        return False

def insert_transactions(transactions: List[Dict[str, Any]]) -> bool:
    """Bulk insert transactions with validation"""
    if not transactions:
        return False

    conn = create_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
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
        
        conn.commit()
        logging.info(f"Inserted {len(transactions)} transactions")
        return True
    except Exception as e:
        logging.error(f"Insert failed: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()
