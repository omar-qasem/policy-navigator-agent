"""
Policy Navigator Agent - Web Demo (FAISS Version)
Stable version for Windows + Python 3.9
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os
import PyPDF2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get absolute path to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.data.faiss_vector_store import FAISSVectorStore
from src.tools.document_processor import DocumentProcessor
from src.tools.federal_register_tool import FederalRegisterTool
from src.tools.url_scraper_tool import URLScraperTool
from dotenv import load_dotenv
from aixplain.factories import ModelFactory

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


def generate_simple_answer(query, results):
    """
    Generate a simple answer from retrieved documents when LLM is unavailable.
    Uses basic text processing to extract relevant information.
    """
    if not results:
        return "I couldn't find any relevant information in the policy documents to answer your question."
    
    # Extract key sentences from top results
    answer_parts = []
    answer_parts.append(f"Based on the policy documents, here's what I found:\n")
    
    for i, result in enumerate(results[:3], 1):  # Use top 3 results
        title = result['metadata'].get('title', 'Unknown Document')
        content = result['content'][:500]  # First 500 chars
        
        # Clean up content
        content = content.replace('\n', ' ').strip()
        if len(content) > 400:
            content = content[:400] + "..."
        
        answer_parts.append(f"\n**Document {i}: {title}**\n{content}")
    
    answer_parts.append(f"\n\n*Note: This is a simplified answer. For more detailed analysis, please ensure the LLM service is available.*")
    
    return "\n".join(answer_parts)


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
        
        # Build context from top results with more content
        context = "\n\n".join([
            f"Document {i+1} (from {r['metadata'].get('title', 'Unknown')}):\n{r['content'][:2000]}"
            for i, r in enumerate(results)
        ])
        
        # Use aiXplain LLM to generate answer
        try:
            # Create improved prompt for LLM
            prompt = f"""You are an expert assistant specializing in US government policies and regulations.

IMPORTANT INSTRUCTIONS:
- Read the ENTIRE document content carefully, including disclaimers and restrictions
- Look for specific details, warnings, prohibitions, and requirements
- Quote relevant sections when available
- If information is found in the documents, provide a detailed answer
- Only say "information not found" if you've thoroughly checked all documents

Question: {user_query}

Relevant policy documents:
{context}

Provide a comprehensive answer based on the documents above. Include specific details, quotes, and citations when available.

Answer:"""
            
            # Use GPT-4o-mini via aiXplain
            from aixplain.factories import ModelFactory
            
            # Try to get GPT-4o-mini model
            try:
                model = ModelFactory.get('6646261c6eb563165658bbb1')  # GPT-4o-mini
                response = model.run(prompt)
                
                # Extract answer from response
                if hasattr(response, 'data'):
                    answer = response.data
                elif hasattr(response, 'text'):
                    answer = response.text
                elif isinstance(response, dict) and 'data' in response:
                    answer = response['data']
                elif isinstance(response, str):
                    answer = response
                else:
                    raise Exception(f"Unexpected response format: {type(response)}")
                    
            except Exception as model_error:
                print(f"Model error: {str(model_error)}")
                # Try alternative: use text completion with different model ID
                try:
                    # Try GPT-3.5-turbo as fallback
                    model = ModelFactory.get('openai/gpt-3.5-turbo')
                    response = model.run(prompt)
                    answer = response.data if hasattr(response, 'data') else str(response)
                except:
                    # If all else fails, generate a simple answer from context
                    answer = generate_simple_answer(user_query, results)
        
        except Exception as llm_error:
            print(f"LLM error: {str(llm_error)}")
            import traceback
            traceback.print_exc()
            # Generate simple answer from context
            answer = generate_simple_answer(user_query, results)
        
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
        elif file.filename.endswith('.pdf'):
            # Extract text from PDF
            with open(temp_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                content = ''
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    content += page.extract_text() + '\n'
            sections = [{'content': content, 'title': file.filename, 'section_number': '1'}]
        else:
            return jsonify({'error': 'Unsupported file type. Please upload XML, TXT, or PDF files.'}), 400
        
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


@app.route('/api/clear-all', methods=['POST'])
def clear_all_documents():
    """Clear all documents from the vector database"""
    try:
        success = vector_store.clear_all()
        
        if success:
            return jsonify({
                'message': 'All documents cleared successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Failed to clear documents'}), 500
    
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
