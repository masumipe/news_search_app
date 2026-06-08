import logging
from typing import Optional

from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, ollama: OllamaClient):
        self.ollama = ollama

    def analyze_article(self, article: dict):
        text = f"{article.get('title', '')}\n\n{article.get('description', '')}\n\n{article.get('content', '')}"
        sentiment = self.ollama.analyze_sentiment(text)
        risks = self.ollama.extract_risks(text)
        summary = self.ollama.summarize_article(
            article.get("title", ""), text
        )
        return {
            "sentiment": sentiment,
            "risks": risks,
            "summary": summary,
        }

    def aggregate_sentiment(self, articles: list):
        sentiments = []
        for a in articles:
            try:
                result = self.ollama.analyze_sentiment(
                    f"{a.get('title', '')}\n\n{a.get('description', '')}"
                )
                sentiments.append({
                    "title": a.get("title", ""),
                    "sentiment": result.get("sentiment", "neutral"),
                    "score": result.get("score", 0.5),
                })
            except Exception as e:
                logger.warning("Sentiment analysis failed for article: %s", str(e))

        if not sentiments:
            return {"aggregate": "neutral", "articles": []}

        avg_score = sum(s["score"] for s in sentiments) / len(sentiments)
        if avg_score > 0.6:
            aggregate = "positive"
        elif avg_score < 0.4:
            aggregate = "negative"
        else:
            aggregate = "neutral"

        return {
            "aggregate": aggregate,
            "average_score": round(avg_score, 3),
            "articles": sentiments,
        }

    def detect_trends(self, articles: list):
        regions = {}
        sectors = {}
        sentiments_over_time = []

        for a in articles:
            region = a.get("region", "unknown")
            regions[region] = regions.get(region, 0) + 1

            for tag in a.get("tags", []):
                sectors[tag] = sectors.get(tag, 0) + 1

            pub = a.get("published_at", "")
            if pub:
                sentiments_over_time.append({
                    "date": pub[:10],
                    "sentiment": "neutral",
                })

        return {
            "region_breakdown": regions,
            "sector_breakdown": sectors,
            "total_articles": len(articles),
        }
