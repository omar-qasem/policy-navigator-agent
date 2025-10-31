"""
Document Processor Tool for Policy Navigator Agent
Processes CFR XML files, PDFs, and text documents for vector indexing
"""

import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import re


class DocumentProcessor:
    """Process policy documents and extract structured information"""
    
    def __init__(self):
        self.supported_formats = ['.xml', '.txt', '.pdf']
    
    def process_cfr_xml(self, xml_path: str) -> List[Dict[str, Any]]:
        """
        Parse CFR XML file and extract regulation sections
        
        Args:
            xml_path: Path to CFR XML file
            
        Returns:
            List of dictionaries containing regulation sections with metadata
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            sections = []
            
            # Extract title information
            title_num = self._extract_title_number(root)
            
            # Find all sections in the XML
            for section in root.findall('.//SECTION'):
                section_data = self._extract_section_data(section, title_num)
                if section_data:
                    sections.append(section_data)
            
            # If no SECTION tags, try alternative structure
            if not sections:
                sections = self._extract_alternative_structure(root, title_num)
            
            return sections
            
        except Exception as e:
            print(f"Error processing CFR XML: {str(e)}")
            return []
    
    def _extract_title_number(self, root: ET.Element) -> str:
        """Extract title number from XML root"""
        # Try different possible locations for title number
        title_elem = root.find('.//TITLENUM')
        if title_elem is not None and title_elem.text:
            # Extract number from text like "TITLE 40"
            match = re.search(r'\d+', title_elem.text)
            if match:
                return match.group()
        
        # Try alternative location
        title_elem = root.find('.//TITLE')
        if title_elem is not None:
            num = title_elem.get('number')
            if num:
                return num
        
        return "Unknown"
    
    def _extract_section_data(self, section: ET.Element, title_num: str) -> Dict[str, Any]:
        """Extract data from a SECTION element"""
        # Get section number
        sectno = section.find('.//SECTNO')
        section_num = sectno.text.strip() if sectno is not None else "Unknown"
        
        # Get section subject/title
        subject = section.find('.//SUBJECT')
        section_title = subject.text.strip() if subject is not None else ""
        
        # Get section content
        content_parts = []
        
        # Extract paragraphs
        for para in section.findall('.//P'):
            if para.text:
                content_parts.append(para.text.strip())
        
        # If no paragraphs, get all text
        if not content_parts:
            content_parts = [self._get_all_text(section)]
        
        content = "\n\n".join(content_parts)
        
        # Clean section number
        section_num_clean = re.sub(r'[§\s]', '', section_num).strip()
        
        return {
            'title': title_num,
            'section': section_num_clean,
            'section_title': section_title,
            'content': content,
            'full_text': f"{section_num} {section_title}\n\n{content}",
            'source': 'CFR',
            'metadata': {
                'title': title_num,
                'section': section_num_clean,
                'subject': section_title
            }
        }
    
    def _extract_alternative_structure(self, root: ET.Element, title_num: str) -> List[Dict[str, Any]]:
        """Try alternative XML structure if SECTION tags not found"""
        sections = []
        
        # Try to find PART elements
        for part in root.findall('.//PART'):
            part_num = part.find('.//PARTNO')
            part_num_text = part_num.text if part_num is not None else "Unknown"
            
            # Extract content from this part
            content = self._get_all_text(part)
            
            if content.strip():
                sections.append({
                    'title': title_num,
                    'section': part_num_text,
                    'section_title': f"Part {part_num_text}",
                    'content': content,
                    'full_text': f"Part {part_num_text}\n\n{content}",
                    'source': 'CFR',
                    'metadata': {
                        'title': title_num,
                        'part': part_num_text
                    }
                })
        
        return sections
    
    def _get_all_text(self, element: ET.Element) -> str:
        """Recursively extract all text from an XML element"""
        text_parts = []
        
        if element.text:
            text_parts.append(element.text.strip())
        
        for child in element:
            child_text = self._get_all_text(child)
            if child_text:
                text_parts.append(child_text)
            if child.tail:
                text_parts.append(child.tail.strip())
        
        return " ".join(text_parts)
    
    def process_text_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process plain text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            List containing document data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            
            return [{
                'title': filename,
                'section': '1',
                'section_title': filename,
                'content': content,
                'full_text': content,
                'source': 'uploaded_file',
                'metadata': {
                    'filename': filename,
                    'file_type': 'text'
                }
            }]
            
        except Exception as e:
            print(f"Error processing text file: {str(e)}")
            return []
    
    def chunk_document(self, document: Dict[str, Any], chunk_size: int = 1000, 
                      overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Split a document into smaller chunks for better retrieval
        
        Args:
            document: Document dictionary
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of document chunks
        """
        content = document['content']
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        chunk_num = 1
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(document, current_chunk, chunk_num))
                    chunk_num += 1
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(document, current_chunk, chunk_num))
        
        return chunks
    
    def _create_chunk(self, document: Dict[str, Any], content: str, chunk_num: int) -> Dict[str, Any]:
        """Create a chunk dictionary with metadata"""
        return {
            'title': document['title'],
            'section': document['section'],
            'section_title': document['section_title'],
            'content': content.strip(),
            'chunk_num': chunk_num,
            'source': document['source'],
            'metadata': {
                **document['metadata'],
                'chunk_num': chunk_num
            }
        }
    
    def process_document(self, file_path: str, chunk: bool = True) -> List[Dict[str, Any]]:
        """
        Main method to process any supported document type
        
        Args:
            file_path: Path to document
            chunk: Whether to chunk the document
            
        Returns:
            List of processed document sections/chunks
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.xml':
            documents = self.process_cfr_xml(file_path)
        elif ext == '.txt':
            documents = self.process_text_file(file_path)
        else:
            print(f"Unsupported file format: {ext}")
            return []
        
        # Optionally chunk documents
        if chunk:
            chunked_docs = []
            for doc in documents:
                if len(doc['content']) > 1000:
                    chunked_docs.extend(self.chunk_document(doc))
                else:
                    chunked_docs.append(doc)
            return chunked_docs
        
        return documents


def test_processor():
    """Test the document processor"""
    processor = DocumentProcessor()
    
    # Test with sample CFR file
    cfr_file = "/home/ubuntu/policy-navigator-agent/data/sample_policies/cfr-title40-vol1.xml"
    
    if os.path.exists(cfr_file):
        print(f"Processing {cfr_file}...")
        sections = processor.process_document(cfr_file, chunk=False)
        print(f"Extracted {len(sections)} sections")
        
        if sections:
            print("\nFirst section:")
            print(f"Title: {sections[0]['title']}")
            print(f"Section: {sections[0]['section']}")
            print(f"Subject: {sections[0]['section_title']}")
            print(f"Content length: {len(sections[0]['content'])} characters")
            print(f"Preview: {sections[0]['content'][:200]}...")
    else:
        print(f"File not found: {cfr_file}")


if __name__ == "__main__":
    test_processor()
