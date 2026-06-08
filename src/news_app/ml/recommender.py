import logging
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..extensions import db
from ..models.article import Article
from ..models.preference import UserPreference, UserInteraction

logger = logging.getLogger(__name__)


class RecommenderService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self._article_vectors = None
        self._article_ids = []
        self._fitted = False

    def fit(self, articles: Optional[list] = None):
        if articles is None:
            try:
                articles = Article.query.order_by(Article.published_at.desc()).limit(1000).all()
            except Exception:
                articles = []

        if not articles:
            self._fitted = False
            return

        texts = []
        self._article_ids = []
        for a in articles:
            text = f"{a.title} {a.description or ''} {a.tags or ''} {a.country or ''}"
            texts.append(text)
            self._article_ids.append(a.id)

        self._article_vectors = self.vectorizer.fit_transform(texts)
        self._fitted = True
        logger.info("Fitted recommender with %d articles", len(articles))

    def recommend_for_user(
        self,
        user_id: int,
        limit: int = 10,
        exclude_ids: Optional[list] = None,
    ):
        if not self._fitted:
            self.fit()

        if not self._fitted:
            return []

        profile = self._build_user_profile(user_id)
        if profile is None:
            return self._get_fallback(limit, exclude_ids)

        profile_vector = self.vectorizer.transform([profile])
        if self._article_vectors is None:
            return []

        similarities = cosine_similarity(profile_vector, self._article_vectors).flatten()
        top_indices = similarities.argsort()[::-1]

        results = []
        seen = set(exclude_ids or [])
        for idx in top_indices:
            if len(results) >= limit:
                break
            article_id = self._article_ids[idx]
            if article_id in seen:
                continue
            seen.add(article_id)
            article = db.session.get(Article, article_id)
            if article:
                reasons = self._explain_recommendation(article, profile, user_id)
                results.append({
                    "article": article.to_dict(),
                    "score": float(similarities[idx]),
                    "reasons": reasons,
                })
        return results

    def _build_user_profile(self, user_id: int) -> Optional[str]:
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        topics = pref.get_topics() if pref else []
        countries = pref.get_countries() if pref else []

        interactions = (
            UserInteraction.query.filter_by(user_id=user_id)
            .order_by(UserInteraction.created_at.desc())
            .limit(50)
            .all()
        )

        liked_articles = []
        for interaction in interactions:
            if interaction.interaction_type in ("like", "click", "view"):
                article = db.session.get(Article, interaction.article_id)
                if article:
                    liked_articles.append(article)

        profile_parts = list(topics) + list(countries)
        for a in liked_articles:
            profile_parts.append(f"{a.title} {a.description or ''} {a.tags or ''}")

        if not profile_parts:
            return None

        return " ".join(profile_parts)

    def _explain_recommendation(self, article: Article, profile: str, user_id: int) -> list:
        reasons = []
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            return ["Recommended based on popular content"]

        user_topics = pref.get_topics()
        user_countries = pref.get_countries()

        article_text_lower = f"{article.title} {article.description or ''}".lower()

        for topic in user_topics:
            if topic.lower() in article_text_lower:
                reasons.append(f"Matches your interest in '{topic}'")
                break

        if article.country and user_countries and article.country in user_countries:
            reasons.append(f"From your preferred country: {article.country}")

        tags = article.tag_list()
        for tag in tags:
            if tag.lower() in [t.lower() for t in user_topics]:
                reasons.append(f"Tagged with '{tag}', one of your topics")

        has_likes = UserInteraction.query.filter_by(
            user_id=user_id,
            article_id=article.id,
            interaction_type="like",
        ).first()
        if has_likes:
            reasons.append("You have engaged with similar articles before")

        if not reasons:
            reasons.append("Trending in topics you follow")

        return reasons

    def _get_fallback(self, limit: int, exclude_ids: Optional[list] = None):
        query = Article.query.order_by(Article.published_at.desc())
        if exclude_ids:
            query = query.filter(Article.id.notin_(exclude_ids))
        articles = query.limit(limit).all()
        return [
            {
                "article": a.to_dict(),
                "score": 0.0,
                "reasons": ["Recent article"],
            }
            for a in articles
        ]

    def rank_search_results(self, user_id: int, articles: list) -> list:
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            return articles

        user_topics = [t.lower() for t in pref.get_topics()]
        user_countries = pref.get_countries()

        scored = []
        for article in articles:
            score = 0.0
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()

            for topic in user_topics:
                if topic in text:
                    score += 0.3

            if article.get("country") in user_countries:
                score += 0.4

            if article.get("source_name", "").lower() in [s.lower() for s in pref.get_sectors()]:
                score += 0.2

            scored.append((score, article))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in scored]

    def refresh_model(self):
        self.fit()
        logger.info("Recommendation model refreshed")
