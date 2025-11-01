# CourtListener API Integration Guide

This document provides a comprehensive guide to the CourtListener API integration in the Policy Navigator Agent. This integration allows the agent to search for and analyze US court cases, providing valuable legal context for government regulations.

## 1. Overview

The CourtListener integration adds a powerful new capability to the Policy Navigator Agent: the ability to query a massive database of federal and state court opinions. This is crucial for understanding how regulations are interpreted, challenged, and upheld in the legal system.

### Key Features:

- **Case Law Search:** Search for court opinions related to specific regulations, keywords, or legal concepts.
- **Regulation Challenge Analysis:** Automatically check if a regulation has been challenged in court and summarize the outcomes.
- **API & Fallback Modes:** The system can use the official CourtListener API with an API key or a fallback mode with example data if no key is provided.

## 2. Technical Implementation

The integration consists of three main components:

1.  **`courtlistener_tool.py`**: A dedicated Python tool that handles all interactions with the CourtListener API.
2.  **`agent_manager.py`**: The agent manager is updated to include new skills for using the CourtListener tool.
3.  **`app_agent.py`**: The Flask application now has new API endpoints to expose the CourtListener functionality.

### `courtlistener_tool.py`

This is the core of the integration. It provides the following key methods:

| Method | Description |
| --- | --- |
| `search_opinions()` | Searches for court opinions based on a query. |
| `check_regulation_challenges()` | A high-level function that searches for cases challenging a specific regulation and summarizes the findings. |
| `get_case_details()` | Retrieves detailed information for a single case. |
| `format_for_agent()` | Formats the raw API results into a clean, human-readable string for the LLM or user. |

**Fallback Mechanism:** If no CourtListener API key is provided, the tool automatically enters a fallback mode. In this mode, it returns pre-defined example cases for demonstration purposes. This ensures the application remains functional even without API access.

### `agent_manager.py`

The agent manager now has two new skills:

- **`check_case_law(regulation, section)`**: This skill uses the `courtlistener_tool` to check for legal challenges to a regulation.
- **`search_court_cases(query)`**: This skill allows the agent to perform general searches for court cases.

The Team Agent can now autonomously decide to use these skills when a user's query relates to legal matters.

### `app_agent.py`

Three new API endpoints have been added to the Flask application:

- **`POST /api/courtlistener/check`**: Checks for challenges to a specific regulation.
- **`POST /api/courtlistener/search`**: Performs a general search for court cases.
- **`GET /api/courtlistener/status`**: Checks the status of the CourtListener integration (API or fallback mode).

## 3. How to Use the Integration

There are two ways to use the CourtListener integration: directly via the new API endpoints or by asking the agent natural language questions.

### Direct API Usage

You can use a tool like `curl` or Postman to interact with the new endpoints.

**Example: Check for challenges to Section 230**

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"regulation": "Communications Decency Act", "section": "Section 230"}' \
     http://localhost:5001/api/courtlistener/check
```

This will return a JSON object with a summary of court cases that have challenged Section 230.

### Natural Language Queries

The Team Agent is now equipped to handle legal questions. You can ask questions like:

- "Has the Clean Air Act ever been challenged in court?"
- "Find court cases related to EPA emissions standards."
- "What was the outcome of *Massachusetts v. EPA*?"

The agent will automatically detect that these are legal queries and use the CourtListener tool to find the answer.

## 4. API Key Configuration (Optional)

While the integration works without an API key (using fallback data), it is highly recommended to obtain a free API key from CourtListener for real-time data.

1.  **Get a free API key** from the [CourtListener API Information Page](https://www.courtlistener.com/api/rest-info/).
2.  **Add the API key** to your `.env` file:

    ```
    COURTLISTENER_API_KEY=your_api_key_here
    ```

3.  **Update `courtlistener_tool.py`** to use the key:

    Find this line in `src/tools/courtlistener_tool.py`:

    ```python
    tool = CourtListenerTool()
    ```

    And change it to:

    ```python
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("COURTLISTENER_API_KEY")
    tool = CourtListenerTool(api_key=api_key)
    ```

The system will automatically use the API key if it's available.

## 5. Conclusion

The CourtListener integration significantly enhances the capabilities of the Policy Navigator Agent, transforming it from a simple document retrieval system into a powerful legal research assistant. This brings the project much closer to the goal of a comprehensive, multi-faceted regulatory intelligence platform.
