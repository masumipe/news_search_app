import sqlite3
import os
from flask_login import UserMixin

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def init_db():
    """Ensure the database and required tables exist."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
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


def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    @classmethod
    def get_by_id(cls, user_id):
        # Simple in-memory storage
        if user_id == 1:
            return cls(1, 'admin', 'admin123')
        return None

class NewsSearch:
    def __init__(self, id, topic, region, summary, website):
        self.id = id
        self.topic = topic
        self.region = region
        self.summary = summary
        self.website = website
    
    @property
    def url(self):
        if isinstance(self.website, str) and self.website.startswith(('http://', 'https://')):
            return self.website
        return f'https://{self.website}' if self.website else ''
    
    @classmethod
    def get_by_id(cls, search_id):
        """Get a search result by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM search_results WHERE id = ?', (search_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(row['id'], row['topic'], row['region'], row['summary'], row['website'])
        return None
    
    @classmethod
    def get_all(cls):
        """Get all search results."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM search_results ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(row['id'], row['topic'], row['region'], row['summary'], row['website']) for row in rows]
    
    def save(self):
        """Save a search result to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO search_results (topic, region, summary, website) VALUES (?, ?, ?, ?)',
            (self.topic, self.region, self.summary, self.website)
        )
        conn.commit()
        search_id = cursor.lastrowid
        conn.close()
        self.id = search_id
        return search_id


class ReportGenerator:
    def __init__(self, id, topic, region, financial_analysis, images, tables):
        self.id = id
        self.topic = topic
        self.region = region
        self.financial_analysis = financial_analysis
        self.images = images
        self.tables = tables
    
    @classmethod
    def get_by_id(cls, report_id):
        """Get a report by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(row['id'], row['topic'], row['region'], row['financial_analysis'], row['images'], row['tables'])
        return None
    
    @classmethod
    def get_all(cls):
        """Get all reports."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(row['id'], row['topic'], row['region'], row['financial_analysis'], row['images'], row['tables']) for row in rows]
    
    def save(self):
        """Save a report to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reports (topic, region, financial_analysis, images, tables) VALUES (?, ?, ?, ?, ?)',
            (self.topic, self.region, self.financial_analysis, self.images, self.tables)
        )
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id
    
    @classmethod
    def get_report(cls, report_id):
        """Get a report by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(row['id'], row['topic'], row['region'], row['financial_analysis'], row['images'], row['tables'])
        return None


# Ensure the database is created and tables exist when models are imported.
init_db()
