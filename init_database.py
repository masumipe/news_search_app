"""
Database initialization script for News Search Application
This script creates the required database tables if they don't exist.
"""

import sqlite3
import os
from pathlib import Path

# Get the application directory
APP_DIR = Path(__file__).parent.parent
DATABASE_PATH = APP_DIR / 'database.db'


def init_database():
    """Initialize the database with required tables."""
    print(f"Initializing database at: {DATABASE_PATH}")
    
    # Remove existing database to start fresh
    if DATABASE_PATH.exists():
        print(f"Removing existing database: {DATABASE_PATH}")
        DATABASE_PATH.unlink()
    
    # Create new database connection
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    # Create search_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            region TEXT NOT NULL,
            summary TEXT NOT NULL,
            website TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            region TEXT NOT NULL,
            financial_analysis TEXT NOT NULL,
            images TEXT NOT NULL,
            tables TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    print(f"Tables created: search_results, reports")
    return True


if __name__ == '__main__':
    init_database()
