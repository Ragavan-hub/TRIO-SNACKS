"""
Configuration settings for the Snacks Shop application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Use environment variable for database or default to local file
    # For Vercel, use /tmp for writable database location
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/database.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Application settings
    # For Vercel, use /tmp for uploads (writable location)
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/static/images/products'
    else:
        UPLOAD_FOLDER = 'static/images/products'
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Default settings
    DEFAULT_TAX_RATE = 5.0  # 5%
    DEFAULT_GST_RATE = 0.0  # 0%
    DEFAULT_SHOP_NAME = "Trio Snacks"
    DEFAULT_STOCK_ALERT_THRESHOLD = 10

