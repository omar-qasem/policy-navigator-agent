"""
Federal Register API Tool for Policy Navigator Agent
Checks latest policy status, amendments, and executive orders
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class FederalRegisterTool:
    """Tool to interact with Federal Register API"""
    
    def __init__(self):
        self.base_url = "https://www.federalregister.gov/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolicyNavigatorAgent/1.0'
        })
    
    def search_documents(self, query: str, page: int = 1, per_page: int = 20,
                        document_types: Optional[List[str]] = None,
                        agencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search Federal Register documents
        
        Args:
            query: Search query string
            page: Page number
            per_page: Results per page
            document_types: Filter by document types (RULE, PRORULE, NOTICE, PRESDOCU)
            agencies: Filter by agency slugs
            
        Returns:
            Dictionary containing search results
        """
        endpoint = f"{self.base_url}/documents.json"
        
        params = {
            'conditions[term]': query,
            'page': page,
            'per_page': per_page
        }
        
        if document_types:
            params['conditions[type][]'] = document_types
        
        if agencies:
            params['conditions[agencies][]'] = agencies
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error searching Federal Register: {str(e)}")
            return {'results': [], 'count': 0}
    
    def get_document(self, document_number: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific Federal Register document by number
        
        Args:
            document_number: Federal Register document number (e.g., "2024-12345")
            
        Returns:
            Document data or None if not found
        """
        endpoint = f"{self.base_url}/documents/{document_number}.json"
        
        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting document {document_number}: {str(e)}")
            return None
    
    def get_recent_rules(self, days: int = 30, agency: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent final rules from the last N days
        
        Args:
            days: Number of days to look back
            agency: Optional agency slug to filter by
            
        Returns:
            List of recent rules
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        endpoint = f"{self.base_url}/documents.json"
        
        params = {
            'conditions[type][]': 'RULE',
            'conditions[publication_date][gte]': start_date,
            'conditions[publication_date][lte]': end_date,
            'per_page': 100,
            'order': 'newest'
        }
        
        if agency:
            params['conditions[agencies][]'] = agency
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error getting recent rules: {str(e)}")
            return []
    
    def get_executive_orders(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get executive orders
        
        Args:
            year: Optional year to filter by
            
        Returns:
            List of executive orders
        """
        endpoint = f"{self.base_url}/documents.json"
        
        params = {
            'conditions[type]': 'PRESDOCU',
            'conditions[presidential_document_type]': 'executive_order',
            'per_page': 100,
            'order': 'newest'
        }
        
        if year:
            params['conditions[publication_date][year]'] = year
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error getting executive orders: {str(e)}")
            return []
    
    def check_cfr_updates(self, title: str, part: str) -> List[Dict[str, Any]]:
        """
        Check for recent updates to a specific CFR title and part
        
        Args:
            title: CFR title number (e.g., "40")
            part: CFR part number (e.g., "60")
            
        Returns:
            List of documents affecting this CFR section
        """
        query = f"{title} CFR {part}"
        
        endpoint = f"{self.base_url}/documents.json"
        
        params = {
            'conditions[term]': query,
            'conditions[type][]': ['RULE', 'PRORULE'],
            'per_page': 50,
            'order': 'newest'
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error checking CFR updates: {str(e)}")
            return []
    
    def get_agency_documents(self, agency_slug: str, document_type: str = 'RULE',
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get documents from a specific agency
        
        Args:
            agency_slug: Agency slug (e.g., "environmental-protection-agency")
            document_type: Type of document (RULE, PRORULE, NOTICE, PRESDOCU)
            limit: Maximum number of results
            
        Returns:
            List of agency documents
        """
        endpoint = f"{self.base_url}/documents.json"
        
        params = {
            'conditions[agencies][]': agency_slug,
            'conditions[type]': document_type,
            'per_page': limit,
            'order': 'newest'
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error getting agency documents: {str(e)}")
            return []
    
    def format_document_summary(self, document: Dict[str, Any]) -> str:
        """
        Format a document into a readable summary
        
        Args:
            document: Document data from API
            
        Returns:
            Formatted string summary
        """
        title = document.get('title', 'No title')
        doc_number = document.get('document_number', 'Unknown')
        publication_date = document.get('publication_date', 'Unknown')
        doc_type = document.get('type', 'Unknown')
        agencies = document.get('agencies', [])
        agency_names = [a.get('name', '') for a in agencies]
        
        abstract = document.get('abstract', '')
        if abstract and len(abstract) > 200:
            abstract = abstract[:200] + "..."
        
        html_url = document.get('html_url', '')
        
        summary = f"""
Document Number: {doc_number}
Title: {title}
Type: {doc_type}
Publication Date: {publication_date}
Agencies: {', '.join(agency_names)}
Abstract: {abstract}
URL: {html_url}
"""
        return summary.strip()


def test_federal_register_tool():
    """Test the Federal Register tool"""
    tool = FederalRegisterTool()
    
    print("=== Testing Federal Register API Tool ===\n")
    
    # Test 1: Search for EPA regulations
    print("1. Searching for EPA environmental regulations...")
    results = tool.search_documents("environmental protection", per_page=5,
                                   agencies=['environmental-protection-agency'])
    print(f"Found {results.get('count', 0)} total documents")
    if results.get('results'):
        print("\nFirst result:")
        print(tool.format_document_summary(results['results'][0]))
    
    # Test 2: Get recent rules
    print("\n2. Getting recent EPA rules (last 30 days)...")
    recent_rules = tool.get_recent_rules(days=30, agency='environmental-protection-agency')
    print(f"Found {len(recent_rules)} recent EPA rules")
    if recent_rules:
        print(f"\nMost recent: {recent_rules[0].get('title', 'No title')}")
    
    # Test 3: Check CFR updates
    print("\n3. Checking for updates to 40 CFR 60...")
    updates = tool.check_cfr_updates("40", "60")
    print(f"Found {len(updates)} documents affecting 40 CFR 60")
    if updates:
        print(f"\nMost recent: {updates[0].get('title', 'No title')}")
    
    # Test 4: Get executive orders
    print("\n4. Getting recent executive orders...")
    exec_orders = tool.get_executive_orders(year=2024)
    print(f"Found {len(exec_orders)} executive orders in 2024")
    if exec_orders:
        print(f"\nMost recent: {exec_orders[0].get('title', 'No title')}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_federal_register_tool()
