"""
Policy Navigator Agent - Multi-Agent Version
Uses aiXplain Team Agent for autonomous decision-making and tool selection
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get absolute path to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.data.faiss_vector_store import FAISSVectorStore
from src.tools.document_processor import DocumentProcessor
from src.tools.federal_register_tool import FederalRegisterTool
from src.tools.url_scraper_tool import URLScraperTool
from src.agents.agent_manager import AgentManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize tools
document_processor = DocumentProcessor()
federal_register = FederalRegisterTool()
url_scraper = URLScraperTool()

# FAISS database path
FAISS_DB_PATH = os.path.join(PROJECT_ROOT, "faiss_db")

# Initialize FAISS vector store
print("Initializing FAISS vector store...")
vector_store = FAISSVectorStore(persist_directory=FAISS_DB_PATH)
print("✓ FAISS vector store ready")

# Initialize Agent Manager
print("\nInitializing aiXplain Agent Manager...")
try:
    agent_manager = AgentManager()
    print("✓ Agent Manager ready")
    agent_status = agent_manager.get_agent_status()
    print(f"Agent Status: {agent_status}")
except Exception as e:
    print(f"✗ Agent Manager initialization failed: {str(e)}")
    print("  Falling back to LLM-only mode")
    agent_manager = None


@app.route('/')
def index():
    """Main page"""
    try:
        stats = vector_store.get_collection_stats()
        if not stats:
            stats = {'total_documents': 0, 'collection_name': 'policy_documents', 'persist_directory': FAISS_DB_PATH, 'backend': 'FAISS'}
        
        # Add agent status to stats
        if agent_manager:
            stats['agent_mode'] = 'Multi-Agent System'
            stats['agents'] = agent_manager.get_agent_status()
        else:
            stats['agent_mode'] = 'LLM Only'
            stats['agents'] = {}
            
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        stats = {'total_documents': 0, 'collection_name': 'policy_documents', 'persist_directory': FAISS_DB_PATH, 'backend': 'FAISS', 'agent_mode': 'Unknown'}
    
    return render_template('index.html', stats=stats)


@app.route('/api/query', methods=['POST'])
def query():
    """Handle user queries using Team Agent"""
    data = request.json
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Step 1: Search vector database for relevant documents
        results = vector_store.search(user_query, n_results=3)
        
        if not results:
            # No documents found, let agent handle it
            if agent_manager:
                agent_response = agent_manager.query(user_query)
                
                if agent_response['success']:
                    return jsonify({
                        'answer': agent_response['answer'],
                        'source': f"Team Agent (No documents found)",
                        'query': user_query,
                        'mode': 'agent_only'
                    })
                else:
                    return jsonify({
                        'answer': 'No relevant information found in the database. Please try a different query or upload more documents.',
                        'source': 'Vector Database',
                        'query': user_query,
                        'mode': 'no_results'
                    })
            else:
                return jsonify({
                    'answer': 'No relevant information found in the database. Please try a different query or upload more documents.',
                    'source': 'Vector Database',
                    'query': user_query,
                    'mode': 'no_results'
                })
        
        # Step 2: Use Team Agent with retrieved context
        if agent_manager:
            try:
                # Prepare context for agent
                context = {
                    'documents': results,
                    'query': user_query
                }
                
                # Query Team Agent
                agent_response = agent_manager.query(user_query, context=context)
                
                if agent_response['success']:
                    return jsonify({
                        'answer': agent_response['answer'],
                        'source': f"Multi-Agent RAG System ({len(results)} documents retrieved)",
                        'query': user_query,
                        'num_results': len(results),
                        'top_match': results[0]['metadata'].get('title', 'Unknown'),
                        'confidence': f"{results[0]['score']:.2f}",
                        'mode': 'multi_agent',
                        'agent': agent_response.get('agent', 'Team Agent')
                    })
                else:
                    # Agent failed, fall back to simple context
                    context_text = "\n\n".join([
                        f"Document {i+1} (from {r['metadata'].get('title', 'Unknown')}):\n{r['content'][:800]}"
                        for i, r in enumerate(results)
                    ])
                    
                    return jsonify({
                        'answer': f"Based on the policy documents:\n\n{context_text[:1000]}...\n\n(Note: Agent processing failed, showing raw excerpts)",
                        'source': f"FAISS Vector Database ({len(results)} documents)",
                        'query': user_query,
                        'num_results': len(results),
                        'mode': 'fallback',
                        'error': agent_response.get('error')
                    })
            
            except Exception as agent_error:
                print(f"Agent error: {str(agent_error)}")
                # Fall back to simple context
                context_text = "\n\n".join([
                    f"Document {i+1} (from {r['metadata'].get('title', 'Unknown')}):\n{r['content'][:800]}"
                    for i, r in enumerate(results)
                ])
                
                return jsonify({
                    'answer': f"Based on the policy documents:\n\n{context_text[:1000]}...\n\n(Note: Agent unavailable, showing raw excerpts)",
                    'source': f"FAISS Vector Database ({len(results)} documents)",
                    'query': user_query,
                    'num_results': len(results),
                    'mode': 'fallback'
                })
        else:
            # No agent available, return simple context
            context_text = "\n\n".join([
                f"Document {i+1} (from {r['metadata'].get('title', 'Unknown')}):\n{r['content'][:800]}"
                for i, r in enumerate(results)
            ])
            
            return jsonify({
                'answer': f"Based on the policy documents:\n\n{context_text[:1000]}...",
                'source': f"FAISS Vector Database ({len(results)} documents)",
                'query': user_query,
                'num_results': len(results),
                'mode': 'no_agent'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save file temporarily
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)
        
        # Process based on file type
        if file.filename.endswith('.xml'):
            sections = document_processor.extract_cfr_sections(temp_path)
        elif file.filename.endswith('.txt'):
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            sections = [{'content': content, 'title': file.filename, 'section_number': '1'}]
        else:
            return jsonify({'error': 'Unsupported file type. Please upload XML or TXT files.'}), 400
        
        # Add to vector store
        documents = []
        for section in sections:
            documents.append({
                'content': section['content'],
                'metadata': {
                    'title': section.get('title', file.filename),
                    'section_number': section.get('section_number', 'N/A'),
                    'source': file.filename,
                    'type': 'uploaded'
                }
            })
        
        added = vector_store.add_documents(documents)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'message': f'Successfully processed and indexed {added} sections from {file.filename}',
            'sections': added
        })
    
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
        
        if result.get('status') == 'success' and result.get('content'):
            # Add to vector store
            documents = [{
                'content': result['content'],
                'metadata': {
                    'title': result.get('title', 'Scraped Content'),
                    'source': url,
                    'type': 'scraped'
                }
            }]
            
            added = vector_store.add_documents(documents)
            
            return jsonify({
                'message': f'Successfully scraped and indexed content from {url}',
                'sections': added,
                'title': result.get('title', 'Unknown')
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
        
        if not results:
            return jsonify({
                'message': 'No recent documents found in the Federal Register',
                'results': []
            })
        
        return jsonify({
            'message': f'Found {len(results)} recent documents',
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/courtlistener/check', methods=['POST'])
def check_case_law():
    """
    Check if a regulation has been challenged in court.
    
    Request body:
    {
        "regulation": "Clean Air Act",
        "section": "Section 111" (optional)
    }
    """
    data = request.json
    regulation = data.get('regulation', '').strip()
    section = data.get('section', '').strip() or None
    
    if not regulation:
        return jsonify({'error': 'Regulation name cannot be empty'}), 400
    
    try:
        # Use agent manager if available
        if agent_manager:
            result = agent_manager.check_case_law(regulation, section)
            
            if result['success']:
                return jsonify({
                    'status': 'success',
                    'regulation': regulation,
                    'section': section,
                    'data': result['data'],
                    'formatted_answer': result['formatted'],
                    'source': result['source']
                })
            else:
                return jsonify({
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'source': result.get('source', 'CourtListener API')
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'error': 'Agent manager not available'
            }), 503
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/courtlistener/search', methods=['POST'])
def search_court_cases():
    """
    Search for court cases related to a query.
    
    Request body:
    {
        "query": "Section 230",
        "limit": 10 (optional)
    }
    """
    data = request.json
    query = data.get('query', '').strip()
    limit = data.get('limit', 10)
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Use agent manager if available
        if agent_manager:
            result = agent_manager.search_court_cases(query, limit=limit)
            
            if result['success']:
                return jsonify({
                    'status': 'success',
                    'query': query,
                    'data': result['data'],
                    'formatted_answer': result['formatted'],
                    'source': result['source']
                })
            else:
                return jsonify({
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'source': result.get('source', 'CourtListener API')
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'error': 'Agent manager not available'
            }), 503
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/courtlistener/status', methods=['GET'])
def courtlistener_status():
    """Check CourtListener tool status"""
    try:
        if agent_manager and hasattr(agent_manager, 'courtlistener_tool'):
            return jsonify({
                'status': 'available',
                'mode': 'fallback' if agent_manager.courtlistener_tool.use_fallback else 'api',
                'note': 'Using example cases (API key required for real data)' if agent_manager.courtlistener_tool.use_fallback else 'Connected to CourtListener API'
            })
        else:
            return jsonify({
                'status': 'unavailable',
                'error': 'CourtListener tool not initialized'
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/agent/status')
def agent_status():
    """Get agent system status"""
    if agent_manager:
        return jsonify({
            'available': True,
            'agents': agent_manager.get_agent_status(),
            'mode': 'Multi-Agent System'
        })
    else:
        return jsonify({
            'available': False,
            'agents': {},
            'mode': 'LLM Only'
        })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'backend': 'FAISS',
        'agent_system': agent_manager is not None,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("="*60)
    print("Policy Navigator - Multi-Agent RAG System")
    print("="*60)
    print(f"Server starting on http://localhost:{port}")
    print(f"Backend: FAISS Vector Store")
    if agent_manager:
        print(f"Agent System: ✓ Multi-Agent (Team Agent)")
        print(f"Team Agent ID: {AgentManager.TEAM_AGENT_ID}")
    else:
        print(f"Agent System: ✗ Fallback to LLM Only")
    print(f"Debug mode: {debug}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
