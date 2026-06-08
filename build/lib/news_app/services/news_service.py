import logging
from datetime import datetime, timezone
from typing import Optional
import requests

from ..extensions import db
from ..models.article import Article

logger = logging.getLogger(__name__)


class NewsService:
    REGIONS = {
        "global": "Global",
        "asia": "Asia",
        "europe": "Europe",
        "north_america": "North America",
        "south_america": "South America",
        "africa": "Africa",
        "oceania": "Oceania",
        "middle_east": "Middle East",
    }

    PRIORITY_REGIONS = {
        "south_asia": ["Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal"],
        "se_asia": ["Indonesia", "Malaysia", "Philippines", "Singapore", "Thailand", "Vietnam"],
        "east_asia": ["China", "Japan", "South Korea", "Taiwan"],
    }

    def __init__(self, config):
        self.api_key = config.get("NEWS_API_KEY", "")
        self.api_url = config.get("NEWS_API_URL", "https://newsapi.org/v2")
        self.timeout = config.get("NEWS_API_TIMEOUT", 30)

    def search(
        self,
        topic: str,
        region: str = "global",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sources: Optional[str] = None,
        language: str = "en",
        page: int = 1,
        page_size: int = 20,
        prioritize_region: bool = True,
        user_regions: Optional[list] = None,
    ):
        if self.api_key:
            try:
                return self._search_external(
                    topic, region, date_from, date_to, sources, language, page, page_size
                )
            except Exception:
                pass
        return self._search_local(
            topic, region, page, page_size, prioritize_region, user_regions
        )

    def _search_external(self, topic, region, date_from, date_to, sources, language, page, page_size):
        params = {
            "q": topic,
            "language": language,
            "pageSize": min(page_size, 100),
            "page": page,
            "apiKey": self.api_key,
        }
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        if sources:
            params["sources"] = sources

        if region and region != "global":
            region_keywords = {
                "asia": "Asia",
                "europe": "Europe OR EU OR UK OR Germany OR France",
                "north_america": "USA OR Canada OR Mexico OR 'North America'",
                "south_america": "Brazil OR Argentina OR 'South America'",
                "africa": "Africa OR Nigeria OR Kenya OR 'South Africa'",
                "middle_east": "'Middle East' OR UAE OR Saudi OR Israel OR Qatar",
                "oceania": "Australia OR 'New Zealand' OR Oceania",
            }
            if region in region_keywords:
                params["q"] = f"({topic}) AND ({region_keywords[region]})"

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
            article = self._normalize_article(item, region)
            articles.append(article)
            self._store_article(article)

        return {
            "articles": articles,
            "total_results": data.get("totalResults", len(articles)),
            "page": page,
            "page_size": page_size,
        }

    def _search_local(
        self, topic, region, page, page_size, prioritize_region, user_regions
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

        if region and region != "global":
            query = query.filter(Article.region == region)

        total = query.count()

        if prioritize_region and user_regions:
            from sqlalchemy import case
            region_order = case(
                *[(Article.region == r, i) for i, r in enumerate(user_regions)],
                else_=len(user_regions),
            )
            query = query.order_by(region_order, Article.published_at.desc())
        else:
            query = query.order_by(Article.published_at.desc())

        articles = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "articles": [a.to_dict() for a in articles],
            "total_results": total,
            "page": page,
            "page_size": page_size,
        }

    def _normalize_article(self, item: dict, region: str):
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
            "region": region or "global",
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
            region=article_data.get("region", "global"),
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
