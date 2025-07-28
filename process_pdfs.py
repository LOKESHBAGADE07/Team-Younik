#!/usr/bin/env python3
"""
PDF Processing Solution for Adobe India Hackathon 2025 - Challenge 1a
Extracts structured data from PDF documents and outputs JSON files.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import concurrent.futures
from dataclasses import dataclass

try:
    import pdfplumber
    import PyPDF2
except ImportError as e:
    print(f"Required library not found: {e}")
    print("Please install required dependencies")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    """Structure for document metadata"""
    title: str
    author: str
    subject: str
    creator: str
    producer: str
    creation_date: str
    modification_date: str
    page_count: int
    file_size: int

@dataclass
class PageContent:
    """Structure for individual page content"""
    page_number: int
    text: str
    word_count: int
    has_images: bool
    tables: List[Dict[str, Any]]
    headings: List[Dict[str, str]]

class PDFProcessor:
    """Main PDF processing class with optimized extraction methods"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def extract_metadata(self, pdf_path: Path) -> DocumentMetadata:
        """Extract metadata from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata or {}
                
                return DocumentMetadata(
                    title=str(metadata.get('/Title', '')).strip(),
                    author=str(metadata.get('/Author', '')).strip(),
                    subject=str(metadata.get('/Subject', '')).strip(),
                    creator=str(metadata.get('/Creator', '')).strip(),
                    producer=str(metadata.get('/Producer', '')).strip(),
                    creation_date=str(metadata.get('/CreationDate', '')).strip(),
                    modification_date=str(metadata.get('/ModDate', '')).strip(),
                    page_count=len(pdf_reader.pages),
                    file_size=pdf_path.stat().st_size
                )
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {pdf_path}: {e}")
            return DocumentMetadata('', '', '', '', '', '', '', 0, 0)
    
    def extract_headings(self, text: str) -> List[Dict[str, str]]:
        """Extract potential headings based on text patterns"""
        headings = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Pattern 1: All caps lines (potential headings)
            if line.isupper() and len(line) > 3 and len(line) < 100:
                headings.append({
                    'text': line,
                    'type': 'uppercase',
                    'line_number': i + 1
                })
            
            # Pattern 2: Lines with numbers (1., 2., etc.)
            elif re.match(r'^\d+\.?\s+[A-Z]', line):
                headings.append({
                    'text': line,
                    'type': 'numbered',
                    'line_number': i + 1
                })
            
            # Pattern 3: Short lines followed by content (potential titles)
            elif (len(line) < 50 and 
                  i < len(lines) - 1 and 
                  len(lines[i + 1].strip()) > 20 and
                  line[0].isupper()):
                headings.append({
                    'text': line,
                    'type': 'title',
                    'line_number': i + 1
                })
        
        return headings[:20]  # Limit to prevent memory issues
    
    def extract_tables(self, page) -> List[Dict[str, Any]]:
        """Extract table data from PDF page"""
        tables = []
        try:
            page_tables = page.extract_tables()
            for i, table in enumerate(page_tables):
                if table and len(table) > 1:  # Must have header + data
                    # Clean the table data
                    cleaned_table = []
                    for row in table:
                        if row and any(cell for cell in row if cell and str(cell).strip()):
                            cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                            cleaned_table.append(cleaned_row)
                    
                    if cleaned_table:
                        tables.append({
                            'table_id': i + 1,
                            'rows': len(cleaned_table),
                            'columns': len(cleaned_table[0]) if cleaned_table else 0,
                            'data': cleaned_table[:10]  # Limit rows to prevent memory issues
                        })
        except Exception as e:
            logger.debug(f"Table extraction failed: {e}")
        
        return tables
    
    def process_page(self, page, page_num: int) -> PageContent:
        """Process individual page and extract structured content"""
        try:
            # Extract text
            text = page.extract_text() or ''
            
            # Check for images
            has_images = len(page.images) > 0
            
            # Extract tables
            tables = self.extract_tables(page)
            
            # Extract headings
            headings = self.extract_headings(text)
            
            # Count words
            word_count = len(text.split()) if text else 0
            
            return PageContent(
                page_number=page_num,
                text=text[:5000],  # Limit text to prevent memory issues
                word_count=word_count,
                has_images=has_images,
                tables=tables,
                headings=headings
            )
            
        except Exception as e:
            logger.warning(f"Failed to process page {page_num}: {e}")
            return PageContent(page_num, '', 0, False, [], [])
    
    def extract_document_structure(self, pages_content: List[PageContent]) -> Dict[str, Any]:
        """Analyze document structure and create summary"""
        total_words = sum(page.word_count for page in pages_content)
        total_tables = sum(len(page.tables) for page in pages_content)
        total_headings = sum(len(page.headings) for page in pages_content)
        pages_with_images = sum(1 for page in pages_content if page.has_images)
        
        # Extract key themes (most common words)
        all_text = ' '.join(page.text for page in pages_content)
        words = re.findall(r'\b[A-Za-z]{4,}\b', all_text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords (excluding common words)
        common_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'said', 'each', 'which', 'their', 'time', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'also', 'back', 'after', 'use', 'her', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'number', 'part', 'sound', 'take', 'turn', 'want', 'place', 'year', 'back', 'give', 'most', 'very', 'after', 'thing', 'our', 'name', 'good', 'sentence', 'man', 'think', 'say', 'great', 'where', 'help', 'through', 'much', 'before', 'line', 'right', 'too', 'mean', 'old', 'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 'show', 'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end', 'why', 'again', 'turn', 'here', 'why', 'ask', 'went', 'men', 'read', 'need', 'land', 'different', 'home', 'us', 'move', 'try', 'kind', 'hand', 'picture', 'again', 'change', 'off', 'play', 'spell', 'air', 'away', 'animal', 'house', 'point', 'page', 'letter', 'mother', 'answer', 'found', 'study', 'still', 'learn', 'should', 'america', 'world'}
        
        keywords = []
        for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
            if word not in common_words and freq > 2:
                keywords.append({'word': word, 'frequency': freq})
                if len(keywords) >= 10:
                    break
        
        return {
            'total_words': total_words,
            'total_tables': total_tables,
            'total_headings': total_headings,
            'pages_with_images': pages_with_images,
            'keywords': keywords,
            'average_words_per_page': total_words // len(pages_content) if pages_content else 0
        }
    
    def process_single_pdf(self, pdf_path: Path, output_dir: Path) -> bool:
        """Process a single PDF file and generate JSON output"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing: {pdf_path.name}")
            
            # Extract metadata
            metadata = self.extract_metadata(pdf_path)
            
            # Process pages with pdfplumber
            pages_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                # Limit pages for performance (can process more if needed)
                max_pages = min(len(pdf.pages), 50)
                
                for page_num in range(max_pages):
                    page = pdf.pages[page_num]
                    page_content = self.process_page(page, page_num + 1)
                    pages_content.append(page_content)
            
            # Extract document structure
            document_structure = self.extract_document_structure(pages_content)
            
            # Create structured output
            output_data = {
                'document_info': {
                    'filename': pdf_path.name,
                    'processing_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'metadata': {
                        'title': metadata.title,
                        'author': metadata.author,
                        'subject': metadata.subject,
                        'creator': metadata.creator,
                        'producer': metadata.producer,
                        'creation_date': metadata.creation_date,
                        'modification_date': metadata.modification_date,
                        'page_count': metadata.page_count,
                        'file_size_bytes': metadata.file_size
                    }
                },
                'content_analysis': {
                    'structure': document_structure,
                    'pages': [
                        {
                            'page_number': page.page_number,
                            'word_count': page.word_count,
                            'has_images': page.has_images,
                            'table_count': len(page.tables),
                            'heading_count': len(page.headings),
                            'preview_text': page.text[:200] + '...' if len(page.text) > 200 else page.text
                        } for page in pages_content
                    ]
                },
                'extracted_data': {
                    'tables': [table for page in pages_content for table in page.tables],
                    'headings': [heading for page in pages_content for heading in page.headings],
                    'full_text': ' '.join(page.text for page in pages_content)[:10000]  # Limit for memory
                }
            }
            
            # Save JSON output
            output_file = output_dir / f"{pdf_path.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully processed {pdf_path.name} in {processing_time:.2f}s")
            
            self.processed_count += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            self.error_count += 1
            return False

def main():
    """Main processing function"""
    start_time = time.time()
    
    # Define directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Validate directories
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Process files with concurrent processing for better performance
    max_workers = min(4, len(pdf_files))  # Limit concurrent processing
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for pdf_file in pdf_files:
            future = executor.submit(processor.process_single_pdf, pdf_file, output_dir)
            futures.append(future)
        
        # Wait for all processing to complete
        concurrent.futures.wait(futures)
    
    # Summary
    total_time = time.time() - start_time
    logger.info(f"Processing complete!")
    logger.info(f"Successfully processed: {processor.processed_count} files")
    logger.info(f"Errors: {processor.error_count} files")
    logger.info(f"Total time: {total_time:.2f}s")
    logger.info(f"Average time per file: {total_time/len(pdf_files):.2f}s")

if __name__ == "__main__":
    main()