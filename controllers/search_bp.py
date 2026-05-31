from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models import NewsSearch, ReportGenerator
from utils.news_fetcher import fetch_news_results

# Create a blueprint for search
search_bp = Blueprint('search', __name__)

news_api="e624435db47745f78ac115b8e2ae92c0"
class SearchController:
    @staticmethod
    def search(topic, region, priority_region):
        """Search and save results to database."""
        results = []
        fetched_results = fetch_news_results(topic, region, priority_region, max_results=10)

        for item in fetched_results:
            summary = item.get('summary') or f"News about {topic} in {region}"
            website = item.get('website')
            results.append(NewsSearch(None, topic, region, summary, website))

        for result in results:
            result.id = result.save()

        return results


class ReportController:
    @staticmethod
    def generate_report(topic, region):
        report = ReportGenerator.generate_report(topic, region)
        report_id = report.save()  # Save report to database
        return report_id


class SettingsController:
    @staticmethod
    def get_settings():
        return {
            'host': 'ollama-host',
            'port': '11434',
            'model': 'ols-ml-model'
        }

@search_bp.route('/', methods=['GET', 'POST'])
def search():
    """Search news articles"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        region = request.form.get('region')
        priority_region = request.form.get('priority_region')
        
        # Use controller to handle search
        results = SearchController.search(topic, region, priority_region)
        
        return render_template('search_results.html', results=results)
    
    return render_template('search.html')


@search_bp.route('/<int:search_id>')
def view_search_result(search_id):
    """View individual search result by ID."""
    result = NewsSearch.get_by_id(search_id)
    if result:
        return render_template('search_result.html', result=result)
    return 'Search result not found', 404
