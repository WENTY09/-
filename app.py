"""
Main application file for the Telegram delivery bot web interface
"""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db

# Configure logging
logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Configure secret key
    app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        _initialize_default_admin()

    # Register blueprints
    from dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app

def _initialize_default_admin():
    """Initialize default admin user if it doesn't exist."""
    from models import Admin
    from sqlalchemy.exc import SQLAlchemyError
    
    try:
        # Define default admin permissions
        default_permissions = {
            "block_users": True,
            "add_money": True,
            "remove_money": True,
            "give_items": True,
            "broadcast": True,
            "view_users": True,
            "manage_admins": True
        }
        
        # Check if admin already exists
        admin = Admin.query.filter_by(telegram_id="6999938953").first()
        if not admin:
            # Create default admin (white_wenty)
            admin = Admin(
                telegram_id="6999938953",
                name="@white_wenty",
                role="owner",
                permissions=default_permissions,
                added_by="system"
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin created.")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error initializing default admin: {e}")

# Create the app
app = create_app()