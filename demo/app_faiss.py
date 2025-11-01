"""
Policy Navigator Agent - Web Demo (FAISS Version)
Stable version for Windows + Python 3.9
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
from dotenv import load_dotenv
import aixplain.api.client as client

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


@app.route('/')
def index():
    """Main page"""
    try:
        stats = vector_store.get_collection_stats()
        if not stats:
            stats = {'total_documents': 0, 'collection_name': 'policy_documents', 'persist_directory': FAISS_DB_PATH, 'backend': 'FAISS'}
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        stats = {'total_documents': 0, 'collection_name': 'policy_documents', 'persist_directory': FAISS_DB_PATH, 'backend': 'FAISS'}
    
    return render_template('index.html', stats=stats)


@app.route('/api/query', methods=['POST'])
def query():
    """Handle user queries"""
    data = request.json
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Search vector database
        results = vector_store.search(user_query, n_results=3)
        
        if not results:
            return jsonify({
                'answer': 'No relevant information found in the database. Please try a different query or upload more documents.',
                'source': 'Vector Database',
                'query': user_query
            })
        
        # Combine top results for context
        context = "\n\n".join([
            f"Document {i+1} (from {r['metadata'].get('title', 'Unknown')}):\n{r['content'][:800]}"
            for i, r in enumerate(results)
        ])
        
        # Use aiXplain LLM to generate answer
        try:
            # Create prompt for LLM
            prompt = f"""You are a helpful assistant that answers questions about US government policies and regulations.

Question: {user_query}

Relevant policy documents:
{context}

Based on the above documents, provide a clear and concise answer to the question. If the documents don't contain enough information, say so.

Answer:"""
            
            # Use GPT-4 via aiXplain (asset ID for GPT-4)
            model = client.Model('6646261c6eb563165658bbb1')  # GPT-4o-mini on aiXplain
            response = model.run(prompt)
            
            if hasattr(response, 'data') and response.data:
                answer = response.data
            else:
                # Fallback to simple context if LLM fails
                answer = f"Based on the retrieved documents:\n\n{context[:1000]}..."
        
        except Exception as llm_error:
            print(f"LLM error: {str(llm_error)}")
            # Fallback to simple context
            answer = f"Based on the policy documents:\n\n{context[:1000]}...\n\n(Note: LLM processing unavailable, showing raw excerpts)"
        
        return jsonify({
            'answer': answer,
            'source': f"FAISS Vector Database ({len(results)} documents) + aiXplain LLM",
            'query': user_query,
            'num_results': len(results),
            'top_match': results[0]['metadata'].get('title', 'Unknown'),
            'confidence': f"{results[0]['score']:.2f}"
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
        
        if result['success']:
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


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'backend': 'FAISS',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("="*60)
    print("Policy Navigator Agent - FAISS Version")
    print("="*60)
    print(f"Server starting on http://localhost:{port}")
    print(f"Backend: FAISS (stable for Windows + Python 3.9)")
    print(f"Debug mode: {debug}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
