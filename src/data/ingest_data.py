"""
Data Ingestion Script for Policy Navigator Agent
Processes CFR data and populates the vector database
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.document_processor import DocumentProcessor
from data.vector_store import VectorStore
from typing import List, Dict, Any


class DataIngestion:
    """Handle data ingestion into vector database"""
    
    def __init__(self, vector_store_path: str = "./chroma_db"):
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore(persist_directory=vector_store_path)
    
    def ingest_cfr_file(self, file_path: str, chunk: bool = True) -> int:
        """
        Ingest a CFR XML file into the vector database
        
        Args:
            file_path: Path to CFR XML file
            chunk: Whether to chunk documents
            
        Returns:
            Number of documents added
        """
        print(f"Processing {file_path}...")
        
        # Process the document
        documents = self.processor.process_document(file_path, chunk=chunk)
        
        if not documents:
            print("No documents extracted")
            return 0
        
        print(f"Extracted {len(documents)} document sections")
        
        # Add to vector store
        added = self.vector_store.add_documents(documents)
        print(f"Added {added} documents to vector store")
        
        return added
    
    def ingest_directory(self, directory: str, pattern: str = "*.xml") -> int:
        """
        Ingest all files matching pattern from a directory
        
        Args:
            directory: Directory path
            pattern: File pattern to match
            
        Returns:
            Total number of documents added
        """
        import glob
        
        files = glob.glob(os.path.join(directory, pattern))
        
        if not files:
            print(f"No files found matching {pattern} in {directory}")
            return 0
        
        print(f"Found {len(files)} files to process")
        
        total_added = 0
        
        for file_path in files:
            added = self.ingest_cfr_file(file_path, chunk=True)
            total_added += added
        
        return total_added
    
    def ingest_text_content(self, content: str, title: str, metadata: Dict[str, Any]) -> int:
        """
        Ingest text content directly
        
        Args:
            content: Text content
            title: Document title
            metadata: Document metadata
            
        Returns:
            Number of documents added
        """
        document = {
            'title': title,
            'section': '1',
            'section_title': title,
            'content': content,
            'full_text': content,
            'source': metadata.get('source', 'manual'),
            'metadata': metadata
        }
        
        # Chunk if content is long
        if len(content) > 1000:
            chunks = self.processor.chunk_document(document)
            return self.vector_store.add_documents(chunks)
        else:
            return self.vector_store.add_documents([document])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return self.vector_store.get_collection_stats()
    
    def reset_database(self):
        """Reset the vector database"""
        self.vector_store.reset_collection()


def main():
    """Main ingestion process"""
    print("=== Policy Navigator Data Ingestion ===\n")
    
    # Initialize ingestion
    ingestion = DataIngestion(vector_store_path="/home/ubuntu/policy-navigator-agent/chroma_db")
    
    # Check if we should reset
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("Resetting vector database...")
        ingestion.reset_database()
        print()
    
    # Ingest sample CFR data
    sample_data_dir = "/home/ubuntu/policy-navigator-agent/data/sample_policies"
    
    if os.path.exists(sample_data_dir):
        print(f"Ingesting data from {sample_data_dir}...")
        total = ingestion.ingest_directory(sample_data_dir, "*.xml")
        print(f"\nTotal documents ingested: {total}")
    else:
        print(f"Sample data directory not found: {sample_data_dir}")
    
    # Show statistics
    print("\n=== Database Statistics ===")
    stats = ingestion.get_stats()
    print(f"Total documents: {stats.get('total_documents', 0)}")
    print(f"Collection: {stats.get('collection_name', 'unknown')}")
    print(f"Location: {stats.get('persist_directory', 'unknown')}")
    
    print("\n=== Ingestion Complete ===")


if __name__ == "__main__":
    main()
