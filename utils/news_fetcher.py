import os
import re
from urllib.parse import quote_plus

import requests
import xml.etree.ElementTree as ET

NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
NEWSAPI_URL = 'https://newsapi.org/v2/everything'
GOOGLE_NEWS_RSS_URL = 'https://news.google.com/rss/search'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'


def _build_query(topic, region=None, priority_region=None):
    parts = []
    if topic:
        parts.append(topic)
    if priority_region and priority_region.strip().lower() != (region or '').strip().lower():
        parts.append(priority_region)
    if region:
        parts.append(region)
    return ' '.join(parts).strip()


def _search_newsapi(query, max_results):
    params = {
        'q': query,
        'pageSize': max_results,
        'language': 'en',
        'sortBy': 'relevancy',
    }

    headers = {'Authorization': NEWS_API_KEY}
    response = requests.get(NEWSAPI_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    articles = data.get('articles', [])
    results = []
    for article in articles[:max_results]:
        title = article.get('title') or query
        url = article.get('url')
        source_name = article.get('source', {}).get('name')
        if not url:
            continue
        results.append({
            'summary': title,
            'website': url,
            'source': source_name,
        })
    return results


def _parse_google_news_rss_link(description_html):
    match = re.search(r'href=["\']([^"\']+)["\']', description_html)
    return match.group(1) if match else None


def _search_google_news_rss(query, region=None, priority_region=None, max_results=10):
    region_code = 'BD' if any(
        str(value).strip().lower() == 'bangladesh'
        for value in (region, priority_region)
    ) else 'US'

    params = {
        'q': query,
        'hl': f'en-{region_code}',
        'gl': region_code,
        'ceid': f'{region_code}:en',
    }

    response = requests.get(GOOGLE_NEWS_RSS_URL, params=params, headers={'User-Agent': USER_AGENT}, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall('.//item')[:max_results]

    results = []
    for item in items:
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        description = (item.findtext('description') or '').strip()
        source_tag = item.find('source')
        source_name = source_tag.text.strip() if source_tag is not None and source_tag.text else None

        if not link and description:
            link = _parse_google_news_rss_link(description) or ''

        if not link:
            continue

        results.append({
            'summary': title or query,
            'website': link,
            'source': source_name,
        })

    return results


def fetch_news_results(topic, region=None, priority_region=None, max_results=10):
    query = _build_query(topic, region, priority_region)
    if not query:
        return []

    if NEWS_API_KEY:
        try:
            return _search_newsapi(query, max_results)
        except Exception as exc:
            print(f'NewsAPI lookup failed: {exc}')

    return _search_google_news_rss(query, region, priority_region, max_results)
