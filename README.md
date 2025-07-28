# PDF Processing Solution - Adobe India Hackathon 2025

## Overview

This is a production-ready PDF processing solution for Challenge 1a of the Adobe India Hackathon 2025. The solution extracts structured data from PDF documents and outputs comprehensive JSON files containing document metadata, content analysis, and extracted data.

## Features

### Core Functionality
- **Automatic PDF Discovery**: Processes all PDF files from the input directory
- **Metadata Extraction**: Extracts document properties, creation dates, author information
- **Content Analysis**: Analyzes document structure, word counts, and content distribution
- **Table Detection**: Identifies and extracts tabular data from PDF pages
- **Heading Recognition**: Detects potential headings using multiple pattern matching strategies
- **Image Detection**: Identifies pages containing images
- **Keyword Extraction**: Analyzes content to identify key themes and topics

### Technical Features
- **Memory Efficient**: Optimized for large PDFs with controlled memory usage
- **Concurrent Processing**: Multi-threaded processing for improved performance
- **Error Handling**: Robust error handling with detailed logging
- **Structured Output**: Well-organized JSON output with clear hierarchy
- **Performance Monitoring**: Built-in timing and performance metrics

## Architecture

### Libraries Used
- **pdfplumber (0.10.3)**: Primary PDF processing library for text and table extraction
- **PyPDF2 (3.0.1)**: Metadata extraction and document information
- **concurrent.futures**: Multi-threaded processing for performance optimization
- **pathlib**: Modern file path handling
- **logging**: Comprehensive logging system

### Design Decisions

1. **Dual Library Approach**: Uses both pdfplumber and PyPDF2 to leverage the strengths of each
   - pdfplumber: Superior text and table extraction
   - PyPDF2: Reliable metadata extraction

2. **Memory Management**: Implements several memory optimization strategies:
   - Limits text extraction per page (5000 chars)
   - Restricts table data (10 rows max)
   - Limits full document text (10000 chars)
   - Controls heading extraction (20 max)

3. **Performance Optimization**:
   - Concurrent processing with controlled thread pool
   - Page limit (50 pages) for very large documents
   - Efficient text processing algorithms

## Docker Configuration

### Build Command
```bash
docker build --platform linux/amd64 -t pdf-processor .
```

### Run Command
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none pdf-processor
```

## Output Format

### JSON Structure
Each processed PDF generates a JSON file with the following structure:

```json
{
  "document_info": {
    "filename": "document.pdf",
    "processing_timestamp": "2025-01-15 10:30:45",
    "metadata": {
      "title": "Document Title",
      "author": "Author Name",
      "subject": "Document Subject",
      "creator": "Creator Application",
      "producer": "PDF Producer",
      "creation_date": "Creation Date",
      "modification_date": "Last Modified",
      "page_count": 25,
      "file_size_bytes": 1048576
    }
  },
  "content_analysis": {
    "structure": {
      "total_words": 5000,
      "total_tables": 3,
      "total_headings": 15,
      "pages_with_images": 5,
      "keywords": [
        {"word": "technology", "frequency": 45},
        {"word": "solution", "frequency": 32}
      ],
      "average_words_per_page": 200
    },
    "pages": [
      {
        "page_number": 1,
        "word_count": 250,
        "has_images": true,
        "table_count": 1,
        "heading_count": 2,
        "preview_text": "First 200 characters of page content..."
      }
    ]
  },
  "extracted_data": {
    "tables": [
      {
        "table_id": 1,
        "rows": 5,
        "columns": 3,
        "data": [["Header1", "Header2", "Header3"], ["Data1", "Data2", "Data3"]]
      }
    ],
    "headings": [
      {
        "text": "CHAPTER 1: INTRODUCTION",
        "type": "uppercase",
        "line_number": 15
      }
    ],
    "full_text": "Complete extracted text (first 10000 characters)..."
  }
}
```

## Performance Specifications

### Compliance with Challenge Requirements
- ✅ **Execution Time**: Optimized for ≤10 seconds per 50-page PDF
- ✅ **Model Size**: No ML models used, only lightweight text processing
- ✅ **Network Access**: No internet connectivity required during execution
- ✅ **CPU Architecture**: Fully compatible with AMD64 architecture
- ✅ **Memory Usage**: Designed to stay well within 16GB RAM limit
- ✅ **Open Source**: All dependencies are open source libraries

### Performance Optimizations
- Multi-threaded processing for multiple PDFs
- Memory-efficient streaming processing
- Intelligent content limiting to prevent memory issues
- Optimized regex patterns for heading detection
- Efficient table extraction algorithms

## Testing

### Local Testing
```bash
# Build the image
docker build --platform linux/amd64 -t pdf-processor .

# Test with sample data
mkdir -p input output
cp your_pdfs/*.pdf input/
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none pdf-processor
```

### Performance Testing
The solution has been tested with:
- Simple text-only PDFs
- Complex multi-column layouts
- Documents with tables and images
- Large documents (50+ pages)
- Various PDF formats and creators

## Error Handling

The solution includes comprehensive error handling:
- Invalid PDF file handling
- Memory limit protection
- Corrupted document recovery
- Network isolation compliance
- Detailed logging for debugging

## Logging

The application provides detailed logging including:
- Processing start/completion times
- Individual file processing status
- Error details with context
- Performance metrics
- Memory usage indicators

## Scalability

The solution is designed to handle:
- Multiple PDF files simultaneously
- Large document collections
- Various PDF formats and structures
- Different content types (text, tables, images)

## Future Enhancements

Potential improvements for production use:
- OCR integration for scanned documents
- Advanced NLP for content categorization
- Machine learning models for document classification
- Enhanced table structure recognition
- Image content analysis

## Support

For questions or issues related to this solution:
1. Check the detailed logging output
2. Verify input directory permissions
3. Ensure Docker platform compatibility
4. Review memory and performance constraints

---

*This solution is optimized for the Adobe India Hackathon 2025 Challenge 1a requirements and demonstrates production-ready PDF processing capabilities within the specified constraints.*