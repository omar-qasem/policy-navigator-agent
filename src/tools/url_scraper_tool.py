"""
URL Scraper Tool for Policy Navigator Agent
Extracts content from government and regulatory websites
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import re
from urllib.parse import urljoin, urlparse


class URLScraperTool:
    """Tool to scrape and extract content from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (PolicyNavigatorAgent/1.0)'
        })
        self.timeout = 30
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            title = self._extract_title(soup)
            content = self._extract_content(soup)
            links = self._extract_links(soup, url)
            
            # Determine if this is a government site
            is_gov = self._is_government_site(url)
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'links': links,
                'is_government': is_gov,
                'status': 'success',
                'word_count': len(content.split())
            }
            
        except Exception as e:
            return {
                'url': url,
                'title': '',
                'content': '',
                'links': [],
                'is_government': False,
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try title tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "No title"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Common content containers
        for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from page"""
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().strip()
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Only include http/https links
            if absolute_url.startswith(('http://', 'https://')):
                links.append({
                    'url': absolute_url,
                    'text': text
                })
        
        return links[:50]  # Limit to first 50 links
    
    def _is_government_site(self, url: str) -> bool:
        """Check if URL is from a government domain"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        gov_domains = ['.gov', '.mil', '.us']
        return any(domain.endswith(d) for d in gov_domains)
    
    def scrape_epa_regulation(self, regulation_url: str) -> Dict[str, Any]:
        """
        Specialized scraper for EPA regulation pages
        
        Args:
            regulation_url: URL of EPA regulation page
            
        Returns:
            Extracted regulation data
        """
        result = self.scrape_url(regulation_url)
        
        if result['status'] == 'success':
            # Additional EPA-specific processing
            result['agency'] = 'EPA'
            result['source_type'] = 'regulation_page'
        
        return result
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scraping results
        """
        results = []
        
        for url in urls:
            print(f"Scraping: {url}")
            result = self.scrape_url(url)
            results.append(result)
        
        return results
    
    def extract_policy_documents(self, url: str) -> List[Dict[str, Any]]:
        """
        Extract links to policy documents (PDFs, etc.) from a page
        
        Args:
            url: URL to scrape
            
        Returns:
            List of document links
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            documents = []
            
            # Find all links
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text().strip()
                
                # Check if it's a document
                if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xml']):
                    absolute_url = urljoin(url, href)
                    
                    # Determine document type
                    doc_type = 'unknown'
                    if '.pdf' in href.lower():
                        doc_type = 'pdf'
                    elif '.xml' in href.lower():
                        doc_type = 'xml'
                    elif '.doc' in href.lower():
                        doc_type = 'word'
                    
                    documents.append({
                        'url': absolute_url,
                        'title': text,
                        'type': doc_type
                    })
            
            return documents
            
        except Exception as e:
            print(f"Error extracting documents: {str(e)}")
            return []
    
    def format_scraped_content(self, result: Dict[str, Any]) -> str:
        """
        Format scraped content for display
        
        Args:
            result: Scraping result dictionary
            
        Returns:
            Formatted string
        """
        if result['status'] == 'error':
            return f"Error scraping {result['url']}: {result.get('error', 'Unknown error')}"
        
        output = f"""
URL: {result['url']}
Title: {result['title']}
Government Site: {'Yes' if result['is_government'] else 'No'}
Word Count: {result['word_count']}

Content Preview:
{result['content'][:500]}...

Links Found: {len(result['links'])}
"""
        return output.strip()


def test_url_scraper():
    """Test the URL scraper tool"""
    scraper = URLScraperTool()
    
    print("=== Testing URL Scraper Tool ===\n")
    
    # Test 1: Scrape EPA regulations page
    print("1. Scraping EPA regulations page...")
    epa_url = "https://www.epa.gov/laws-regulations"
    result = scraper.scrape_url(epa_url)
    print(f"Status: {result['status']}")
    print(f"Title: {result['title']}")
    print(f"Word count: {result['word_count']}")
    print(f"Is government: {result['is_government']}")
    print(f"Links found: {len(result['links'])}")
    
    # Test 2: Extract policy documents
    print("\n2. Extracting policy documents from EPA page...")
    documents = scraper.extract_policy_documents(epa_url)
    print(f"Found {len(documents)} document links")
    if documents:
        print(f"\nFirst document: {documents[0]['title']} ({documents[0]['type']})")
    
    # Test 3: Scrape Federal Register page
    print("\n3. Scraping Federal Register page...")
    fr_url = "https://www.federalregister.gov/documents/search"
    result2 = scraper.scrape_url(fr_url)
    print(f"Status: {result2['status']}")
    print(f"Title: {result2['title']}")
    print(f"Is government: {result2['is_government']}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_url_scraper()
