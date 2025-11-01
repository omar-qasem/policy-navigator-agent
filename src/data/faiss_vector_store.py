"""
FAISS Vector Store Manager for Policy Navigator Agent
Alternative to ChromaDB - more stable on Windows
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer


class FAISSVectorStore:
    """Manage vector database for policy documents using FAISS"""
    
    def __init__(self, persist_directory: str = "./faiss_db"):
        """
        Initialize FAISS vector store
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Initialize or load FAISS index
        self.index_path = os.path.join(persist_directory, "faiss.index")
        self.metadata_path = os.path.join(persist_directory, "metadata.pkl")
        
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self._load_index()
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.metadata = []
            self.id_counter = 0
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.id_counter = data['id_counter']
            print(f"Loaded FAISS index with {len(self.metadata)} documents")
        except Exception as e:
            print(f"Error loading index: {str(e)}")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.metadata = []
            self.id_counter = 0
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'id_counter': self.id_counter
                }, f)
            print(f"Saved FAISS index with {len(self.metadata)} documents")
        except Exception as e:
            print(f"Error saving index: {str(e)}")
    
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
        
        # Extract content and generate embeddings
        contents = [doc['content'] for doc in documents]
        embeddings = self.embedding_model.encode(contents, show_progress_bar=True)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store metadata
        for doc in documents:
            self.metadata.append({
                'id': self.id_counter,
                'content': doc['content'],
                'metadata': doc.get('metadata', {})
            })
            self.id_counter += 1
        
        # Save to disk
        self._save_index()
        
        return len(documents)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of matching documents with scores
        """
        if len(self.metadata) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search FAISS index
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), 
            min(n_results, len(self.metadata))
        )
        
        # Prepare results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                doc = self.metadata[idx]
                results.append({
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': float(1 / (1 + dist))  # Convert distance to similarity score
                })
        
        return results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        return {
            'total_documents': len(self.metadata),
            'collection_name': 'policy_documents',
            'persist_directory': self.persist_directory,
            'backend': 'FAISS'
        }
    
    def clear_all(self):
        """Clear all documents from the vector store"""
        try:
            # Reset index and metadata
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.metadata = []
            self.id_counter = 0
            
            # Save empty state to disk
            self._save_index()
            
            print("All documents cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing documents: {str(e)}")
            return False
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.metadata = []
            self.id_counter = 0
            print("Collection deleted successfully")
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")


if __name__ == "__main__":
    # Test the FAISS vector store
    print("Testing FAISS Vector Store...")
    
    store = FAISSVectorStore(persist_directory="./faiss_test_db")
    
    # Add test documents
    test_docs = [
        {
            'content': 'The EPA regulates air quality standards under the Clean Air Act.',
            'metadata': {'source': 'test', 'title': 'Air Quality'}
        },
        {
            'content': 'Water pollution is controlled by the Clean Water Act.',
            'metadata': {'source': 'test', 'title': 'Water Quality'}
        }
    ]
    
    added = store.add_documents(test_docs)
    print(f"Added {added} documents")
    
    # Search
    results = store.search("EPA air quality", n_results=2)
    print(f"\nSearch results for 'EPA air quality':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['content'][:100]}... (score: {result['score']:.3f})")
    
    # Stats
    stats = store.get_collection_stats()
    print(f"\nStats: {stats}")
    
    print("\n✓ FAISS Vector Store test completed successfully!")
