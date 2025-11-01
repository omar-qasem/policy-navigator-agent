"""
Data ingestion script for FAISS vector store
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.faiss_vector_store import FAISSVectorStore
from src.tools.document_processor import DocumentProcessor


def ingest_cfr_data(vector_store_path: str = "./faiss_db", reset: bool = False):
    """
    Ingest CFR data into FAISS vector store
    
    Args:
        vector_store_path: Path to FAISS database
        reset: Whether to reset the database
    """
    print("="*60)
    print("FAISS Data Ingestion - Policy Navigator Agent")
    print("="*60)
    print()
    
    # Initialize vector store
    vs = FAISSVectorStore(persist_directory=vector_store_path)
    
    if reset:
        print("Resetting vector store...")
        vs.delete_collection()
        vs = FAISSVectorStore(persist_directory=vector_store_path)
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Process CFR XML file
    cfr_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "sample", "CFR-2024-title40.xml"
    )
    
    if not os.path.exists(cfr_file):
        print(f"✗ CFR file not found: {cfr_file}")
        print("  Please ensure the sample data is downloaded.")
        return
    
    print(f"Processing: {cfr_file}")
    print()
    
    # Extract sections
    sections = processor.extract_cfr_sections(cfr_file)
    print(f"✓ Extracted {len(sections)} sections from CFR")
    print()
    
    # Prepare documents for ingestion
    documents = []
    for section in sections:
        documents.append({
            'content': section['content'],
            'metadata': {
                'title': section['title'],
                'section_number': section['section_number'],
                'source': 'CFR Title 40',
                'type': 'regulation'
            }
        })
    
    # Add to vector store in batches
    batch_size = 100
    total_added = 0
    
    print(f"Ingesting {len(documents)} documents in batches of {batch_size}...")
    print()
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        added = vs.add_documents(batch)
        total_added += added
        print(f"  Batch {i//batch_size + 1}: Added {added} documents (Total: {total_added})")
    
    print()
    print("="*60)
    print(f"✓ Ingestion complete! Total documents: {total_added}")
    
    # Show stats
    stats = vs.get_collection_stats()
    print(f"✓ Backend: {stats['backend']}")
    print(f"✓ Total documents in database: {stats['total_documents']}")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest policy data into FAISS vector store')
    parser.add_argument('--reset', action='store_true', help='Reset the vector store before ingestion')
    parser.add_argument('--path', type='str', default='./faiss_db', help='Path to FAISS database')
    
    args = parser.parse_args()
    
    ingest_cfr_data(vector_store_path=args.path, reset=args.reset)
