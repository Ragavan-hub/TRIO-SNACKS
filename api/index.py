"""
Vercel serverless entry point for Flask application
"""
import sys
import os

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Change to parent directory for relative paths
os.chdir(parent_dir)

# Import app after setting up environment
from app import app

# Export the app for Vercel (WSGI application)
handler = app

