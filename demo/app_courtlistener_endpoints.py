"""
CourtListener API endpoints for Policy Navigator
Add these routes to your Flask app (app_agent.py or app_faiss.py)
"""

# Add this route to your Flask app:

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


# Example usage in your query endpoint:
"""
@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get('query', '').strip()
    
    # Detect if query is about case law
    case_law_keywords = ['challenged in court', 'court case', 'ruling', 'litigation', 'lawsuit']
    
    if any(keyword in user_query.lower() for keyword in case_law_keywords):
        # Extract regulation name from query
        # Simple extraction - you can make this more sophisticated
        regulation = user_query.split('about')[-1].strip('?').strip()
        
        # Check case law
        if agent_manager:
            result = agent_manager.check_case_law(regulation)
            if result['success']:
                return jsonify({
                    'answer': result['formatted'],
                    'source': 'CourtListener API + Multi-Agent RAG',
                    'query': user_query
                })
    
    # Continue with normal RAG query...
"""
