from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import time
from typing import List, Dict, Optional

class NewsSourceVerifier:
    def __init__(self):
        self.trusted_sources = {
            'reuters.com': 0.9,
            'apnews.com': 0.9,
            'bbc.com': 0.85,
            'nytimes.com': 0.8,
            'theguardian.com': 0.8,
            'wsj.com': 0.8,
            'bloomberg.com': 0.85,
            'npr.org': 0.85,
            'economist.com': 0.85,
            'ft.com': 0.85,
            'wikipedia.org': 0.98,  
            'timesofindia.indiatimes.com': 0.75, 
            'thehindu.com': 0.75  ,
            'hindustantimes.com':0.8
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Rate limiting parameters
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds between requests

    def _wait_for_rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
            
        self.last_request_time = time.time()

    def get_article_content(self, url: str) -> Optional[Dict]:
        """Fetch and parse article content from URL"""
        try:
            self._wait_for_rate_limit()
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic content extraction - you might need to adjust selectors based on the source
            title = soup.find('h1').get_text() if soup.find('h1') else ''
            content = ''
            
            # Look for article content in common containers
            article_containers = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                term in str(x).lower() for term in ['article', 'content', 'story']))
            
            for container in article_containers:
                paragraphs = container.find_all('p')
                content += ' '.join(p.get_text().strip() for p in paragraphs)
            
            return {
                'title': title,
                'content': content,
                'url': url
            }
            
        except Exception as e:
            print(f"Error fetching article content from {url}: {e}")
            return None

    def search_related_articles(self, headline: str, max_results: int = 5) -> List[Dict]:
        """Search for related articles from trusted sources"""
        try:
            self._wait_for_rate_limit()
            search_query = quote(f"{headline} news")
            search_url = f"https://www.google.com/search?q={search_query}"
            
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = []
            
            for result in soup.find_all('div', class_='g'):
                try:
                    link_elem = result.find('a')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    if not url.startswith('http'):
                        continue
                    
                    # Check if URL is from trusted sources
                    source_domain = next((source for source in self.trusted_sources.keys() 
                                       if source in url), None)
                    if not source_domain:
                        continue
                    
                    title = result.find('h3').get_text() if result.find('h3') else ''
                    snippet = result.find('div', class_='VwiC3b').get_text() if result.find('div', class_='VwiC3b') else ''
                    
                    # Get article content
                    article_content = self.get_article_content(url)
                    
                    search_results.append({
                        'url': url,
                        'title': title,
                        'snippet': snippet,
                        'source': source_domain,
                        'credibility_score': self.trusted_sources[source_domain],
                        'content': article_content['content'] if article_content else None
                    })
                    
                    if len(search_results) >= max_results:
                        break
                    
                except Exception as e:
                    print(f"Error processing search result: {e}")
                    continue
            
            return search_results
            
        except Exception as e:
            print(f"Error searching for articles: {e}")
            return []

    def get_source_credibility(self, source_domain: str) -> float:
        """Get credibility score for a source"""
        return self.trusted_sources.get(source_domain, 0.0)

    def add_trusted_source(self, domain: str, credibility_score: float):
        """Add a new trusted source"""
        self.trusted_sources[domain] = max(0.0, min(1.0, credibility_score))

    def remove_trusted_source(self, domain: str):
        """Remove a trusted source"""
        self.trusted_sources.pop(domain, None)