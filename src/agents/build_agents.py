"""
Build aiXplain Agents for Policy Navigator
Creates RAG agent, API agent, and Team Agent
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aixplain.factories import AgentFactory, TeamAgentFactory
from aixplain.modules.agent import Agent
from aixplain.modules.team_agent import TeamAgent
from typing import Optional


class PolicyNavigatorAgentBuilder:
    """Build and manage Policy Navigator agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize agent builder
        
        Args:
            api_key: aiXplain API key (optional, will use env var if not provided)
        """
        if api_key:
            os.environ['AIXPLAIN_API_KEY'] = api_key
        elif not os.getenv('AIXPLAIN_API_KEY'):
            raise ValueError("AIXPLAIN_API_KEY not found in environment variables")
        
        self.agents = {}
    
    def create_rag_agent(self) -> Agent:
        """
        Create RAG agent for policy document retrieval
        
        Returns:
            RAG Agent instance
        """
        print("Creating RAG Agent...")
        
        instructions = """You are a Policy Document Retrieval Agent specialized in US government regulations.

Your responsibilities:
1. Search the vector database for relevant policy documents
2. Retrieve specific CFR (Code of Federal Regulations) sections
3. Provide accurate citations with title and section numbers
4. Extract and summarize relevant regulatory text
5. Answer questions about environmental regulations, FDA rules, and other federal policies

When responding:
- Always cite the source (e.g., "40 CFR § 60.1")
- Provide the exact regulatory text when available
- Explain complex regulations in plain language
- Indicate if information is not found in the database

You have access to:
- 3,000+ sections from CFR Title 40 (Environmental Protection)
- Vector search capabilities for semantic retrieval
- Metadata including title, section, and subject information
"""
        
        try:
            rag_agent = AgentFactory.create(
                name="Policy RAG Agent",
                description="Retrieves and answers questions about US government policy documents",
                instructions=instructions,
                tools=[],  # Tools will be added separately
            )
            
            print(f"✓ RAG Agent created: {rag_agent.id}")
            self.agents['rag_agent'] = rag_agent
            return rag_agent
            
        except Exception as e:
            print(f"Error creating RAG agent: {str(e)}")
            raise
    
    def create_api_agent(self) -> Agent:
        """
        Create API agent for Federal Register queries
        
        Returns:
            API Agent instance
        """
        print("Creating API Agent...")
        
        instructions = """You are a Federal Register API Agent specialized in checking policy status and updates.

Your responsibilities:
1. Check the latest status of federal regulations
2. Search for recent rule changes and amendments
3. Retrieve executive orders and presidential documents
4. Monitor agency-specific regulatory actions
5. Provide information about proposed rules and public comments

When responding:
- Provide document numbers for reference
- Include publication dates
- Link to official Federal Register URLs
- Summarize key changes and impacts
- Distinguish between proposed and final rules

You have access to:
- Federal Register API for real-time regulatory data
- Search capabilities across all federal agencies
- Historical regulatory documents
- Executive orders and presidential actions
"""
        
        try:
            api_agent = AgentFactory.create(
                name="Federal Register API Agent",
                description="Checks policy status and retrieves regulatory updates via Federal Register API",
                instructions=instructions,
                tools=[],  # Tools will be added separately
            )
            
            print(f"✓ API Agent created: {api_agent.id}")
            self.agents['api_agent'] = api_agent
            return api_agent
            
        except Exception as e:
            print(f"Error creating API agent: {str(e)}")
            raise
    
    def create_scraper_agent(self) -> Agent:
        """
        Create web scraper agent for government websites
        
        Returns:
            Scraper Agent instance
        """
        print("Creating Scraper Agent...")
        
        instructions = """You are a Web Scraper Agent specialized in extracting content from government websites.

Your responsibilities:
1. Scrape content from EPA, FDA, OSHA, and other government sites
2. Extract policy documents and guidance materials
3. Process user-provided URLs for policy information
4. Identify and download regulatory documents (PDFs, XMLs)
5. Validate that sources are official government sites

When responding:
- Verify URLs are from .gov domains
- Extract main content while filtering navigation and ads
- Provide clean, formatted text from web pages
- List any policy documents found on the page
- Include source URLs for verification

You have access to:
- Web scraping capabilities for government sites
- Document extraction tools
- URL validation and processing
- Content cleaning and formatting
"""
        
        try:
            scraper_agent = AgentFactory.create(
                name="Web Scraper Agent",
                description="Extracts policy content from government websites and user-provided URLs",
                instructions=instructions,
                tools=[],  # Tools will be added separately
            )
            
            print(f"✓ Scraper Agent created: {scraper_agent.id}")
            self.agents['scraper_agent'] = scraper_agent
            return scraper_agent
            
        except Exception as e:
            print(f"Error creating scraper agent: {str(e)}")
            raise
    
    def create_coordinator_agent(self) -> Agent:
        """
        Create coordinator agent for query routing
        
        Returns:
            Coordinator Agent instance
        """
        print("Creating Coordinator Agent...")
        
        instructions = """You are the Coordinator Agent for the Policy Navigator system.

Your responsibilities:
1. Analyze user queries and determine the best approach
2. Route questions to the appropriate specialized agent
3. Synthesize responses from multiple agents
4. Provide comprehensive answers with proper citations
5. Handle document upload and URL processing requests

