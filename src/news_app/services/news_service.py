import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
import requests

from ..extensions import db
from ..models.article import Article

logger = logging.getLogger(__name__)


class NewsService:
    POPULAR_COUNTRIES = [
        "Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal",
        "United States", "Canada", "United Kingdom", "Germany", "France",
        "Australia", "Japan", "China", "South Korea", "Singapore",
        "Indonesia", "Malaysia", "Philippines", "Vietnam", "Thailand",
        "Brazil", "Argentina", "Nigeria", "Kenya", "South Africa",
        "Saudi Arabia", "UAE", "Qatar", "Turkey", "Russia",
    ]

    def __init__(self, config):
        self.api_key = config.get("NEWS_API_KEY", "")
        self.api_url = config.get("NEWS_API_URL", "https://newsapi.org/v2")
        self.timeout = config.get("NEWS_API_TIMEOUT", 30)

    def search(
        self,
        topic: str,
        country: str = "",
        domains: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sources: Optional[str] = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
        prioritize_country: bool = True,
        user_countries: Optional[list] = None,
    ):
        if self.api_key:
            try:
                return self._search_external(
                    topic, country, domains, date_from, date_to,
                    sources, language, page, page_size,
                )
            except Exception:
                pass
        return self._search_local(
            topic, country, page, page_size,
            prioritize_country, user_countries,
        )

    def _search_external(
        self, topic, country, domains, date_from, date_to,
        sources, language, page, page_size,
    ):
        params = {
            "q": topic,
            "language": language,
            "pageSize": min(page_size, 100),
            "page": page,
            "apiKey": self.api_key,
            "sortBy": "publishedAt",
        }
        if sources:
            params["sources"] = sources
        if domains:
            params["domains"] = domains

        if country:
            params["q"] = f"{topic} {country}"

        url = f"{self.api_url}/everything"
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("News API request failed: %s", str(e))
            return {"articles": [], "total_results": 0, "error": str(e)}

        articles = []
        for item in data.get("articles", []):
            article = self._normalize_article(item, country)
            stored = self._store_article(article)
            articles.append(stored.to_dict())

        return {
            "articles": articles,
            "total_results": data.get("totalResults", len(articles)),
            "page": page,
            "page_size": page_size,
        }

    def fetch_from_source_urls(self, topic: str, source_urls: list, country: str = ""):
        domains = self._extract_domains(source_urls)
        if not domains:
            return {"articles": [], "total_results": 0}

        domains_str = ",".join(domains)
        return self.search(
            topic=topic,
            country=country,
            domains=domains_str,
        )

    def _extract_domains(self, urls: list) -> list:
        domains = set()
        for url in urls:
            url = url.strip()
            if not url:
                continue
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            try:
                parsed = urlparse(url)
                hostname = parsed.hostname or ""
                hostname = re.sub(r"^www\.", "", hostname)
                if hostname:
                    domains.add(hostname)
            except Exception:
                pass
        return list(domains)

    def _search_local(
        self, topic, country, page, page_size,
        prioritize_country, user_countries,
    ):
        query = Article.query

        if topic:
            like_pattern = f"%{topic}%"
            query = query.filter(
                db.or_(
                    Article.title.ilike(like_pattern),
                    Article.description.ilike(like_pattern),
                    Article.content.ilike(like_pattern),
                    Article.tags.ilike(like_pattern),
                )
            )

        if country:
            query = query.filter(Article.country == country)

        total = query.count()

        if prioritize_country and user_countries:
            from sqlalchemy import case
            country_order = case(
                *[(Article.country == c, i) for i, c in enumerate(user_countries)],
                else_=len(user_countries),
            )
            query = query.order_by(country_order, Article.published_at.desc())
        else:
            query = query.order_by(Article.published_at.desc())

        articles = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "articles": [a.to_dict() for a in articles],
            "total_results": total,
            "page": page,
            "page_size": page_size,
        }

    def _normalize_article(self, item: dict, country: str):
        return {
            "source_id": item.get("source", {}).get("id", ""),
            "source_name": item.get("source", {}).get("name", ""),
            "author": item.get("author", ""),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "url_to_image": item.get("urlToImage", ""),
            "published_at": item.get("publishedAt", ""),
            "content": item.get("content", ""),
            "country": country or "global",
            "language": "en",
            "category": "",
            "tags": "",
        }

    def _store_article(self, article_data: dict):
        existing = Article.query.filter_by(url=article_data["url"]).first()
        if existing:
            return existing

        published = None
        if article_data.get("published_at"):
            try:
                published = datetime.fromisoformat(
                    article_data["published_at"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                published = datetime.now(timezone.utc)

        article = Article(
            source_id=article_data.get("source_id", ""),
            source_name=article_data.get("source_name", ""),
            author=article_data.get("author", ""),
            title=article_data.get("title", ""),
            description=article_data.get("description", ""),
            url=article_data["url"],
            url_to_image=article_data.get("url_to_image", ""),
            published_at=published,
            content=article_data.get("content", ""),
            country=article_data.get("country", "global"),
            language=article_data.get("language", "en"),
            category=article_data.get("category", ""),
            tags=article_data.get("tags", ""),
        )
        db.session.add(article)
        db.session.commit()
        return article

    def get_article_by_id(self, article_id: int):
        return db.session.get(Article, article_id)

    def get_reading_list(self, user_id: int):
        from ..models.article import ReadingListItem
        items = (
            ReadingListItem.query.filter_by(user_id=user_id)
            .order_by(ReadingListItem.added_at.desc())
            .all()
        )
        return items

    def add_to_reading_list(self, user_id: int, article_id: int, notes: str = ""):
        from ..models.article import ReadingListItem
        existing = ReadingListItem.query.filter_by(
            user_id=user_id, article_id=article_id
        ).first()
        if existing:
            return existing

        item = ReadingListItem(user_id=user_id, article_id=article_id, notes=notes)
        db.session.add(item)
        db.session.commit()
        return item

    def remove_from_reading_list(self, item_id: int):
        from ..models.article import ReadingListItem
        item = db.session.get(ReadingListItem, item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
