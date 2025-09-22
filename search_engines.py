import requests
import time
import random
from typing import Dict, List, Optional
from utils import build_dork_query, parse_search_results

class BaseSearchEngine:
    """Base class for search engines."""
    
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if proxy:
            self.session.proxies.update({
                'http': proxy,
                'https': proxy
            })
    
    def search(self, query: str) -> List[Dict[str, str]]:
        """Perform search - to be implemented by subclasses."""
        raise NotImplementedError

class GoogleDorker(BaseSearchEngine):
    """Google search engine dorker."""
    
    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)
        self.base_url = "https://www.google.com/search"
    
    def search(self, site: str, query: str = "", additional_operators: str = "") -> List[Dict[str, str]]:
        """Perform Google dork search."""
        dork_query = build_dork_query(site, query, additional_operators)
        
        params = {
            'q': dork_query,
            'num': 20,
            'hl': 'en'
        }
        
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return parse_search_results(response.text, "google")
            else:
                return []
                
        except Exception as e:
            print(f"Google search error: {e}")
            return []

class DuckDuckGoDorker(BaseSearchEngine):
    """DuckDuckGo search engine dorker."""
    
    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)
        self.base_url = "https://html.duckduckgo.com/html/"
    
    def search(self, site: str, query: str = "", additional_operators: str = "") -> List[Dict[str, str]]:
        """Perform DuckDuckGo dork search."""
        dork_query = build_dork_query(site, query, additional_operators)
        
        params = {
            'q': dork_query
        }
        
        try:
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return parse_search_results(response.text, "duckduckgo")
            else:
                return []
                
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []

class YandexDorker(BaseSearchEngine):
    """Yandex search engine dorker."""
    
    def __init__(self, proxy: Optional[str] = None):
        super().__init__(proxy)
        self.base_url = "https://yandex.com/search/"
    
    def search(self, site: str, query: str = "", additional_operators: str = "") -> List[Dict[str, str]]:
        """Perform Yandex dork search."""
        dork_query = build_dork_query(site, query, additional_operators)
        
        params = {
            'text': dork_query,
            'lr': 21
        }
        
        try:
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return parse_search_results(response.text, "yandex")
            else:
                return []
                
        except Exception as e:
            print(f"Yandex search error: {e}")
            return []

class SearchEngineManager:
    """Manager class to handle multiple search engines."""
    
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.engines = {
            'Google': GoogleDorker(proxy),
            'DuckDuckGo': DuckDuckGoDorker(proxy),
            'Yandex': YandexDorker(proxy)
        }
    
    def get_engine(self, engine_name: str) -> BaseSearchEngine:
        """Get search engine instance by name."""
        return self.engines.get(engine_name)
    
    def search_all_engines(self, site: str, query: str = "", additional_operators: str = "") -> Dict[str, List[Dict[str, str]]]:
        """Search across all available engines."""
        results = {}
        
        for engine_name, engine in self.engines.items():
            try:
                results[engine_name] = engine.search(site, query, additional_operators)
            except Exception as e:
                print(f"Error with {engine_name}: {e}")
                results[engine_name] = []
        
        return results