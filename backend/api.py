from datetime import datetime

@app.route('/')
def dashboard():
    """Main dashboard with enhanced analytics"""
    stats = get_summary_stats()
    
    # Get current month data
    current_month = datetime.now().strftime('%Y-%m')
    current_month_data = next(
        (m for m in stats['monthly'] if m['month'] == current_month),
        {'total': 0, 'count': 0}
    )
    
    # Get recent transactions
    recent_transactions = get_transactions(limit=10)
    
    # Prepare type statistics
    type_stats = sorted(
        stats['by_type'],
        key=lambda x: x['total'],
        reverse=True
    )
    
    return render_template(
        'dashboard.html',
        total_transactions=stats['total_transactions'],
        current_month=current_month_data,
        monthly_stats=stats['monthly'],
        type_stats=type_stats,
        recent_transactions=recent_transactions
    )
