from flask import Flask, jsonify, request
from .database import get_transactions, get_summary_stats
import logging

logging.basicConfig(filename='api.log', level=logging.INFO)

app = Flask(__name__)

@app.route('/api/transactions', methods=['GET'])
def api_get_transactions():
    try:
        filters = {
            'type': request.args.get('type'),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'min_amount': request.args.get('min_amount'),
            'max_amount': request.args.get('max_amount'),
            'limit': request.args.get('limit', default=100)
        }
        
        transactions = get_transactions(filters)
        return jsonify({
            'success': True,
            'count': len(transactions),
            'data': transactions
        })
    except Exception as e:
        logging.error(f"API Error in /transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/summary', methods=['GET'])
def api_get_summary():
    try:
        summary = get_summary_stats()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logging.error(f"API Error in /summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/types', methods=['GET'])
def api_get_types():
    try:
        
        types = [
            {'id': 1, 'name': 'incoming', 'description': 'Money received'},
            {'id': 2, 'name': 'payment', 'description': 'Payment to merchant'},
            {'id': 3, 'name': 'transfer', 'description': 'Transfer to number'},
            {'id': 4, 'name': 'deposit', 'description': 'Bank deposit'},
            {'id': 5, 'name': 'airtime', 'description': 'Airtime purchase'},
            {'id': 6, 'name': 'cash_power', 'description': 'Cash power payment'},
            {'id': 7, 'name': 'withdrawal', 'description': 'Agent withdrawal'},
            {'id': 8, 'name': 'bundle', 'description': 'Data bundle'},
            {'id': 9, 'name': 'other', 'description': 'Other transactions'}
        ]
        return jsonify({
            'success': True,
            'data': types
        })
    except Exception as e:
        logging.error(f"API Error in /types: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
