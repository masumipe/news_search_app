"""Seed script to populate the database with demo data."""
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.news_app.app import create_app
from src.news_app.extensions import db
from src.news_app.models.user import User
from src.news_app.models.article import Article
from src.news_app.models.report import Report
from src.news_app.models.preference import UserPreference


def seed():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        if User.query.first():
            print("Database already seeded. Skipping.")
            return

        users = [
            {"username": "admin", "email": "admin@newsai.com", "password": "admin123!", "role": "admin"},
            {"username": "analyst", "email": "analyst@newsai.com", "password": "analyst123!", "role": "analyst"},
            {"username": "alice", "email": "alice@example.com", "password": "password123", "role": "user"},
            {"username": "bob", "email": "bob@example.com", "password": "password123", "role": "user"},
        ]
        for u_data in users:
            user = User(username=u_data["username"], email=u_data["email"], role=u_data["role"])
            user.set_password(u_data["password"])
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users")

        import json
        preferences = [
            {"user_id": 3, "topics": "technology, AI, startups", "countries": "Bangladesh, India, United States", "sectors": "technology, finance", "sources": ["https://techcrunch.com", "https://www.thedailystar.net"]},
            {"user_id": 4, "topics": "energy, markets, inflation", "countries": "United Kingdom, Germany, global", "sectors": "energy, finance", "sources": ["https://www.bbc.com", "https://www.reuters.com"]},
        ]
        for p_data in preferences:
            pref = UserPreference(
                user_id=p_data["user_id"],
                preferred_topics=p_data["topics"],
                preferred_countries=p_data["countries"],
                preferred_sectors=p_data["sectors"],
                news_sources=json.dumps(p_data["sources"]),
            )
            db.session.add(pref)
        db.session.commit()
        print("Created user preferences")

        now = datetime.now(timezone.utc)
        articles = [
            {
                "source_name": "Tech Daily",
                "title": "AI Revolution: How Machine Learning is Transforming Industries",
                "description": "Artificial intelligence and machine learning continue to reshape industries from healthcare to finance, with new breakthroughs announced weekly.",
                "url": "https://example.com/ai-revolution",
                "published_at": now - timedelta(hours=2),
                "country": "global",
                "tags": "AI, machine learning, technology",
            },
            {
                "source_name": "Financial Times",
                "title": "Global Markets Rally on Interest Rate Optimism",
                "description": "Stock markets worldwide surged as central banks signal potential rate cuts, boosting investor confidence across sectors.",
                "url": "https://example.com/markets-rally",
                "published_at": now - timedelta(hours=5),
                "country": "global",
                "tags": "markets, finance, interest rates",
            },
            {
                "source_name": "Asia News Network",
                "title": "Bangladesh Banking Sector Shows Robust Growth",
                "description": "Bangladesh's banking sector reports 12% growth in deposits and improved asset quality, driven by digital transformation and regulatory reforms.",
                "url": "https://example.com/bangladesh-banking",
                "published_at": now - timedelta(hours=8),
                "country": "Bangladesh",
                "tags": "Bangladesh, banking, finance",
            },
            {
                "source_name": "Euro Wire",
                "title": "European Green Energy Transition Accelerates",
                "description": "EU member states commit to ambitious renewable energy targets, with solar and wind capacity expected to double by 2027.",
                "url": "https://example.com/europe-green-energy",
                "published_at": now - timedelta(days=1),
                "country": "Germany",
                "tags": "energy, green, Europe",
            },
            {
                "source_name": "Tech Crunch",
                "title": "Startup Funding Rebounds in Q2 2024",
                "description": "Venture capital funding shows signs of recovery with $45 billion invested globally in Q2, led by AI and climate tech startups.",
                "url": "https://example.com/startup-funding",
                "published_at": now - timedelta(days=1),
                "country": "United States",
                "tags": "startups, funding, venture capital",
            },
            {
                "source_name": "Reuters",
                "title": "Oil Prices Volatile Amid Geopolitical Tensions",
                "description": "Crude oil prices swing as geopolitical developments in the Middle East and production decisions by OPEC+ create market uncertainty.",
                "url": "https://example.com/oil-volatility",
                "published_at": now - timedelta(days=2),
                "country": "Saudi Arabia",
                "tags": "energy, oil, geopolitics",
            },
            {
                "source_name": "Bloomberg",
                "title": "Supply Chain Resilience Becomes Top Priority for Global CEOs",
                "description": "A survey of Fortune 500 CEOs reveals supply chain diversification and digitalization are the top strategic priorities for 2024.",
                "url": "https://example.com/supply-chain-ceo",
                "published_at": now - timedelta(days=2),
                "country": "global",
                "tags": "supply chain, business, strategy",
            },
            {
                "source_name": "Africa Report",
                "title": "African Continental Free Trade Area Gains Momentum",
                "description": "Trade under the AfCFTA framework increases 40% year-on-year as more countries implement tariff reduction schedules.",
                "url": "https://example.com/afcfta-growth",
                "published_at": now - timedelta(days=3),
                "country": "Nigeria",
                "tags": "Africa, trade, economy",
            },
        ]
        for a_data in articles:
            article = Article(
                source_name=a_data["source_name"],
                title=a_data["title"],
                description=a_data["description"],
                url=a_data["url"],
                published_at=a_data["published_at"],
                country=a_data["country"],
                tags=a_data["tags"],
            )
            db.session.add(article)
        db.session.commit()
        print(f"Created {len(articles)} articles")

        reports = [
            {
                "user_id": 1,
                "title": "Market Overview: Global Economic Trends Q2 2024",
                "report_type": "market_overview",
                "status": "completed",
                "summary": "Analysis of global economic indicators including GDP growth, inflation trends, and monetary policy outlook across major economies.",
                "article_ids": "1,2,3",
            },
            {
                "user_id": 2,
                "title": "Sector Analysis: Technology & AI Investment Landscape",
                "report_type": "financial_analysis",
                "status": "completed",
                "summary": "Deep dive into AI sector investment trends, key players, and risk assessment for technology portfolio positioning.",
                "article_ids": "1,5",
            },
        ]
        for r_data in reports:
            report = Report(
                user_id=r_data["user_id"],
                title=r_data["title"],
                report_type=r_data["report_type"],
                status=r_data["status"],
                summary=r_data["summary"],
                article_ids=r_data["article_ids"],
            )
            db.session.add(report)
        db.session.commit()
        print(f"Created {len(reports)} reports")

        print("\nSeed complete! Demo credentials:")
        print("  admin  / admin123!   (admin)")
        print("  analyst / analyst123! (analyst)")
        print("  alice  / password123  (user)")
        print("  bob    / password123  (user)")


if __name__ == "__main__":
    seed()
