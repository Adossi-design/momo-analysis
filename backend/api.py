from flask import Flask, jsonify, request, render_template
from backend.database import get_transaction_count, get_transactions, get_summary_stats
import logging
from typing import Dict, Any
from pathlib import Path

def create_app() -> Flask:
    """Create and configure the Flask application"""
    app = Flask(__name__,
               template_folder=str(Path(__file__).parent.parent/'frontend'/'templates',
               static_folder=str(Path(__file__).parent.parent/'frontend'/'static')

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    @app.route('/')
    def dashboard() -> str:
        """Render the main dashboard page"""
        stats = get_summary_stats()
        return render_template('dashboard.html', 
                            total_transactions=stats.get('total_transactions', 0),
                            summary_stats=stats)

    @app.route('/api/health', methods=['GET'])
    def health_check() -> Dict[str, str]:
        """Health check endpoint"""
        return {'status': 'healthy'}

    @app.route('/api/transactions/count', methods=['GET'])
    def transaction_count() -> Dict[str, Any]:
        """Get total transaction count"""
        try:
            count = get_transaction_count()
            return {
                'status': 'success',
                'count': count,
                'message': f'Found {count} transactions'
            }
        except Exception as e:
            logging.error(f"API error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500

    @app.route('/api/transactions', methods=['GET'])
    def list_transactions() -> Dict[str, Any]:
        """List transactions with pagination"""
        try:
            limit = min(int(request.args.get('limit', 10)), 100)  # Max 100 transactions
            offset = int(request.args.get('offset', 0))
            
            transactions = get_transactions(limit=limit, offset=offset)
            
            return {
                'status': 'success',
                'count': len(transactions),
                'total': get_transaction_count(),
                'transactions': transactions
            }
        except Exception as e:
            logging.error(f"API error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500

    @app.route('/api/stats', methods=['GET'])
    def stats() -> Dict[str, Any]:
        """Get summary statistics"""
        try:
            stats = get_summary_stats()
            return {
                'status': 'success',
                'stats': stats
            }
        except Exception as e:
            logging.error(f"API error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500

    return app
