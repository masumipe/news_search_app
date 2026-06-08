import pytest
from src.news_app.app import create_app
from src.news_app.extensions import db as _db
from src.news_app.models.user import User


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client, db):
    user = User(username="testuser", email="test@example.com", role="user")
    user.set_password("testpassword123")
    db.session.add(user)
    db.session.commit()

    with client:
        resp = client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword123",
        }, follow_redirects=True)
        assert resp.status_code == 200

    return {}


@pytest.fixture
def sample_article(db):
    from src.news_app.models.article import Article
    article = Article(
        source_name="Test Source",
        title="Test Article Title for Testing",
        description="This is a test article description for testing purposes.",
        url="https://example.com/test-article",
        country="global",
        tags="test, sample",
    )
    db.session.add(article)
    db.session.commit()
    return article
