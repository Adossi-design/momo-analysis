from flask import Flask, jsonify
from backend.database import get_transaction_count, get_transactions
import logging

def create_app():
    """Factory pattern Flask application creation"""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    @app.route('/api/transactions/count', methods=['GET'])
    def transaction_count():
        try:
            count = get_transaction_count()
            return jsonify({
                'status': 'success',
                'count': count,
                'message': f'Found {count} transactions'
            })
        except Exception as e:
            logging.error(f"API error: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/transactions', methods=['GET'])
    def list_transactions():
        try:
            limit = int(request.args.get('limit', 100))
            transactions = get_transactions(limit=limit)
            return jsonify({
                'status': 'success',
                'count': len(transactions),
                'transactions': transactions
            })
        except Exception as e:
            logging.error(f"API error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'})

    return app
