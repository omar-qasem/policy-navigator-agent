# 🏛️ Policy Navigator Agent

**A Multi-Agent RAG System for Navigating US Government Regulations**

This repository contains the source code and documentation for the Policy Navigator Agent, a sophisticated multi-agent Retrieval-Augmented Generation (RAG) system built on the **aiXplain platform**. The agent is designed to provide intelligent, accurate, and context-aware answers to questions about US government regulations, compliance policies, and public health guidelines.

It leverages a powerful combination of local vector search, real-time API integrations, and web scraping to deliver comprehensive insights into the complex landscape of federal policy.


---

## ✨ Key Features

The Policy Navigator Agent offers a robust set of features designed for researchers, legal professionals, compliance officers, and the general public.

| Feature                           | Description                                                                                                                                                            |
| :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Multi-Agent RAG System**        | A sophisticated architecture featuring specialized agents for document retrieval, real-time data queries, and web scraping, all coordinated by a central team agent.   |
| **Vector-Indexed Knowledge Base** | A rich, locally-hosted vector database containing over 3,100 sections of the Code of Federal Regulations (CFR), powered by ChromaDB for fast semantic search.          |
| **Real-time API Integration**     | Connects to the **Federal Register API** to fetch the latest rule changes, proposed regulations, and executive orders, ensuring information is always up-to-date.      |
| **Dynamic Document Ingestion**    | Users can expand the agent's knowledge base by uploading their own policy documents (XML, TXT, or PDF) or providing a public URL for on-the-fly scraping and indexing. |
| **Interactive Web Demo**          | A user-friendly web interface built with Flask that provides a localhost-capable environment for querying the agent, uploading files, and scraping URLs.               |
| **Comprehensive Documentation**   | Includes a detailed setup guide, API reference, and architecture overview to facilitate easy deployment and extension.                                                 |

---

## 🏗️ System Architecture

The agent employs a multi-agent architecture where each component has a specialized role. This modular design, orchestrated by a **Team Agent** on the aiXplain platform, ensures efficient query handling and allows for easy scalability.

1. **Coordinator / Team Agent**: The central brain of the system. It analyzes user queries and routes them to the most appropriate specialized agent. It is responsible for synthesizing responses from multiple sources to provide a single, comprehensive answer.

2. **RAG Agent (Retrieval Agent)**: This agent queries the local **ChromaDB** vector database. It is optimized for semantic search over thousands of indexed policy documents to find relevant historical context and established regulations.

3. **API Agent**: This agent connects to external, real-time data sources like the **Federal Register API**. It is tasked with finding the latest policy updates, proposed rules, and other time-sensitive information that may not yet be in the static knowledge base.

4. **Scraper Agent**: This agent is responsible for ingesting new information from the web. It can process user-provided URLs to extract and index content from government websites, or be directed to find and download specific policy documents.

This division of labor allows the Policy Navigator to combine the breadth of a large, indexed knowledge base with the depth of real-time information, providing users with a complete and accurate picture of US regulations.

---

## 📚 Data Sources

The agent is pre-loaded with a comprehensive set of US government regulations and has the capability to connect to several more.

| Source                                                                                                                    | Type               | Description                                                                                                  | Status       |
| :------------------------------------------------------------------------------------------------------------------------ | :----------------- | :----------------------------------------------------------------------------------------------------------- | :----------- |
| **Code of Federal Regulations (CFR)**                                                                                     | Static Dataset     | Over 3,100 sections from **Title 40 (Protection of Environment)** are pre-indexed.                           | ✅ Indexed    |
| **Federal Register API**                                                                                                  | Real-time API      | Provides daily updates on rules, proposed rules, and notices from federal agencies.                          | ✅ Integrated |
| **User-Uploaded Documents**                                                                                               | Dynamic Ingestion  | Supports `.xml`, `.txt`, and `.pdf` files for on-demand indexing.                                            | ✅ Enabled    |
| **Public Government URLs**                                                                                                | Dynamic Ingestion  | Scrapes and indexes content from any valid `.gov` or other public URL.                                       | ✅ Enabled    |
| **[CFR Title 2, Volume 1 (2025)](https://www.govinfo.gov/content/pkg/CFR-2025-title2-vol1/pdf/CFR-2025-title2-vol1.pdf)** | Static PDF         | Contains **Title 2 – Grants and Agreements**, 2025 edition, published by the Office of the Federal Register. | ✅ Added      |
| **CourtListener API**                                                                                                     | Future Integration | Planned integration for retrieving federal and state court opinions related to regulations.                  | 🚧 Planned   |

---

## 🚀 Setup and Installation

Follow these steps to run the Policy Navigator Agent on your local machine.

### Prerequisites

* Python 3.10+
* `pip` for package management
* An **aiXplain API Key**

### 1. Clone the Repository

```bash
gh repo clone <your-github-username>/policy-navigator-agent
cd policy-navigator-agent
```

### 2. Install Dependencies

Create a virtual environment and install the required Python packages.

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root and add your aiXplain API key.

```env
# /home/ubuntu/policy-navigator-agent/.env

AIXPLAIN_API_KEY=your_aixplain_api_key_here
```

### 4. Ingest Initial Data

The repository includes a sample dataset from CFR Title 40. Run the ingestion script to populate the local vector database.

```bash
python3 src/data/ingest_data.py --reset
```

This will create a `chroma_db` directory in the project root containing the indexed documents.

To include additional datasets like **CFR Title 2, Volume 1 (2025)**, you can download and ingest it manually using:

```bash
python3 src/data/ingest_data.py --file https://www.govinfo.gov/content/pkg/CFR-2025-title2-vol1/pdf/CFR-2025-title2-vol1.pdf
```

---

## 📺 Demo Video

You can watch a short demo of the **Policy Navigator Agent** in action here:

🎥 **[View Demo on Google Drive](https://drive.google.com/file/d/1ZZLisO6f5Payq5BZktxGZ2u7pnBOzWJ6/view?usp=sharing)**

---

## Usage

Once the web demo is running, you can interact with the agent in several ways:

* **Ask a Question**: Type a question into the main text area and click "Submit Query."
* **Upload a Document**: Click the upload area to select a local `.xml`, `.txt`, or `.pdf` file. The agent will process and index its content.
* **Extract from URL**: Enter a public URL and click "Extract Content." The agent will scrape the page and add its text to the knowledge base.
