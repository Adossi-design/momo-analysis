from flask import Flask, jsonify, request, render_template
from backend.database import get_transaction_count, get_transactions, get_summary_stats
import logging
from pathlib import Path
from datetime import datetime

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__,
               template_folder=str(Path(__file__).parent.parent/'frontend'/'templates'),
               static_folder=str(Path(__file__).parent.parent/'frontend'/'static'))

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Add custom filter for number formatting
    @app.template_filter('thousands')
    def format_thousands(value):
        return "{:,.0f}".format(value)
    
    @app.route('/')
    def dashboard():
        """Main dashboard with server-side rendering"""
        stats = get_summary_stats()
        
        # Get current month data with proper defaults
        current_month = datetime.now().strftime('%Y-%m')
        current_month_data = {
            'total': 0,
            'count': 0
        }
        
        # Find matching month or use defaults
        for month in stats['monthly']:
            if month['month'] == current_month:
                current_month_data = {
                    'total': float(month['total']),
                    'count': int(month['count'])
                }
                break
                
        return render_template(
            'dashboard.html',
            total_transactions=stats['total_transactions'],
            current_month=current_month_data,
            monthly_stats=stats['monthly'],
            type_stats=sorted(stats['by_type'], key=lambda x: x['total'], reverse=True),
            recent_transactions=get_transactions(limit=10)
        )

    @app.route('/api/transactions')
    def api_transactions():
        """API endpoint for transactions"""
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
        """API endpoint for statistics"""
        try:
            return jsonify({
                'status': 'success',
                'data': get_summary_stats()
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app
