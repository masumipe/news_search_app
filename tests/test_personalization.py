def test_recommender_init(app):
    from src.news_app.ml.recommender import RecommenderService
    recommender = RecommenderService()
    assert recommender is not None


def test_recommender_fit(app, db):
    from src.news_app.ml.recommender import RecommenderService
    from src.news_app.models.article import Article

    articles = [
            Article(
                title=f"Article {i} about technology",
                description=f"Technology news article {i}",
                url=f"https://example.com/tech-{i}",
                tags="technology",
                country="global",
            )
        for i in range(5)
    ]
    for a in articles:
        db.session.add(a)
    db.session.commit()

    recommender = RecommenderService()
    recommender.fit()
    assert recommender._fitted


def test_recommender_empty(app):
    from src.news_app.ml.recommender import RecommenderService
    recommender = RecommenderService()
    recommender.fit([])
    results = recommender.recommend_for_user(user_id=1, limit=5)
    assert results == []


def test_recommender_with_preferences(app, db):
    from src.news_app.ml.recommender import RecommenderService
    from src.news_app.models.article import Article
    from src.news_app.models.user import User
    from src.news_app.models.preference import UserPreference

    user = User(username="recuser", email="rec@example.com", role="user")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    pref = UserPreference(user_id=user.id, preferred_topics="technology")
    db.session.add(pref)

    articles = [
            Article(
                title=f"Tech Article {i}",
                description=f"Technology related content {i}",
                url=f"https://example.com/t{i}",
                tags="technology",
                country="global",
            )
        for i in range(3)
    ]
    for a in articles:
        db.session.add(a)
    db.session.commit()

    recommender = RecommenderService()
    recommender.fit()
    results = recommender.recommend_for_user(user.id, limit=5)
    assert len(results) <= 3
