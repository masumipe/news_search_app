def test_login_page(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Sign In" in resp.data


def test_register_page(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200
    assert b"Create Account" in resp.data


def test_register_user(client, db):
    resp = client.post("/auth/register", data={
        "username": "newuser",
        "email": "new@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Registration successful" in resp.data


def test_register_duplicate_username(client, db):
    from src.news_app.models.user import User
    user = User(username="dupuser", email="dup1@example.com", role="user")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/auth/register", data={
        "username": "dupuser",
        "email": "dup2@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Username already taken" in resp.data


def test_login_success(client, db):
    from src.news_app.models.user import User
    user = User(username="logintest", email="login@example.com", role="user")
    user.set_password("correctpassword")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/auth/login", data={
        "username": "logintest",
        "password": "correctpassword",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data


def test_login_failure(client, db):
    resp = client.post("/auth/login", data={
        "username": "nonexistent",
        "password": "wrong",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data


def test_logout(client, auth_headers, db):
    resp = client.get("/auth/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Sign In" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Sign In" in resp.data
