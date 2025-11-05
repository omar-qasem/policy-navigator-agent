"""
Simple test Flask app to debug upload/scrape issues
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import tempfile

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.document_processor import DocumentProcessor
from src.tools.url_scraper_tool import URLScraperTool
from src.data.vector_store import VectorStore

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get absolute paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# Initialize tools
document_processor = DocumentProcessor()
url_scraper = URLScraperTool()
vector_store = VectorStore(persist_directory=CHROMA_DB_PATH)


@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_document():
    """Handle document uploads"""
    if request.method == 'OPTIONS':
        return '', 204
    
    print("Upload endpoint called")
    
    if 'file' not in request.files:
        print("No file in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    print(f"File received: {file.filename}")
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save file temporarily
        # Use tempfile.gettempdir() for cross-platform compatibility
        upload_dir = os.path.join(tempfile.gettempdir(), 'policy_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Use basename to handle Windows paths with backslashes
        safe_filename = os.path.basename(file.filename)
        filepath = os.path.join(upload_dir, safe_filename)
        file.save(filepath)
        print(f"File saved to: {filepath}")
        
        # Process document
        documents = document_processor.process_document(filepath, chunk=True)
        print(f"Processed {len(documents)} documents")
        
        if documents:
            # Add to vector store
            added = vector_store.add_documents(documents)
            print(f"Added {added} documents to vector store")
            
            return jsonify({
                'success': True,
                'message': f'Successfully processed and indexed {added} document sections',
                'filename': file.filename,
                'sections': added
            })
        else:
            return jsonify({'error': 'Could not extract content from document'}), 400
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST', 'OPTIONS'])
def scrape_url():
    """Handle URL scraping"""
    if request.method == 'OPTIONS':
        return '', 204
    
    print("Scrape endpoint called")
    
    data = request.json
    url = data.get('url', '').strip()
    print(f"URL to scrape: {url}")
    
    if not url:
        return jsonify({'error': 'URL cannot be empty'}), 400
    
    try:
        # Scrape URL
        result = url_scraper.scrape_url(url)
        print(f"Scrape result status: {result['status']}")
        
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
                    'is_government': result['is_government']
                }
            }
            
            # Chunk if content is long
            if len(result['content']) > 1000:
                chunks = document_processor.chunk_document(document)
                added = vector_store.add_documents(chunks)
            else:
                added = vector_store.add_documents([document])
            
            print(f"Added {added} sections to vector store")
            
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
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"Starting test server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
