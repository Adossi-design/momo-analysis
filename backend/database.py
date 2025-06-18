import sqlite3
from datetime import datetime
import logging

logging.basicConfig(filename='database_operations.log', level=logging.INFO)

def create_connection(db_file='momo_transactions.db'):
    """Create a database connection"""
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def setup_database():
    """Create database tables"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT,
            transaction_type TEXT,
            amount REAL,
            recipient TEXT,
            sender TEXT,
            message_body TEXT,
            readable_date TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create transaction types reference table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_types (
            type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE,
            description TEXT
        )
        ''')
        
        # Insert standard transaction types
        types = [
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
        
        cursor.executemany('''
        INSERT OR IGNORE INTO transaction_types (type_name, description)
        VALUES (?, ?)
        ''', types)
        
        conn.commit()
        logging.info("Database tables created successfully")
        return True
    except Exception as e:
        logging.error(f"Error setting up database: {e}")
        return False
    finally:
        conn.close()

def insert_transactions(transactions):
    """Insert multiple transactions into the database"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        for t in transactions:
            cursor.execute('''
            INSERT INTO transactions 
            (transaction_date, transaction_type, amount, recipient, sender, message_body, readable_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                t['date'].isoformat() if t['date'] else None,
                t['type'],
                t['amount'],
                t['recipient'],
                t['sender'],
                t['body'],
                t['readable_date']
            ))
        
        conn.commit()
        logging.info(f"Inserted {len(transactions)} transactions")
        return True
    except Exception as e:
        logging.error(f"Error inserting transactions: {e}")
        return False
    finally:
        conn.close()

def get_transactions(filters=None):
    """Retrieve transactions with optional filters"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        base_query = '''
        SELECT * FROM transactions
        '''
        
        params = []
        conditions = []
        
        if filters:
            if filters.get('type'):
                conditions.append('transaction_type = ?')
                params.append(filters['type'])
            
            if filters.get('start_date'):
                conditions.append('transaction_date >= ?')
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                conditions.append('transaction_date <= ?')
                params.append(filters['end_date'])
            
            if filters.get('min_amount'):
                conditions.append('amount >= ?')
                params.append(float(filters['min_amount']))
            
            if filters.get('max_amount'):
                conditions.append('amount <= ?')
                params.append(float(filters['max_amount']))
        
        if conditions:
            base_query += ' WHERE ' + ' AND '.join(conditions)
        
        base_query += ' ORDER BY transaction_date DESC'
        
        if filters and filters.get('limit'):
            base_query += ' LIMIT ?'
            params.append(int(filters['limit']))
        
        cursor.execute(base_query, params)
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching transactions: {e}")
        return []
    finally:
        conn.close()

def get_summary_stats():
    """Get summary statistics for dashboard"""
    conn = create_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        
        # Transaction counts by type
        cursor.execute('''
        SELECT transaction_type, COUNT(*) as count, SUM(amount) as total 
        FROM transactions 
        GROUP BY transaction_type
        ''')
        by_type = [dict(row) for row in cursor.fetchall()]
        
        # Monthly summary
        cursor.execute('''
        SELECT strftime('%Y-%m', transaction_date) as month, 
               COUNT(*) as count, 
               SUM(amount) as total
        FROM transactions
        GROUP BY month
        ORDER BY month
        ''')
        monthly = [dict(row) for row in cursor.fetchall()]
        
        # Recent transactions
        cursor.execute('''
        SELECT * FROM transactions
        ORDER BY transaction_date DESC
        LIMIT 5
        ''')
        recent = [dict(row) for row in cursor.fetchall()]
        
        return {
            'by_type': by_type,
            'monthly': monthly,
            'recent': recent
        }
    except Exception as e:
        logging.error(f"Error fetching summary stats: {e}")
        return {}
    finally:
        conn.close()
