from flask import Flask, jsonify, request, render_template
from backend.database import get_transaction_count, get_transactions, get_summary_stats
import logging
from pathlib import Path
from datetime import datetime

def create_app() -> Flask:
    app = Flask(__name__,
               template_folder=str(Path(__file__).parent.parent/'frontend'/'templates'),
               static_folder=str(Path(__file__).parent.parent/'frontend'/'static'))

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    @app.route('/')
    def dashboard():
        """Main dashboard with server-side rendering"""
        stats = get_summary_stats()
        recent_transactions = get_transactions(limit=5)
        return render_template('dashboard.html',
                            total_transactions=stats['total_transactions'],
                            monthly_stats=stats['monthly'],
                            recent_transactions=recent_transactions,
                            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    @app.route('/api/transactions')
    def api_transactions():
        """API endpoint for transactions (used by AJAX)"""
        try:
            limit = min(int(request.args.get('limit', 10)), 100)
            transactions = get_transactions(limit=limit)
            return jsonify({
                'status': 'success',
                'data': transactions,
                'count': len(transactions)
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/stats')
    def api_stats():
        """API endpoint for statistics (used by AJAX)"""
        try:
            return jsonify({
                'status': 'success',
                'data': get_summary_stats()
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app
