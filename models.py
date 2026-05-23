from flask_login import UserMixin

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

class ReportGenerator:
    def __init__(self, id, topic, region, financial_analysis, images, tables):
        self.id = id
        self.topic = topic
        self.region = region
        self.financial_analysis = financial_analysis
        self.images = images
        self.tables = tables
