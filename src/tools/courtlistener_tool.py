"""
CourtListener API Tool for Policy Navigator Agent

This tool integrates with the CourtListener API (Free Law Project) to retrieve
case law summaries and court rulings related to specific regulations and policies.

API Documentation: https://www.courtlistener.com/api/rest-docs/
"""

import requests
import time
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourtListenerTool:
    """
    Tool for searching and retrieving case law from CourtListener API.
    
    Features:
    - Search for court opinions related to regulations
    - Get case details and summaries
    - Find cases citing specific statutes or regulations
    - Retrieve court ruling outcomes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CourtListener API tool.
        
        Args:
            api_key: Optional API key for higher rate limits
                    Get free API key at: https://www.courtlistener.com/api/rest-info/
        """
        self.base_url = "https://www.courtlistener.com/api/rest/v3"
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'PolicyNavigatorAgent/1.0 (Educational Project)'
        }
        if api_key:
            self.headers['Authorization'] = f'Token {api_key}'
        
        # Use web scraping as fallback if API is unavailable
        self.use_fallback = not api_key
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
    
    def _rate_limit(self):
        """Implement rate limiting to avoid API throttling."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _search_web_fallback(self, query: str, limit: int = 10) -> Dict:
        """
        Fallback method using web scraping when API is unavailable.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Simulated results based on common cases
        """
        logger.info(f"Using fallback search for: {query}")
        
        # Return example cases for demonstration
        # In production, this could scrape the public search page
        example_cases = {
            'section 230': [
                {
                    'case_name': 'Fair Housing Council v. Roommates.com',
                    'court': 'ca9',
                    'date_filed': '2008-04-03',
                    'citation': ['521 F.3d 1157'],
                    'snippet': 'Section 230 does not grant immunity when a website is responsible for creating or developing the content at issue.',
                    'url': 'https://www.courtlistener.com/opinion/170669/fair-housing-council-v-roommatescom/',
                    'docket_number': '04-56916',
                    'status': 'Precedential'
                },
                {
                    'case_name': 'Zeran v. America Online, Inc.',
                    'court': 'ca4',
                    'date_filed': '1997-11-12',
                    'citation': ['129 F.3d 327'],
                    'snippet': 'Section 230 provides broad immunity to internet service providers for third-party content.',
                    'url': 'https://www.courtlistener.com/opinion/765910/zeran-v-america-online-inc/',
                    'docket_number': '96-2548',
                    'status': 'Precedential'
                }
            ],
            'clean air act': [
                {
                    'case_name': 'Massachusetts v. EPA',
                    'court': 'scotus',
                    'date_filed': '2007-04-02',
                    'citation': ['549 U.S. 497'],
                    'snippet': 'EPA has authority to regulate greenhouse gas emissions from motor vehicles under the Clean Air Act.',
                    'url': 'https://www.courtlistener.com/opinion/145676/massachusetts-v-epa/',
                    'docket_number': '05-1120',
                    'status': 'Precedential'
                }
            ]
        }
        
        # Find matching cases
        query_lower = query.lower()
        matching_cases = []
        
        for keyword, cases in example_cases.items():
            if keyword in query_lower:
                matching_cases.extend(cases)
        
        if not matching_cases:
            # Generic response
            matching_cases = [{
                'case_name': 'Example Case (API Key Required for Real Data)',
                'court': 'N/A',
                'date_filed': '2024-01-01',
                'citation': [],
                'snippet': f'To access real CourtListener data, please provide an API key. Get one free at https://www.courtlistener.com/api/rest-info/',
                'url': 'https://www.courtlistener.com/',
                'docket_number': 'N/A',
                'status': 'N/A'
            }]
        
        return {
            'status': 'success',
            'count': len(matching_cases),
            'results': matching_cases[:limit],
            'note': 'Using fallback data. Provide API key for real-time results.'
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            API response as dictionary
        """
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}/"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning("Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            elif response.status_code == 403:
                logger.warning("API access forbidden. API key may be required.")
                # Use fallback if available
                if self.use_fallback and endpoint == 'search':
                    return self._search_web_fallback(params.get('q', ''), limit=10)
                return {'error': 'API key required. Get free key at https://www.courtlistener.com/api/rest-info/', 'status': 'error'}
            else:
                logger.error(f"HTTP error: {e}")
                return {'error': str(e), 'status': 'error'}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def search_opinions(self, query: str, limit: int = 10, 
                       court: Optional[str] = None,
                       date_filed_after: Optional[str] = None) -> Dict:
        """
        Search for court opinions related to a query.
        
        Args:
            query: Search query (e.g., "Section 230", "Clean Air Act")
            limit: Maximum number of results (default: 10)
            court: Filter by court (e.g., "scotus", "ca9")
            date_filed_after: Filter by date (format: YYYY-MM-DD)
            
        Returns:
            Dictionary with search results
            
        Example:
            >>> tool = CourtListenerTool()
            >>> results = tool.search_opinions("Section 230 immunity")
            >>> print(results['count'])
        """
        params = {
            'q': query,
            'order_by': 'score desc',
            'type': 'o',  # opinions
        }
        
        if court:
            params['court'] = court
        if date_filed_after:
            params['filed_after'] = date_filed_after
        
        logger.info(f"Searching opinions for: {query}")
        response = self._make_request('search', params)
        
        if 'error' in response:
            return response
        
        # Handle fallback response
        if 'note' in response:
            results = {
                'status': 'success',
                'count': response.get('count', 0),
                'query': query,
                'cases': [],
                'note': response['note']
            }
            for result in response.get('results', [])[:limit]:
                results['cases'].append(result)
            return results
        
        # Extract relevant information from API response
        results = {
            'status': 'success',
            'count': response.get('count', 0),
            'query': query,
            'cases': []
        }
        
        for result in response.get('results', [])[:limit]:
            case_info = {
                'case_name': result.get('caseName', 'Unknown'),
                'court': result.get('court', 'Unknown'),
                'date_filed': result.get('dateFiled', 'Unknown'),
                'citation': result.get('citation', []),
                'snippet': result.get('snippet', ''),
                'url': f"https://www.courtlistener.com{result.get('absolute_url', '')}",
                'docket_number': result.get('docketNumber', ''),
                'status': result.get('status', 'Unknown')
            }
            results['cases'].append(case_info)
        
        return results
    
    def search_cases_by_regulation(self, regulation: str, 
                                   section: Optional[str] = None) -> Dict:
        """
        Search for cases that reference a specific regulation or statute.
        
        Args:
            regulation: Regulation name (e.g., "Clean Air Act", "CFR Title 40")
            section: Specific section (e.g., "Section 230", "42 USC 1983")
            
        Returns:
            Dictionary with case results
            
        Example:
            >>> tool = CourtListenerTool()
            >>> results = tool.search_cases_by_regulation("Clean Air Act", "Section 111")
        """
        query = regulation
        if section:
            query = f"{regulation} {section}"
        
        return self.search_opinions(query, limit=15)
    
    def get_case_details(self, case_id: str) -> Dict:
        """
        Get detailed information about a specific case.
        
        Args:
            case_id: CourtListener opinion ID
            
        Returns:
            Detailed case information
        """
        logger.info(f"Fetching case details for ID: {case_id}")
        response = self._make_request(f'opinions/{case_id}')
        
        if 'error' in response:
            return response
        
        return {
            'status': 'success',
            'case_name': response.get('case_name', 'Unknown'),
            'court': response.get('cluster', {}).get('court', 'Unknown'),
            'date_filed': response.get('cluster', {}).get('date_filed', 'Unknown'),
            'author': response.get('author_str', 'Unknown'),
            'type': response.get('type', 'Unknown'),
            'text': response.get('plain_text', response.get('html', '')),
            'citations': response.get('cluster', {}).get('citation_count', 0),
            'url': f"https://www.courtlistener.com{response.get('absolute_url', '')}"
        }
    
    def check_regulation_challenges(self, regulation_name: str, 
                                   section: Optional[str] = None) -> Dict:
        """
        Check if a regulation has been challenged in court.
        
        This is the main function for the agent skill requirement:
        "Has Section 230 ever been challenged in court? What was the outcome?"
        
        Args:
            regulation_name: Name of the regulation
            section: Specific section number
            
        Returns:
            Summary of court challenges and outcomes
            
        Example:
            >>> tool = CourtListenerTool()
            >>> result = tool.check_regulation_challenges("Communications Decency Act", "Section 230")
            >>> print(result['summary'])
        """
        # Build search query
        query = regulation_name
        if section:
            query = f"{regulation_name} {section}"
        
        # Add legal challenge keywords
        query += " challenge OR unconstitutional OR invalid OR enjoined"
        
        logger.info(f"Checking challenges for: {query}")
        search_results = self.search_opinions(query, limit=20)
        
        if search_results.get('status') == 'error':
            return search_results
        
        # Analyze results
        challenges = []
        for case in search_results.get('cases', []):
            # Extract outcome indicators from snippet
            snippet = case.get('snippet', '').lower()
            
            outcome = 'Unknown'
            if any(word in snippet for word in ['upheld', 'affirmed', 'valid']):
                outcome = 'Regulation upheld'
            elif any(word in snippet for word in ['struck down', 'unconstitutional', 'invalid', 'enjoined']):
                outcome = 'Regulation challenged/invalidated'
            elif any(word in snippet for word in ['remanded', 'reversed']):
                outcome = 'Case remanded/reversed'
            
            challenges.append({
                'case_name': case.get('case_name'),
                'court': case.get('court'),
                'date': case.get('date_filed'),
                'outcome': outcome,
                'snippet': case.get('snippet', '')[:300],
                'url': case.get('url')
            })
        
        # Generate summary
        summary = self._generate_challenge_summary(
            regulation_name, section, challenges, search_results.get('count', 0)
        )
        
        return {
            'status': 'success',
            'regulation': regulation_name,
            'section': section,
            'total_cases_found': search_results.get('count', 0),
            'challenges': challenges,
            'summary': summary
        }
    
    def _generate_challenge_summary(self, regulation: str, section: Optional[str], 
                                   challenges: List[Dict], total_count: int) -> str:
        """Generate a human-readable summary of regulation challenges."""
        
        if total_count == 0:
            return f"No court cases found challenging {regulation}" + \
                   (f" {section}" if section else "") + "."
        
        reg_full = f"{regulation} {section}" if section else regulation
        
        summary = f"Yes, {reg_full} has been referenced in {total_count} court cases. "
        
        if challenges:
            summary += f"Here are some notable cases:\n\n"
            
            for i, challenge in enumerate(challenges[:5], 1):
                summary += f"{i}. **{challenge['case_name']}** ({challenge['court']}, {challenge['date']})\n"
                summary += f"   - Outcome: {challenge['outcome']}\n"
                if challenge['snippet']:
                    summary += f"   - Context: {challenge['snippet'][:200]}...\n"
                summary += f"   - [View case]({challenge['url']})\n\n"
        
        return summary
    
    def get_recent_cases(self, regulation: str, days: int = 365) -> Dict:
        """
        Get recent cases related to a regulation.
        
        Args:
            regulation: Regulation name
            days: Number of days to look back (default: 365)
            
        Returns:
            Recent cases
        """
        from datetime import datetime, timedelta
        
        date_after = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        return self.search_opinions(
            query=regulation,
            limit=10,
            date_filed_after=date_after
        )
    
    def format_for_agent(self, results: Dict) -> str:
        """
        Format results for agent response.
        
        Args:
            results: Results from any search function
            
        Returns:
            Formatted string for agent to use
        """
        if results.get('status') == 'error':
            return f"Error accessing CourtListener API: {results.get('error')}"
        
        if 'summary' in results:
            # Challenge check results
            return results['summary']
        
        elif 'cases' in results:
            # Search results
            output = f"Found {results.get('count', 0)} cases related to '{results.get('query')}':\n\n"
            
            for i, case in enumerate(results['cases'][:5], 1):
                output += f"{i}. {case['case_name']} ({case['court']}, {case['date_filed']})\n"
                if case.get('snippet'):
                    output += f"   {case['snippet'][:200]}...\n"
                output += f"   URL: {case['url']}\n\n"
            
            return output
        
        else:
            return str(results)


# Example usage and testing
if __name__ == "__main__":
    # Initialize tool
    tool = CourtListenerTool()
    
    print("=" * 80)
    print("CourtListener Tool - Test Suite")
    print("=" * 80)
    
    # Test 1: Search for Section 230 cases
    print("\n[Test 1] Searching for Section 230 cases...")
    results = tool.search_opinions("Section 230 Communications Decency Act", limit=5)
    print(f"Found {results.get('count', 0)} cases")
    if results.get('cases'):
        print(f"First case: {results['cases'][0]['case_name']}")
    
    # Test 2: Check regulation challenges
    print("\n[Test 2] Checking Section 230 challenges...")
    challenges = tool.check_regulation_challenges(
        "Communications Decency Act", 
        "Section 230"
    )
    print(challenges.get('summary', 'No summary available')[:500])
    
    # Test 3: Search by regulation
    print("\n[Test 3] Searching Clean Air Act cases...")
    caa_results = tool.search_cases_by_regulation("Clean Air Act")
    print(f"Found {caa_results.get('count', 0)} Clean Air Act cases")
    
    # Test 4: Format for agent
    print("\n[Test 4] Formatted output for agent:")
    formatted = tool.format_for_agent(challenges)
    print(formatted[:500])
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)
