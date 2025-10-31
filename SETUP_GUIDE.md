# 🛠️ Policy Navigator Agent - Setup Guide

This guide provides detailed instructions for setting up, running, and extending the Policy Navigator Agent. It is intended for developers who want to customize the agent, add new data sources, or integrate it into their own applications.

---

## 1. Project Structure

The repository is organized into the following directories:

```
/policy-navigator-agent
├── .env                # Environment variables (API keys)
├── agent_ids.json      # Stores IDs of created aiXplain agents
├── chroma_db/          # Local vector database (created after ingestion)
├── data/
│   ├── sample_policies/  # Sample CFR XML data
│   ├── __init__.py
│   ├── ingest_data.py    # Script to populate the vector database
│   └── vector_store.py   # Manages ChromaDB interactions
├── demo/
│   ├── templates/
│   │   └── index.html    # HTML for the web interface
│   ├── __init__.py
│   └── app.py            # Flask web application
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── build_agents.py # Script to create aiXplain agents
│   └── tools/
│       ├── __init__.py
│       ├── document_processor.py # Processes XML, TXT files
│       ├── federal_register_tool.py # Interacts with Federal Register API
│       └── url_scraper_tool.py # Scrapes content from URLs
├── README.md             # Main project documentation
├── requirements.txt      # Python dependencies
└── SETUP_GUIDE.md        # This file
```

---

## 2. Core Components

### Vector Database (`vector_store.py`)

*   **Technology**: [ChromaDB](https://www.trychroma.com/)
*   **Description**: Manages the creation, population, and querying of the local vector database. It handles document chunking, embedding, and semantic search.
*   **Key Functions**:
    *   `add_documents()`: Adds processed text and metadata to the collection.
    *   `search()`: Performs a semantic search on the vector store.
    *   `get_collection_stats()`: Returns the total number of indexed documents.

### Data Ingestion (`ingest_data.py`)

*   **Description**: The main script for populating the vector database. It uses the `DocumentProcessor` to parse files and the `VectorStore` to index them.
*   **Usage**:
    *   `python3 src/data/ingest_data.py`: Ingests data from the `data/sample_policies` directory.
    *   `python3 src/data/ingest_data.py --reset`: Clears the existing database before ingesting data.

### Custom Tools (`src/tools/`)

1.  **`document_processor.py`**: Parses CFR XML files and other text-based documents. Extracts structured data (title, section, content) and prepares it for indexing.
2.  **`federal_register_tool.py`**: A client for the Federal Register API. It can search for documents, check for recent rule changes, and retrieve specific regulatory information.
3.  **`url_scraper_tool.py`**: Uses `requests` and `BeautifulSoup` to scrape content from web pages. It is designed to extract the main text while filtering out boilerplate content like navigation bars and footers.

### aiXplain Agent Builder (`build_agents.py`)

*   **Description**: This script uses the `aixplain` SDK to create and configure the multi-agent system.
*   **Key Functions**:
    *   `create_rag_agent()`: Defines the agent responsible for querying the local vector store.
    *   `create_api_agent()`: Defines the agent for interacting with the Federal Register API.
    *   `create_team_agent()`: Assembles the specialized agents into a coordinated team.
*   **Output**: Creates `agent_ids.json`, which stores the unique IDs of the created agents for later use.

### Web Demo (`demo/app.py`)

*   **Technology**: [Flask](https://flask.palletsprojects.com/)
*   **Description**: A simple web application that provides an interface for interacting with the agent.
*   **Endpoints**:
    *   `/`: Main user interface.
    *   `/api/query`: Handles user questions and routes them to the agent.
    *   `/api/upload`: Manages file uploads for document ingestion.
    *   `/api/scrape`: Handles URL scraping requests.

---

## 3. Extending the Agent

### Adding New Data Sources

To add a new static data source (e.g., another set of CFR titles):

1.  Place the new data files (e.g., XML, TXT) in a new directory under `data/`.
2.  Modify `src/data/ingest_data.py` to point to the new directory and run the script.

To add a new real-time API:

1.  Create a new tool in `src/tools/` similar to `federal_register_tool.py`.
2.  Create a new specialized agent in `src/agents/build_agents.py` to use this tool.
3.  Add the new agent to the `TeamAgentFactory.create()` call in `build_agents.py`.

### Customizing Agent Instructions

The behavior of each agent is defined by the `instructions` passed to `AgentFactory.create()` in `build_agents.py`. You can modify these instructions to change an agent's personality, specialize its role further, or alter its response format.

### Deploying Agents Permanently

By default, agents created via the SDK are in "draft" mode and expire after 24 hours. To make them permanent, you need to deploy them.

Uncomment the `builder.deploy_agents()` call in `src/agents/build_agents.py` and re-run the script:

```python
# src/agents/build_agents.py

# ... (inside main function)

# Deploy agents to make them permanent
builder.deploy_agents()
```

---

## 4. Running in Production

The Flask development server is not suitable for production use. For a production deployment, use a production-ready WSGI server like Gunicorn or uWSGI.

**Example with Gunicorn:**

1.  Install Gunicorn:
    ```bash
    pip3 install gunicorn
    ```

2.  Run the application:
    ```bash
    cd demo
    gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
    ```

This will start the server on port 8000 with 4 worker processes.

---

## 5. API Reference (Flask App)

*   **`POST /api/query`**
    *   **Body**: `{"query": "Your question here"}`
    *   **Response**: `{"answer": "...", "source": "..."}`

*   **`POST /api/upload`**
    *   **Body**: `multipart/form-data` with a file attached.
    *   **Response**: `{"success": true, "message": "..."}`

*   **`POST /api/scrape`**
    *   **Body**: `{"url": "http://example.com"}`
    *   **Response**: `{"success": true, "message": "..."}`

*   **`GET /api/stats`**
    *   **Response**: `{"total_documents": 1234, ...}`
