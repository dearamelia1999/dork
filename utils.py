import re
import urllib.parse
from typing import List, Dict, Optional

def validate_url(url: str) -> bool:
    """Validate if the provided URL is properly formatted."""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def clean_url(url: str) -> str:
    """Clean and format URL for dorking."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')

def extract_domain(url: str) -> str:
    """Extract domain from URL for site: operator."""
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return url

def parse_search_results(html_content: str, search_engine: str) -> List[Dict[str, str]]:
    """Parse search results from HTML content."""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    try:
        if search_engine == "google":
            # Google search result selectors
            result_divs = soup.find_all('div', class_='g')
            for div in result_divs[:20]:
                title_elem = div.find('h3')
                link_elem = div.find('a')
                snippet_elem = div.find('span', class_='aCOpRe') or div.find('div', class_='VwiC3b')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if link.startswith('/url?q='):
                        link = urllib.parse.unquote(link.split('/url?q=')[1].split('&')[0])
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "duckduckgo":
            # DuckDuckGo result selectors
            result_divs = soup.find_all('div', class_='result')
            for div in result_divs[:20]:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "yandex":
            # Yandex result selectors
            result_divs = soup.find_all('div', class_='organic')
            for div in result_divs[:20]:
                title_elem = div.find('h2').find('a') if div.find('h2') else None
                snippet_elem = div.find('div', class_='text-container')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "bing":
            # Bing result selectors
            result_divs = soup.find_all('li', class_='b_algo')
            for div in result_divs[:20]:
                title_elem = div.find('h2').find('a') if div.find('h2') else None
                snippet_elem = div.find('p') or div.find('div', class_='b_caption')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "baidu":
            # Baidu result selectors
            result_divs = soup.find_all('div', class_='result')
            for div in result_divs[:20]:
                title_elem = div.find('h3').find('a') if div.find('h3') else None
                snippet_elem = div.find('div', class_='c-abstract')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "yahoo":
            # Yahoo result selectors
            result_divs = soup.find_all('div', class_='Sr')
            for div in result_divs[:20]:
                title_elem = div.find('h3').find('a') if div.find('h3') else None
                snippet_elem = div.find('p', class_='fz-ms')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "startpage":
            # StartPage result selectors
            result_divs = soup.find_all('div', class_='w-gl__result')
            for div in result_divs[:20]:
                title_elem = div.find('h3').find('a') if div.find('h3') else None
                snippet_elem = div.find('p', class_='w-gl__description')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
        
        elif search_engine == "searx":
            # Searx result selectors
            result_divs = soup.find_all('div', class_='result')
            for div in result_divs[:20]:
                title_elem = div.find('h3').find('a') if div.find('h3') else None
                snippet_elem = div.find('p', class_='content')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
    
    except Exception as e:
        print(f"Error parsing results: {e}")
    
    return results

def format_results_for_display(results: List[Dict[str, str]]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"""
**{i}. {result['title']}**
🔗 {result['url']}
📝 {result['snippet'][:200]}{'...' if len(result['snippet']) > 200 else ''}
---
""")
    
    return "\n".join(formatted)
