from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models import NewsSearch, ReportGenerator
from utils.news_fetcher import fetch_news_results
from utils.ollama_service import OllamaService

# Create a blueprint for search
search_bp = Blueprint('search', __name__)

news_api="e624435db47745f78ac115b8e2ae92c0"
class SearchController:
    @staticmethod
    def search(topic, region, priority_region, max_results=100):
        """Search and save results to database."""
        results = []
        fetched_results = fetch_news_results(topic, max_results=max_results)

        for item in fetched_results:
            summary = item.get('summary') or f"News about {topic}"
            website = item.get('website')
            results.append(NewsSearch(None, topic, '', summary, website))

        for result in results:
            result.id = result.save()

        return results


class ReportController:
    @staticmethod
    def generate_report(topic, region):
        report = ReportGenerator(
            None,
            topic,
            region,
            financial_analysis=f"Financial analysis for {topic} in {region}",
            images="image1.png,image2.png",
            tables="table1.csv,table2.csv"
        )
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

@search_bp.route('/search', methods=['GET', 'POST'], strict_slashes=False)
def search():
    """Search news articles with pagination"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        
        # Use controller to handle search (get more results for pagination)
        results = SearchController.search(topic, max_results=100)
        
        # Initialize Ollama service
        ollama = OllamaService()
        use_ollama = ollama.is_available()
        
        # Generate summaries for each result if Ollama is available
        for result in results:
            if use_ollama:
                result.ollama_summary = ollama.get_summary(result.summary, max_length=200)
            else:
                result.ollama_summary = result.summary[:200]
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        items_per_page = 10
        
        # Calculate pagination
        total_items = len(results)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        result_start = start_idx + 1
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        paginated_results = results[start_idx:end_idx]
        
        return render_template(
            'search_results.html',
            results=paginated_results,
            page=page,
            total_pages=total_pages,
            total_items=total_items,
            result_start=result_start,
            result_end=end_idx,
            items_per_page=items_per_page,
            start_page=start_page,
            end_page=end_page,
            topic=topic
        )
    else:                       
        return render_template('search.html')


@search_bp.route('/search/page/<int:page>', methods=['GET'], strict_slashes=False)
def search_page(page):
    """Handle pagination for search results"""
    topic = request.args.get('topic', '')
    
    if not topic:
        return redirect(url_for('search.search'))
    
    # Use controller to handle search
    results = SearchController.search(topic, max_results=100)
    
    # Initialize Ollama service
    ollama = OllamaService()
    use_ollama = ollama.is_available()
    
    # Generate summaries for each result if Ollama is available
    for result in results:
        if use_ollama:
            result.ollama_summary = ollama.get_summary(result.summary, max_length=200)
        else:
            result.ollama_summary = result.summary[:200]
    
    # Get pagination parameters
    items_per_page = 10
    
    # Calculate pagination
    total_items = len(results)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    result_start = start_idx + 1
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    paginated_results = results[start_idx:end_idx]
    
    return render_template(
        'search_results.html',
        results=paginated_results,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        result_start=result_start,
        result_end=end_idx,
        items_per_page=items_per_page,
        start_page=start_page,
        end_page=end_page,
        topic=topic
    )
