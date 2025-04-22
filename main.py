import os
import logging
import threading
import time
import psutil
from flask import render_template, jsonify
from app import app
from models import db, User, Buff, Admin
from telegram_bot.bot import run_telegram_bot

# Set up logging with a simple format
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define routes
@app.route('/')
def index():
    """Render the main dashboard page."""
    # Check if bot token is configured
    bot_configured = bool(os.environ.get("TELEGRAM_BOT_TOKEN"))
    
    return render_template('index.html', bot_configured=bot_configured)

@app.route('/stats')
def stats_page():
    """Render the detailed statistics page."""
    return render_template('stats.html')

@app.route('/api/stats')
def api_stats():
    """API endpoint for getting real-time stats."""
    try:
        # Get database stats
        total_users = User.query.count()
        total_deliveries = db.session.query(db.func.sum(User.deliveries)).scalar() or 0
        total_money = db.session.query(db.func.sum(User.money)).scalar() or 0
        active_buffs = Buff.query.filter(Buff.expires_at > time.time()).count()
        
        # Get top users from database
        top_users_db = User.query.order_by(User.deliveries.desc()).limit(10).all()
        top_users = []
        for user in top_users_db:
            top_users.append({
                "user_id": user.telegram_id,
                "username": user.username,
                "deliveries": user.deliveries
            })
        
        # Get system stats
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Format results
        stats = {
            "system": {
                "cpu": cpu_percent,
                "memory": memory_percent,
                "disk": disk_percent,
                "uptime": int(time.time() - psutil.boot_time())
            },
            "bot": {
                "total_users": total_users,
                "total_deliveries": total_deliveries,
                "total_earnings": total_money,
                "active_buffs": active_buffs
            },
            "top_users": top_users,
            "bot_status": bool(os.environ.get("TELEGRAM_BOT_TOKEN"))
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        # Fallback stats if there's an error
        stats = {
            "system": {
                "cpu": 0,
                "memory": 0,
                "disk": 0,
                "uptime": 0
            },
            "bot": {
                "total_users": 0,
                "total_deliveries": 0,
                "total_earnings": 0,
                "active_buffs": 0
            },
            "top_users": [],
            "bot_status": bool(os.environ.get("TELEGRAM_BOT_TOKEN"))
        }
    
    return jsonify(stats)

# Start Telegram bot in a background thread when run directly
if __name__ == '__main__':
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True  # Thread will exit when main program exits
    bot_thread.start()
    
    logger.info("Starting Flask dashboard...")
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Start bot thread when loaded by gunicorn
    logger.info("Starting Telegram bot thread for gunicorn...")
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