Query routing guidelines:
- Use RAG Agent for: Questions about specific regulations, CFR sections, policy details
- Use API Agent for: Recent changes, new rules, executive orders, policy status checks
- Use Scraper Agent for: User-provided URLs, website content extraction
- Use multiple agents when: Query requires both historical context and recent updates

When responding:
- Provide clear, well-structured answers
- Include citations from all sources used
- Distinguish between different information sources
- Offer to clarify or provide additional details
- Suggest related regulations or policies when relevant
"""
        
        try:
            coordinator_agent = AgentFactory.create(
                name="Policy Navigator Coordinator",
                description="Routes queries and coordinates responses from specialized policy agents",
                instructions=instructions,
                tools=[],  # Tools will be added separately
            )
            
            print(f"✓ Coordinator Agent created: {coordinator_agent.id}")
            self.agents['coordinator_agent'] = coordinator_agent
            return coordinator_agent
            
        except Exception as e:
            print(f"Error creating coordinator agent: {str(e)}")
            raise
    
    def create_team_agent(self) -> TeamAgent:
        """
        Create team agent that coordinates all specialized agents
        
        Returns:
            Team Agent instance
        """
        print("\nCreating Team Agent...")
        
        # First create individual agents if not already created
        if 'rag_agent' not in self.agents:
            self.create_rag_agent()
        
        if 'api_agent' not in self.agents:
            self.create_api_agent()
        
        if 'scraper_agent' not in self.agents:
            self.create_scraper_agent()
        
        instructions = """You are the Policy Navigator Team Agent, coordinating multiple specialized agents to answer questions about US government regulations and policies.

Your team includes:
1. RAG Agent - Searches indexed policy documents (3,000+ CFR sections)
2. API Agent - Checks Federal Register for recent updates and changes
3. Scraper Agent - Extracts content from government websites and user URLs

How to handle queries:
1. Analyze the user's question
2. Determine which agent(s) can best answer it
3. Coordinate between agents when multiple sources are needed
4. Synthesize a comprehensive response with proper citations
5. Provide source references for all information

Response format:
- Start with a direct answer to the question
- Provide relevant regulatory text with citations
- Include recent updates if applicable
- List all sources used
- Offer to provide more details or related information

Special capabilities:
- Document upload: Process user-uploaded policy documents
- URL extraction: Scrape and index content from provided URLs
- Multi-source synthesis: Combine historical regulations with recent changes
- Citation tracking: Maintain accurate references to all sources
"""
        
        try:
            team_agent = TeamAgentFactory.create(
                name="Policy Navigator Team",
                description="Multi-agent system for comprehensive US government policy and regulation queries",
                instructions=instructions,
                agents=[
                    self.agents['rag_agent'],
                    self.agents['api_agent'],
                    self.agents['scraper_agent']
                ],
                llm_id="6646261c6eb563165658bbb1"  # GPT-4o
            )
            
            print(f"✓ Team Agent created: {team_agent.id}")
            self.agents['team_agent'] = team_agent
            return team_agent
            
        except Exception as e:
            print(f"Error creating team agent: {str(e)}")
            raise
    
    def deploy_agents(self):
        """Deploy all agents to make them permanent"""
        print("\nDeploying agents...")
        
        for name, agent in self.agents.items():
            if name != 'team_agent':  # Deploy individual agents first
                try:
                    agent.deploy()
                    print(f"✓ Deployed {name}")
                except Exception as e:
                    print(f"✗ Error deploying {name}: {str(e)}")
        
        # Deploy team agent last
        if 'team_agent' in self.agents:
            try:
                self.agents['team_agent'].deploy()
                print(f"✓ Deployed team_agent")
            except Exception as e:
                print(f"✗ Error deploying team_agent: {str(e)}")
    
    def save_agent_ids(self, filepath: str = "agent_ids.json"):
        """Save agent IDs to file for later use"""
        import json
        
        agent_data = {}
        for name, agent in self.agents.items():
            agent_data[name] = {
                'id': agent.id,
                'name': agent.name
            }
        
        with open(filepath, 'w') as f:
            json.dump(agent_data, f, indent=2)
        
        print(f"\n✓ Agent IDs saved to {filepath}")


def main():
    """Main function to build agents"""
    print("=== Building Policy Navigator Agents ===\n")
    
    # Check for API key
    api_key = os.getenv('AIXPLAIN_API_KEY')
    if not api_key:
        print("Error: AIXPLAIN_API_KEY not found in environment variables")
        print("Please set it in .env file or export it:")
        print("export AIXPLAIN_API_KEY='your_api_key_here'")
        return
    
    try:
        # Initialize builder
        builder = PolicyNavigatorAgentBuilder(api_key=api_key)
        
        # Create individual agents
        builder.create_rag_agent()
        builder.create_api_agent()
        builder.create_scraper_agent()
        
        # Create team agent
        builder.create_team_agent()
        
        # Save agent IDs
        builder.save_agent_ids("/home/ubuntu/policy-navigator-agent/agent_ids.json")
        
        # Ask if user wants to deploy
        print("\n" + "="*50)
        print("Agents created successfully!")
        print("Note: Agents are in draft mode (expire in 24 hours)")
        print("To make them permanent, run: builder.deploy_agents()")
        print("="*50)
        
    except Exception as e:
        print(f"\nError building agents: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
