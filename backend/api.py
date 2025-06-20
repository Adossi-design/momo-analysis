from flask import Flask, jsonify, request, render_template
from backend.database import get_transaction_count, get_transactions, get_summary_stats
import logging
from pathlib import Path
from datetime import datetime

def create_app():
    app = Flask(__name__,
               template_folder=str(Path(__file__).parent.parent/'frontend'/'templates'),
               static_folder=str(Path(__file__).parent.parent/'frontend'/'static'))

    logging.basicConfig(level=logging.INFO)

    @app.template_filter('thousands')
    def format_thousands(value):
        return "{:,.0f}".format(value)
    
    @app.route('/')
    def dashboard():
        stats = get_summary_stats()
        monthly_stats = list(stats['monthly'])
        type_stats = list(stats['by_type'])
        
        current_month = datetime.now().strftime('%Y-%m')
        current_month_data = next(
            (m for m in monthly_stats if m['month'] == current_month),
            {'total': 0, 'count': 0}
        )
        
        return render_template(
            'dashboard.html',
            total_transactions=stats['total_transactions'],
            current_month=current_month_data,
            monthly_stats=monthly_stats,
            type_stats=sorted(type_stats, key=lambda x: x['total'], reverse=True),
            recent_transactions=list(get_transactions(limit=10))
        )

    @app.route('/api/transactions')
    def api_transactions():
        try:
            limit = min(int(request.args.get('limit', 10)), 100)
            transactions = list(get_transactions(limit=limit))
            return jsonify({
                'status': 'success',
                'data': transactions,
                'count': len(transactions)
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/api/stats')
    def api_stats():
        try:
            stats = get_summary_stats()
            return jsonify({
                'status': 'success',
                'data': {
                    'total': stats['total_transactions'],
                    'by_type': list(stats['by_type']),
                    'monthly': list(stats['monthly'])
                }
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app
