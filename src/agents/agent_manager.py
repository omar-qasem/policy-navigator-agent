"""
Agent Manager for Policy Navigator
Handles aiXplain Team Agent integration for multi-agent RAG system
"""

import os
import sys
from typing import Dict, Any, Optional, List
from aixplain.factories import AgentFactory
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.courtlistener_tool import CourtListenerTool
from src.tools.federal_register_tool import FederalRegisterTool


class AgentManager:
    """Manages aiXplain Team Agent and sub-agents"""
    
    # Agent IDs from aiXplain platform
    TEAM_AGENT_ID = '6905048fa1a609715ed913cc'
    RAG_AGENT_ID = '6905048c56dba9504302685f'
    API_AGENT_ID = '6905048d56dba95043026860'
    SCRAPER_AGENT_ID = '6905048ea1a609715ed913cb'
    
    def __init__(self):
        """Initialize agent manager"""
        # Load environment variables
        load_dotenv()
        
        # Verify API key is set
        api_key = os.getenv('AIXPLAIN_API_KEY')
        if not api_key:
            raise ValueError("AIXPLAIN_API_KEY not found in environment variables")
        
        self.team_agent = None
        self.rag_agent = None
        self.api_agent = None
        self.scraper_agent = None
        
        # Initialize custom tools
        self.courtlistener_tool = CourtListenerTool()  # Fallback mode (no API key)
        self.federal_register_tool = FederalRegisterTool()
        
        self._load_agents()
    
    def _load_agents(self):
        """Load agents from aiXplain platform"""
        try:
            print("Loading aiXplain agents...")
            
            # Load Team Agent (main orchestrator)
            self.team_agent = AgentFactory.get(self.TEAM_AGENT_ID)
            print(f"✓ Team Agent loaded: {self.TEAM_AGENT_ID}")
            
            # Load individual agents (optional, for direct access)
            try:
                self.rag_agent = AgentFactory.get(self.RAG_AGENT_ID)
                print(f"✓ RAG Agent loaded: {self.RAG_AGENT_ID}")
            except Exception as e:
                print(f"⚠ RAG Agent not loaded: {str(e)}")
            
            try:
                self.api_agent = AgentFactory.get(self.API_AGENT_ID)
                print(f"✓ API Agent loaded: {self.API_AGENT_ID}")
            except Exception as e:
                print(f"⚠ API Agent not loaded: {str(e)}")
            
            try:
                self.scraper_agent = AgentFactory.get(self.SCRAPER_AGENT_ID)
                print(f"✓ Scraper Agent loaded: {self.SCRAPER_AGENT_ID}")
            except Exception as e:
                print(f"⚠ Scraper Agent not loaded: {str(e)}")
            
        except Exception as e:
            print(f"✗ Error loading agents: {str(e)}")
            raise
    
    def query(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send query to Team Agent for processing
        
        Args:
            user_query: User's question
            context: Optional context (retrieved documents, metadata, etc.)
            
        Returns:
            Dictionary with agent response
        """
        try:
            # Prepare the query with context if provided
            if context and context.get('documents'):
                # Include retrieved documents in the query
                docs_text = "\n\n".join([
                    f"Document {i+1} (from {doc['metadata'].get('title', 'Unknown')}):\n{doc['content'][:800]}"
                    for i, doc in enumerate(context['documents'])
                ])
                
                enhanced_query = f"""User Question: {user_query}

Retrieved Policy Documents:
{docs_text}

Please answer the user's question based on the provided documents. If the documents don't contain sufficient information, indicate that and provide general guidance."""
            else:
                enhanced_query = user_query
            
            # Run Team Agent
            print(f"Sending query to Team Agent: {user_query[:100]}...")
            response = self.team_agent.run(enhanced_query)
            
            # Extract response
            if hasattr(response, 'data'):
                answer = response.data
            elif isinstance(response, dict):
                answer = response.get('data', str(response))
            else:
                answer = str(response)
            
            return {
                'success': True,
                'answer': answer,
                'agent': 'Team Agent',
                'agent_id': self.TEAM_AGENT_ID
            }
            
        except Exception as e:
            print(f"Error in agent query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': 'Team Agent',
                'agent_id': self.TEAM_AGENT_ID
            }
    
    def query_rag_agent(self, query: str, documents: list) -> Dict[str, Any]:
        """
        Query RAG agent directly
        
        Args:
            query: User query
            documents: Retrieved documents
            
        Returns:
            Agent response
        """
        if not self.rag_agent:
            return {'success': False, 'error': 'RAG Agent not available'}
        
        try:
            # Prepare context
            context = "\n\n".join([
                f"{doc['metadata'].get('title', 'Unknown')}:\n{doc['content'][:500]}"
                for doc in documents
            ])
            
            prompt = f"Question: {query}\n\nContext:\n{context}\n\nAnswer:"
            response = self.rag_agent.run(prompt)
            
            return {
                'success': True,
                'answer': response.data if hasattr(response, 'data') else str(response),
                'agent': 'RAG Agent'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def query_api_agent(self, query: str) -> Dict[str, Any]:
        """
        Query API agent for Federal Register data
        
        Args:
            query: Search query
            
        Returns:
            Agent response
        """
        if not self.api_agent:
            return {'success': False, 'error': 'API Agent not available'}
        
        try:
            response = self.api_agent.run(f"Search Federal Register for: {query}")
            return {
                'success': True,
                'answer': response.data if hasattr(response, 'data') else str(response),
                'agent': 'API Agent'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def query_scraper_agent(self, url: str) -> Dict[str, Any]:
        """
        Query scraper agent to extract content from URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Agent response
        """
        if not self.scraper_agent:
            return {'success': False, 'error': 'Scraper Agent not available'}
        
        try:
            response = self.scraper_agent.run(f"Extract content from: {url}")
            return {
                'success': True,
                'answer': response.data if hasattr(response, 'data') else str(response),
                'agent': 'Scraper Agent'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_case_law(self, regulation: str, section: str = None) -> Dict[str, Any]:
        """
        Check if a regulation has been challenged in court using CourtListener.
        
        Args:
            regulation: Regulation name (e.g., "Clean Air Act")
            section: Optional section number (e.g., "Section 230")
            
        Returns:
            Dictionary with case law information
        """
        try:
            result = self.courtlistener_tool.check_regulation_challenges(regulation, section)
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'data': result,
                    'formatted': self.courtlistener_tool.format_for_agent(result),
                    'source': 'CourtListener API'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'source': 'CourtListener API'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'CourtListener API'
            }
    
    def search_court_cases(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for court cases related to a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results
        """
        try:
            result = self.courtlistener_tool.search_opinions(query, limit=limit)
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'data': result,
                    'formatted': self.courtlistener_tool.format_for_agent(result),
                    'source': 'CourtListener API'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'source': 'CourtListener API'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'CourtListener API'
            }
    
    def get_agent_status(self) -> Dict[str, bool]:
        """
        Get status of all agents and tools
        
        Returns:
            Dictionary with agent and tool availability status
        """
        return {
            'team_agent': self.team_agent is not None,
            'rag_agent': self.rag_agent is not None,
            'api_agent': self.api_agent is not None,
            'scraper_agent': self.scraper_agent is not None,
            'courtlistener_tool': self.courtlistener_tool is not None,
            'federal_register_tool': self.federal_register_tool is not None
        }


if __name__ == "__main__":
    # Test agent manager
    print("Testing Agent Manager...")
    print("="*60)
    
    try:
        manager = AgentManager()
        
        # Check status
        status = manager.get_agent_status()
        print("\nAgent Status:")
        for agent, available in status.items():
            print(f"  {agent}: {'✓ Available' if available else '✗ Not Available'}")
        
        # Test query
        print("\nTesting Team Agent query...")
        result = manager.query("What are EPA air quality regulations?")
        
        if result['success']:
            print(f"\n✓ Query successful!")
            print(f"Answer: {result['answer'][:200]}...")
        else:
            print(f"\n✗ Query failed: {result.get('error')}")
        
        print("\n" + "="*60)
        print("✓ Agent Manager test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
