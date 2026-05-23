class AuthManager:
    def __init__(self, app):
        self.app = app

    def authenticate(self, username, password):
        if username == 'admin' and password == 'admin123':
            from models import User
            return User(1, 'admin', 'admin123')
        return None
