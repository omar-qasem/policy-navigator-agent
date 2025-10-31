"""
Policy Navigator Agent - Web Demo
Flask application with localhost capability
"""

from flask import Flask, render_template, request, jsonify, session
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.document_processor import DocumentProcessor
from src.tools.federal_register_tool import FederalRegisterTool
from src.tools.url_scraper_tool import URLScraperTool
from src.data.vector_store import VectorStore
from src.data.ingest_data import DataIngestion

# Import aiXplain
from aixplain.factories import AgentFactory, TeamAgentFactory

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize tools
document_processor = DocumentProcessor()
federal_register = FederalRegisterTool()
url_scraper = URLScraperTool()
vector_store = VectorStore(persist_directory="../chroma_db")
data_ingestion = DataIngestion(vector_store_path="../chroma_db")

# Load agent IDs
AGENT_IDS_FILE = "../agent_ids.json"
team_agent = None

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


@app.route('/')
def index():
    """Main page"""
    stats = vector_store.get_collection_stats()
    return render_template('index.html', stats=stats)


@app.route('/api/query', methods=['POST'])
def query():
    """Handle user queries"""
    data = request.json
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Get session ID if exists
        session_id = session.get('agent_session_id')
        
        # Try to use aiXplain agent first
        agent = load_agent()
        
        if agent:
            # Use aiXplain agent
            response = agent.run(user_query, session_id=session_id)
            
            # Store session ID
            if hasattr(response, 'data') and hasattr(response.data, 'session_id'):
                session['agent_session_id'] = response.data.session_id
            
            answer = response.data.get('output', 'No response generated')
            source = 'aiXplain Team Agent'
        else:
            # Fallback to local vector search
            results = vector_store.search(user_query, n_results=3)
            
            if results:
                answer = "Based on the policy documents:\n\n"
                for i, result in enumerate(results, 1):
                    metadata = result['metadata']
                    content = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
                    
                    answer += f"{i}. **{metadata.get('title', 'Unknown')} CFR § {metadata.get('section', 'Unknown')}** - {metadata.get('section_title', '')}\n\n"
                    answer += f"{content}\n\n"
                
                source = 'Local Vector Search'
            else:
                answer = "I couldn't find relevant information in the policy database. Please try rephrasing your question or check if the topic is covered in the indexed regulations."
                source = 'No results'
        
        return jsonify({
            'answer': answer,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Handle document uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save file temporarily
        upload_dir = '/tmp/policy_uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        
        # Process document
        documents = document_processor.process_document(filepath, chunk=True)
        
        if documents:
            # Add to vector store
            added = vector_store.add_documents(documents)
            
            return jsonify({
                'success': True,
                'message': f'Successfully processed and indexed {added} document sections',
                'filename': file.filename,
                'sections': added
            })
        else:
            return jsonify({'error': 'Could not extract content from document'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def scrape_url():
    """Handle URL scraping"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL cannot be empty'}), 400
    
    try:
        # Scrape URL
        result = url_scraper.scrape_url(url)
        
        if result['status'] == 'success':
            # Add to vector store
            document = {
                'title': result['title'],
                'section': '1',
                'section_title': result['title'],
                'content': result['content'],
                'source': 'scraped_url',
                'metadata': {
                    'url': url,
                    'is_government': result['is_government'],
                    'scraped_at': datetime.now().isoformat()
                }
            }
            
            # Chunk if content is long
            if len(result['content']) > 1000:
                chunks = document_processor.chunk_document(document)
                added = vector_store.add_documents(chunks)
            else:
                added = vector_store.add_documents([document])
            
            return jsonify({
                'success': True,
                'message': f'Successfully scraped and indexed content from {url}',
                'title': result['title'],
                'word_count': result['word_count'],
                'sections': added,
                'is_government': result['is_government']
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to scrape URL')}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/federal-register', methods=['POST'])
def check_federal_register():
    """Check Federal Register for updates"""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Search Federal Register
        results = federal_register.search_documents(query, per_page=5)
        
        documents = []
        for doc in results.get('results', []):
            documents.append({
                'title': doc.get('title', 'No title'),
                'document_number': doc.get('document_number', 'Unknown'),
                'publication_date': doc.get('publication_date', 'Unknown'),
                'type': doc.get('type', 'Unknown'),
                'url': doc.get('html_url', ''),
                'abstract': doc.get('abstract', '')[:200] + '...' if doc.get('abstract') else ''
            })
        
        return jsonify({
            'success': True,
            'count': results.get('count', 0),
            'documents': documents
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = vector_store.get_collection_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Check if running in production or development
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("="*60)
    print("Policy Navigator Agent - Web Demo")
    print("="*60)
    print(f"Server starting on http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
