def test_search_page(client, auth_headers):
    resp = client.get("/news/search")
    assert resp.status_code == 200


def test_search_with_query(client, auth_headers, db):
    from src.news_app.models.article import Article
    article = Article(
        source_name="Test",
        title="Technology Advances in 2024",
        description="New tech developments",
        url="https://example.com/tech",
        country="global",
        tags="technology",
    )
    db.session.add(article)
    db.session.commit()

    resp = client.get("/news/search?q=technology")
    assert resp.status_code == 200
    assert b"Technology" in resp.data


def test_article_view(client, auth_headers, sample_article):
    resp = client.get(f"/news/article/{sample_article.id}")
    assert resp.status_code == 200
    assert sample_article.title.encode() in resp.data


def test_add_to_reading_list(client, auth_headers, sample_article):
    resp = client.post(
        f"/news/reading-list/add/{sample_article.id}",
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_reading_list_page(client, auth_headers):
    resp = client.get("/news/reading-list")
    assert resp.status_code == 200


def test_record_interaction(client, auth_headers, sample_article):
    resp = client.post(
        f"/news/interaction/{sample_article.id}",
        data={"type": "like"},
    )
    assert resp.status_code == 200


def test_api_search(client, auth_headers):
    resp = client.get("/api/news/search?q=test")
    assert resp.status_code == 200
    assert resp.is_json


def test_api_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json["status"] == "healthy"
