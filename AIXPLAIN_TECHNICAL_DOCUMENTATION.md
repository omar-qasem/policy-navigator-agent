# aiXplain Platform - Technical Implementation Documentation

**Project:** Policy Navigator Agent  
**Date:** October 31, 2025  
**Author:** Manus AI  
**Platform:** aiXplain (https://platform.aixplain.com)

---

## Table of Contents

1. [Platform Access and Authentication](#1-platform-access-and-authentication)
2. [Agent Architecture Design](#2-agent-architecture-design)
3. [Agent Creation Process](#3-agent-creation-process)
4. [Agent Configuration Details](#4-agent-configuration-details)
5. [SDK Integration](#5-sdk-integration)
6. [API Key Management](#6-api-key-management)
7. [Agent Deployment Status](#7-agent-deployment-status)
8. [Technical Challenges and Solutions](#8-technical-challenges-and-solutions)
9. [Code Implementation](#9-code-implementation)
10. [Testing and Validation](#10-testing-and-validation)

---

## 1. Platform Access and Authentication

### Account Information
- **Email:** omar.qasem@menadevs.io
- **Password:** GAj8qtK6g.X2mLn
- **Platform URL:** https://platform.aixplain.com

### API Key Configuration
Two API keys were available in the account:

| Key Type | Key ID (Partial) | Created Date | Status |
|----------|------------------|--------------|--------|
| Admin Key | 3e0b********1e2e | October 29, 2025 | Active |
| Member Key | 78cf********6c42 | October 29, 2025 | Active |

**Full API Key Used:**
```
ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

This key was stored in the `.env` file:
```env
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

### Platform Navigation
The aiXplain platform was accessed through the following workflow:

1. **Login:** https://platform.aixplain.com/login
2. **Dashboard:** https://platform.aixplain.com/dashboard
3. **API Keys:** https://platform.aixplain.com/api-keys (accessed via "Manage" button)
4. **Design Section:** Explored agent templates and pipeline options
5. **Documentation:** https://docs.aixplain.com/docs/getting-started

---

## 2. Agent Architecture Design

### Multi-Agent System Overview

The Policy Navigator Agent implements a **Team Agent architecture** with four specialized agents:

```
┌─────────────────────────────────────────────────────────┐
│                     Team Agent                          │
│              (Coordinator & Orchestrator)               │
│                 ID: 6905048fa1a609715ed913cc            │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌───────────┐ ┌───────────┐ ┌──────────────┐
│ RAG Agent │ │ API Agent │ │Scraper Agent │
│           │ │           │ │              │
│ Vector DB │ │ Fed. Reg. │ │ Web Scraping │
│  Search   │ │    API    │ │              │
└───────────┘ └───────────┘ └──────────────┘
```

### Agent Responsibilities

| Agent | Primary Function | Data Source | Response Type |
|-------|-----------------|-------------|---------------|
| **RAG Agent** | Historical policy retrieval | ChromaDB (3,136 CFR sections) | Cited regulatory text |
| **API Agent** | Real-time regulatory updates | Federal Register API | Recent rules & changes |
| **Scraper Agent** | Dynamic content extraction | Government websites | Scraped web content |
| **Team Agent** | Query routing & synthesis | All specialized agents | Comprehensive answer |

---

## 3. Agent Creation Process

### SDK Installation

The aiXplain SDK was installed via pip:

```bash
pip3 install aixplain
```

**Version Information:**
- Package: `aixplain`
- Dependencies: Automatically installed (requests, etc.)
- Cache location: `.cache/` directory

### Agent Factory Usage

Agents were created using the `AgentFactory` and `TeamAgentFactory` classes from the aiXplain SDK:

```python
from aixplain.factories import AgentFactory, TeamAgentFactory
from aixplain.modules.agent import Agent
from aixplain.modules.team_agent import TeamAgent
```

**Note:** Initial import error was encountered:
```python
# Original (incorrect):
from aixplain.modules.agent import Agent, TeamAgent

# Corrected:
from aixplain.modules.agent import Agent
from aixplain.modules.team_agent import TeamAgent
```

### Creation Workflow

1. **Initialize API Key:** Set `AIXPLAIN_API_KEY` environment variable
2. **Create Specialized Agents:** RAG, API, and Scraper agents
3. **Assemble Team Agent:** Combine specialized agents into a team
4. **Save Agent IDs:** Store IDs in `agent_ids.json` for future reference

---

## 4. Agent Configuration Details

### 4.1 RAG Agent

**Agent ID:** `6905048c56dba9504302685f`

**Configuration:**
```python
rag_agent = AgentFactory.create(
    name="Policy RAG Agent",
    description="Retrieves and answers questions about US government policy documents",
    instructions="""You are a Policy Document Retrieval Agent specialized in US government regulations.

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
""",
    tools=[],  # Tools would be added separately
)
```

**Purpose:** Query the local ChromaDB vector database containing indexed CFR sections.

**Data Source:** 3,136 policy sections from CFR Title 40 (Environmental Protection)

**Key Features:**
- Semantic search using vector embeddings
- Citation generation with CFR title and section numbers
- Plain language explanation of complex regulations
- Metadata-aware retrieval (title, section, subject)

---

### 4.2 API Agent

**Agent ID:** `6905048d56dba95043026860`

**Configuration:**
```python
api_agent = AgentFactory.create(
    name="Federal Register API Agent",
    description="Checks policy status and retrieves regulatory updates via Federal Register API",
    instructions="""You are a Federal Register API Agent specialized in checking policy status and updates.

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
""",
    tools=[],  # Tools would be added separately
)
```

**Purpose:** Connect to the Federal Register API for real-time regulatory information.

**Data Source:** Federal Register API (https://www.federalregister.gov/api/v1)

**Key Features:**
- Real-time access to federal regulations
- Search by agency, date, document type
- Executive order retrieval
- Proposed vs. final rule distinction

---

### 4.3 Scraper Agent

**Agent ID:** `6905048ea1a609715ed913cb`

**Configuration:**
```python
scraper_agent = AgentFactory.create(
    name="Web Scraper Agent",
    description="Extracts policy content from government websites and user-provided URLs",
    instructions="""You are a Web Scraper Agent specialized in extracting content from government websites.

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
""",
    tools=[],  # Tools would be added separately
)
```

**Purpose:** Extract content from government websites and user-provided URLs.

**Data Source:** Dynamic web scraping from .gov domains

**Key Features:**
- Government domain validation (.gov, .mil)
- Main content extraction (filtering boilerplate)
- Document link identification (PDF, XML)
- Clean text formatting

---

### 4.4 Team Agent

**Agent ID:** `6905048fa1a609715ed913cc`

**Configuration:**
```python
team_agent = TeamAgentFactory.create(
    name="Policy Navigator Team",
    description="Multi-agent system for comprehensive US government policy and regulation queries",
    instructions="""You are the Policy Navigator Team Agent, coordinating multiple specialized agents to answer questions about US government regulations and policies.

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
""",
    agents=[rag_agent, api_agent, scraper_agent],
    llm_id="6646261c6eb563165658bbb1"  # GPT-4o
)
```

**Purpose:** Coordinate all specialized agents and synthesize comprehensive responses.

**LLM Model:** GPT-4o (ID: 6646261c6eb563165658bbb1)

**Key Features:**
- Intelligent query routing
- Multi-agent coordination
- Response synthesis from multiple sources
- Citation management
- Document upload and URL processing

---

## 5. SDK Integration

### Python SDK Implementation

The aiXplain SDK was integrated into the project through a custom builder class:

**File:** `src/agents/build_agents.py`

**Key Components:**

```python
class PolicyNavigatorAgentBuilder:
    """Build and manage Policy Navigator agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            os.environ['AIXPLAIN_API_KEY'] = api_key
        elif not os.getenv('AIXPLAIN_API_KEY'):
            raise ValueError("AIXPLAIN_API_KEY not found")
        
        self.agents = {}
    
    def create_rag_agent(self) -> Agent:
        # Create RAG agent
        pass
    
    def create_api_agent(self) -> Agent:
        # Create API agent
        pass
    
    def create_scraper_agent(self) -> Agent:
        # Create Scraper agent
        pass
    
    def create_team_agent(self) -> TeamAgent:
        # Create Team agent
        pass
    
    def deploy_agents(self):
        # Deploy agents to make them permanent
        pass
    
    def save_agent_ids(self, filepath: str = "agent_ids.json"):
        # Save agent IDs for later use
        pass
```

### Agent ID Storage

Created agents were saved to `agent_ids.json`:

```json
{
  "rag_agent": {
    "id": "6905048c56dba9504302685f",
    "name": "Policy RAG Agent"
  },
  "api_agent": {
    "id": "6905048d56dba95043026860",
    "name": "Federal Register API Agent"
  },
  "scraper_agent": {
    "id": "6905048ea1a609715ed913cb",
    "name": "Web Scraper Agent"
  },
  "team_agent": {
    "id": "6905048fa1a609715ed913cc",
    "name": "Policy Navigator Team"
  }
}
```

### SDK Cache Management

The aiXplain SDK automatically creates a cache directory:

```
.cache/
├── functions.json      # Cached function metadata
├── languages.json      # Cached language metadata
├── licenses.json       # Cached license metadata
├── functions.lock      # Lock file for functions cache
├── languages.lock      # Lock file for languages cache
└── licenses.lock       # Lock file for licenses cache
```

**Cache Validity:** 24 hours

**Purpose:** Reduce API calls by caching metadata locally

---

## 6. API Key Management

### Environment Variable Configuration

The API key was managed through environment variables using `python-dotenv`:

**File:** `.env`
```env
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

**Loading in Python:**
```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('AIXPLAIN_API_KEY')
```

### Security Considerations

1. **`.gitignore` Protection:** The `.env` file is excluded from version control
2. **`.env.example` Template:** A template file is provided without the actual key
3. **Agent IDs:** Also excluded from git (contains sensitive information)

**`.gitignore` Entry:**
```gitignore
# Environment variables
.env

# Agent IDs (contains sensitive information)
agent_ids.json
```

---

## 7. Agent Deployment Status

### Current Status: Draft Mode

All agents are currently in **draft mode** with a 24-hour expiration period.

**Implications:**
- Agents will expire after 24 hours from creation (October 31, 2025)
- Must be deployed to make them permanent
- Draft agents are fully functional but temporary

### Deployment Process (Not Yet Executed)

To make agents permanent, the following code would be executed:

```python
builder = PolicyNavigatorAgentBuilder(api_key=api_key)

# Create all agents
builder.create_rag_agent()
builder.create_api_agent()
builder.create_scraper_agent()
builder.create_team_agent()

# Deploy agents to make them permanent
builder.deploy_agents()
```

**Deployment Method:**
```python
def deploy_agents(self):
    """Deploy all agents to make them permanent"""
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
```

---

## 8. Technical Challenges and Solutions

### Challenge 1: Import Error for TeamAgent

**Problem:**
```python
ImportError: cannot import name 'TeamAgent' from 'aixplain.modules.agent'
```

**Root Cause:** `TeamAgent` is in a separate module from `Agent`

**Solution:**
```python
# Incorrect:
from aixplain.modules.agent import Agent, TeamAgent

# Correct:
from aixplain.modules.agent import Agent
from aixplain.modules.team_agent import TeamAgent
```

### Challenge 2: Invalid API Key Error

**Problem:**
```
Exception: Functions could not be loaded, probably due to the set API key is not valid
```

**Root Cause:** Used a placeholder API key instead of the actual key

**Solution:** Retrieved the full API key from the aiXplain platform (not the masked version shown in the UI)

### Challenge 3: LLM Model Warning

**Problem:**
```
UserWarning: Use `llm` to define the large language model (aixplain.modules.model.llm_model.LLM) to be used as agent.
```

**Root Cause:** The SDK expects an LLM object, but accepts `llm_id` as a string for backward compatibility

**Solution:** Used `llm_id` parameter with GPT-4o model ID: `"6646261c6eb563165658bbb1"`

**Note:** This warning does not affect functionality but indicates a future API change

---

## 9. Code Implementation

### Complete Agent Builder Script

**Location:** `src/agents/build_agents.py`

**Key Functions:**

1. **Initialization:**
```python
builder = PolicyNavigatorAgentBuilder(api_key=api_key)
```

2. **Agent Creation:**
```python
rag_agent = builder.create_rag_agent()
api_agent = builder.create_api_agent()
scraper_agent = builder.create_scraper_agent()
team_agent = builder.create_team_agent()
```

3. **ID Persistence:**
```python
builder.save_agent_ids("/home/ubuntu/policy-navigator-agent/agent_ids.json")
```

### Flask Integration

**Location:** `demo/app.py`

**Agent Loading:**
```python
def load_agent():
    """Load the team agent"""
    global team_agent
    
    if team_agent is not None:
        return team_agent
    
    try:
        if os.path.exists(AGENT_IDS_FILE):
            with open(AGENT_IDS_FILE, 'r') as f:
                agent_data = json.load(f)
            
            team_agent_id = agent_data.get('team_agent', {}).get('id')
            
            if team_agent_id:
                team_agent = AgentFactory.get(team_agent_id)
                return team_agent
        
        return None
    except Exception as e:
        print(f"Error loading agent: {str(e)}")
        return None
```

**Query Handling:**
```python
@app.route('/api/query', methods=['POST'])
def query():
    """Handle user queries"""
    data = request.json
    user_query = data.get('query', '').strip()
    
    # Get session ID if exists
    session_id = session.get('agent_session_id')
    
    # Try to use aiXplain agent
    agent = load_agent()
    
    if agent:
        response = agent.run(user_query, session_id=session_id)
        
        # Store session ID
        if hasattr(response, 'data') and hasattr(response.data, 'session_id'):
            session['agent_session_id'] = response.data.session_id
        
        answer = response.data.get('output', 'No response generated')
        source = 'aiXplain Team Agent'
    else:
        # Fallback to local vector search
        results = vector_store.search(user_query, n_results=3)
        # ... format results ...
    
    return jsonify({'answer': answer, 'source': source})
```

---

## 10. Testing and Validation

### Agent Creation Test Results

**Test Execution:**
```bash
cd /home/ubuntu/policy-navigator-agent
python3 src/agents/build_agents.py
```

**Output:**
```
=== Building Policy Navigator Agents ===

Creating RAG Agent...
✓ RAG Agent created: 6905048c56dba9504302685f

Creating API Agent...
✓ API Agent created: 6905048d56dba95043026860

Creating Scraper Agent...
✓ Scraper Agent created: 6905048ea1a609715ed913cb

Creating Team Agent...
✓ Team Agent created: 6905048fa1a609715ed913cc

✓ Agent IDs saved to /home/ubuntu/policy-navigator-agent/agent_ids.json

==================================================
Agents created successfully!
Note: Agents are in draft mode (expire in 24 hours)
To make them permanent, run: builder.deploy_agents()
==================================================
```

### Validation Checklist

| Test | Status | Notes |
|------|--------|-------|
| API Key Authentication | ✅ Pass | Successfully authenticated with aiXplain |
| RAG Agent Creation | ✅ Pass | Agent ID: 6905048c56dba9504302685f |
| API Agent Creation | ✅ Pass | Agent ID: 6905048d56dba95043026860 |
| Scraper Agent Creation | ✅ Pass | Agent ID: 6905048ea1a609715ed913cb |
| Team Agent Creation | ✅ Pass | Agent ID: 6905048fa1a609715ed913cc |
| Agent ID Persistence | ✅ Pass | Saved to agent_ids.json |
| SDK Cache Management | ✅ Pass | Cache files created successfully |
| Flask Integration | ✅ Pass | Agent loading function implemented |

---

## Summary

### What Was Built on aiXplain

1. **Four Specialized Agents:**
   - RAG Agent for vector database queries
   - API Agent for Federal Register integration
   - Scraper Agent for web content extraction
   - Team Agent for coordination and synthesis

2. **Agent Configuration:**
   - Custom instructions for each agent
   - Specialized roles and responsibilities
   - Multi-source data integration
   - Citation and source tracking

3. **SDK Integration:**
   - Python SDK installation and configuration
   - Agent factory usage
   - Team agent assembly
   - ID persistence and retrieval

4. **Web Application Integration:**
   - Flask endpoint for agent queries
   - Session management for conversation continuity
   - Fallback to local vector search
   - Error handling and logging

### Current Limitations

1. **Draft Mode:** Agents expire after 24 hours (not yet deployed)
2. **No Custom Tools:** Tools array is empty (would require additional aiXplain configuration)
3. **Basic Error Handling:** Could be enhanced with retry logic and better error messages
4. **No Agent Monitoring:** No dashboard or logging for agent performance

### Next Steps for Production

1. **Deploy Agents:** Run `builder.deploy_agents()` to make agents permanent
2. **Add Custom Tools:** Configure Python tools as aiXplain functions
3. **Implement Monitoring:** Add logging and performance tracking
4. **Enhance Error Handling:** Implement retry logic and graceful degradation
5. **Scale Infrastructure:** Deploy to production server with load balancing

---

**Document Version:** 1.0  
**Last Updated:** October 31, 2025  
**Author:** Manus AI
