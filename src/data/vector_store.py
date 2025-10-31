"""
Vector Store Manager for Policy Navigator Agent
Handles document indexing and retrieval using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
import json


class VectorStore:
    """Manage vector database for policy documents"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize vector store
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="policy_documents",
            metadata={"description": "US Government policy and regulation documents"}
        )
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            
        Returns:
            Number of documents added
        """
        if not documents:
            return 0
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            # Generate unique ID
            doc_id = self._generate_id(doc, i)
            ids.append(doc_id)
            
            # Get text content
            text = doc.get('content', doc.get('full_text', ''))
            texts.append(text)
            
            # Prepare metadata
            metadata = {
                'title': str(doc.get('title', '')),
                'section': str(doc.get('section', '')),
                'section_title': str(doc.get('section_title', '')),
                'source': str(doc.get('source', 'unknown')),
            }
            
            # Add additional metadata if present
            if 'metadata' in doc and isinstance(doc['metadata'], dict):
                for key, value in doc['metadata'].items():
                    if key not in metadata:
                        metadata[key] = str(value)
            
            metadatas.append(metadata)
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            return len(documents)
        except Exception as e:
            print(f"Error adding documents to vector store: {str(e)}")
            return 0
    
    def _generate_id(self, doc: Dict[str, Any], index: int) -> str:
        """Generate a unique ID for a document"""
        title = doc.get('title', 'unknown')
        section = doc.get('section', 'unknown')
        chunk_num = doc.get('chunk_num', index)
        
        return f"{title}_{section}_{chunk_num}"
    
    def search(self, query: str, n_results: int = 5, 
              filter_metadata: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant documents with metadata and scores
        """
        try:
            # Build where clause for filtering
            where = filter_metadata if filter_metadata else None
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            formatted_results = []
            
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'id': results['ids'][0][i]
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching vector store: {str(e)}")
            return []
    
    def search_by_title(self, title: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents by CFR title
        
        Args:
            title: CFR title number (e.g., "40")
            n_results: Number of results to return
            
        Returns:
            List of documents from that title
        """
        return self.search(
            query="",
            n_results=n_results,
            filter_metadata={"title": title}
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            print(f"Error getting collection stats: {str(e)}")
            return {
                'total_documents': 0,
                'collection_name': 'policy_documents',
                'persist_directory': self.persist_directory
            }
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name="policy_documents")
            print("Collection deleted successfully")
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
    
    def reset_collection(self):
        """Reset the collection (delete and recreate)"""
        try:
            self.delete_collection()
            self.collection = self.client.get_or_create_collection(
                name="policy_documents",
                metadata={"description": "US Government policy and regulation documents"}
            )
            print("Collection reset successfully")
        except Exception as e:
            print(f"Error resetting collection: {str(e)}")
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for display
        
        Args:
            results: List of search results
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        output = []
        output.append(f"Found {len(results)} relevant documents:\n")
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            
            output.append(f"\n--- Result {i} ---")
            output.append(f"Title: {metadata.get('title', 'Unknown')}")
            output.append(f"Section: {metadata.get('section', 'Unknown')}")
            output.append(f"Subject: {metadata.get('section_title', 'Unknown')}")
            output.append(f"Source: {metadata.get('source', 'Unknown')}")
            if result['distance'] is not None:
                output.append(f"Relevance Score: {1 - result['distance']:.3f}")
            output.append(f"\nContent Preview:\n{content_preview}")
        
        return "\n".join(output)


def test_vector_store():
    """Test the vector store"""
    print("=== Testing Vector Store ===\n")
    
    # Initialize vector store
    store = VectorStore(persist_directory="./test_chroma_db")
    
    # Test 1: Add sample documents
    print("1. Adding sample policy documents...")
    sample_docs = [
        {
            'title': '40',
            'section': '1.1',
            'section_title': 'EPA Authority',
            'content': 'The Environmental Protection Agency has authority to regulate air quality standards under the Clean Air Act.',
            'source': 'CFR',
            'metadata': {'agency': 'EPA'}
        },
        {
            'title': '40',
            'section': '60.1',
            'section_title': 'Air Quality Standards',
            'content': 'Standards of performance for new stationary sources are established to protect public health and welfare.',
            'source': 'CFR',
            'metadata': {'agency': 'EPA'}
        },
        {
            'title': '21',
            'section': '1.1',
            'section_title': 'FDA Authority',
            'content': 'The Food and Drug Administration regulates food, drugs, and medical devices to ensure safety.',
            'source': 'CFR',
            'metadata': {'agency': 'FDA'}
        }
    ]
    
    added = store.add_documents(sample_docs)
    print(f"Added {added} documents")
    
    # Test 2: Get collection stats
    print("\n2. Collection statistics:")
    stats = store.get_collection_stats()
    print(json.dumps(stats, indent=2))
    
    # Test 3: Search for relevant documents
    print("\n3. Searching for 'air quality standards'...")
    results = store.search("air quality standards", n_results=2)
    print(store.format_search_results(results))
    
    # Test 4: Search by title
    print("\n4. Searching for documents in Title 40...")
    title_results = store.search_by_title("40", n_results=5)
    print(f"Found {len(title_results)} documents in Title 40")
    
    # Cleanup
    print("\n5. Cleaning up test database...")
    store.delete_collection()
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_vector_store()
