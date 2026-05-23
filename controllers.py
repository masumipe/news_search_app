from models import NewsSearch, ReportGenerator
from flask import Blueprint

search_bp = Blueprint('search', __name__)
report_bp = Blueprint('report', __name__)
settings_bp = Blueprint('settings', __name__)

class SearchController:
    @staticmethod
    def search(topic, region, priority_region):
        # Simulated search results
        results = [
            NewsSearch(1, topic, region, f"News about {topic} in {region}", "news1.com"),
            NewsSearch(2, topic, region, f"Breaking news on {topic}", "news2.com"),
            NewsSearch(3, topic, region, f"Analysis of {topic}", "news3.com"),
            NewsSearch(4, topic, region, f"Latest updates on {topic}", "news4.com"),
            NewsSearch(5, topic, region, f"Expert opinion on {topic}", "news5.com"),
            NewsSearch(6, topic, region, f"Market impact of {topic}", "news6.com"),
            NewsSearch(7, topic, region, f"Economic implications of {topic}", "news7.com"),
            NewsSearch(8, topic, region, f"Industry trends in {topic}", "news8.com"),
            NewsSearch(9, topic, region, f"Global perspective on {topic}", "news9.com"),
            NewsSearch(10, topic, region, f"Future outlook for {topic}", "news10.com"),
        ]
        return results

class ReportController:
    @staticmethod
    def generate_report(topic, region):
        report = ReportGenerator(
            id=1,
            topic=topic,
            region=region,
            financial_analysis=f"Financial analysis for {topic} in {region}",
            images=["image1.png", "image2.png"],
            tables=["table1.csv", "table2.csv"]
        )
        return report

class SettingsController:
    @staticmethod
    def get_settings():
        return {
            'host': 'ollama-host',
            'port': '11434',
            'model': 'ols-ml-model'
        }
