import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

DB_PATH = Path(__file__).parent / 'momo_transactions.db'

class Database:
    def __init__(self):
        self.conn = None
        os.makedirs(DB_PATH.parent, exist_ok=True)
    
    def __enter__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn.cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        self.conn.close()

def initialize_database():
    try:
        with Database() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_date TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    recipient TEXT,
                    sender TEXT,
                    message_body TEXT,
                    readable_date TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trans_date 
                ON transactions(transaction_date)
            ''')
        logging.info("Database initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Database init failed: {e}")
        return False

def insert_transactions(transactions: List[Dict[str, Any]]):
    try:
        with Database() as cursor:
            cursor.executemany('''
                INSERT INTO transactions VALUES (
                    NULL, ?, ?, ?, ?, ?, ?, ?
                )
            ''', [
                (
                    tx['date'], tx['type'], tx['amount'],
                    tx.get('recipient'), tx.get('sender'),
                    tx.get('body'), tx.get('readable_date')
                ) for tx in transactions
            ])
        return True
    except Exception as e:
        logging.error(f"Insert failed: {e}")
        return False

def get_transactions(limit: int = 100) -> List[Dict[str, Any]]:
    try:
        with Database() as cursor:
            cursor.execute('''
                SELECT * FROM transactions 
                ORDER BY transaction_date DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return []

def get_summary_stats() -> Dict[str, Any]:
    try:
        with Database() as cursor:
            cursor.execute('''
                SELECT COUNT(*) as total FROM transactions
            ''')
            total = cursor.fetchone()['total']
            
            cursor.execute('''
                SELECT transaction_type, COUNT(*) as count, 
                SUM(amount) as total FROM transactions
                GROUP BY transaction_type
            ''')
            by_type = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT strftime('%Y-%m', transaction_date) as month,
                COUNT(*) as count, SUM(amount) as total
                FROM transactions GROUP BY month
                ORDER BY month
            ''')
            monthly = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_transactions': total,
                'by_type': by_type,
                'monthly': monthly
            }
    except Exception as e:
        logging.error(f"Stats failed: {e}")
        return {}
