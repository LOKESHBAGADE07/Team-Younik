📄 PDF Analyzer - Web Edition
A modern, browser-based PDF analysis tool inspired by Challenge 1a of the Adobe India Hackathon 2025. This solution has been re-imagined as a fully client-side web application, meaning no files are ever uploaded to a server. All processing happens securely and instantly in your browser.

The application allows users to drag and drop PDF files to extract comprehensive JSON data, including document metadata, content analysis, and structured text.

✨ Features
Entirely Client-Side: Maximum privacy and security. Your files are never sent over the network.

Modern User Interface: A clean, responsive interface with a beautiful dark mode.

Drag & Drop Upload: Easily add multiple PDF files at once with a user-friendly drag-and-drop zone.

Instant Processing: Leverages the power of the browser for fast analysis without server-side delays.

Comprehensive Analysis:

Metadata Extraction: Extracts title, author, subject, creation dates, and file properties.

Content Analysis: Calculates word counts, identifies pages with images, and analyzes content distribution.

Heading Recognition: Detects potential headings using pattern matching.

Keyword Extraction: Identifies key themes and topics from the document's content.

Structured JSON Output: View the well-organized JSON output directly in a dedicated tab for easy inspection or copying.

🚀 Technology Stack
This project has transitioned from a Python/Docker backend to a lightweight, high-performance front-end solution.

Core Library: PDF.js (by Mozilla)

The world's most popular web-based PDF rendering and parsing engine. It provides robust, safe, and reliable PDF processing directly in the browser, eliminating the need for server-side dependencies like pdfplumber or PyPDF2.

HTML5: For the core structure and semantics of the application.

CSS3: For all styling, including the responsive layout, animations, and the light/dark theme switcher.

Vanilla JavaScript (ES6+): For all application logic, including file handling, DOM manipulation, and orchestrating the analysis with PDF.js. No heavy frameworks are used, ensuring the application is fast and lightweight.

💻 How to Use
Running this web application is incredibly simple. No builds, no dependencies, no Docker.

Clone the Repository:

git clone [https://github.com/your-username/your-repository.git](https://github.com/LOKESHBAGADE07/Team-Younik)

Open the HTML File:
Navigate into the cloned folder and open the index.html file in any modern web browser (like Chrome, Firefox, or Edge).

cd your-repository
# Double-click index.html in your file explorer

Analyze your PDFs:
Drag and drop your PDF files onto the upload area or click to select them using the file picker. The results will appear instantly.

📊 Output Format
The generated JSON structure remains comprehensive and is now created dynamically by the JavaScript in your browser.

{
  "document_info": {
    "filename": "document.pdf",
    "processing_timestamp": "2025-09-08T08:15:00.123Z",
    "metadata": {
      "title": "Document Title",
      "author": "Author Name",
      "page_count": 25,
      "file_size_bytes": 1048576
    }
  },
  "content_analysis": {
    "structure": {
      "total_words": 5000,
      "pages_with_images": 5,
      "total_headings": 15,
      "keywords": [
        {"word": "technology", "frequency": 45}
      ]
    },
    "pages": [
      {
        "page_number": 1,
        "word_count": 250,
        "has_images": true,
        "heading_count": 2,
        "preview_text": "First 200 characters of page content..."
      }
    ]
  },
  "extracted_data": {
    "headings": [
      {"text": "CHAPTER 1: INTRODUCTION", "type": "uppercase"}
    ],
    "full_text": "Complete extracted text (first 10000 characters)..."
  }
}

💡 Key Design Decisions
Privacy First: Shifting to a 100% client-side model was a deliberate choice to guarantee user privacy. This is a significant advantage over solutions that require file uploads.

Zero Dependencies: By using Vanilla JavaScript and a CDN-hosted library, there is no need for npm install or complex build steps. This makes the project universally accessible.

User Experience: Significant effort was invested in creating a clean, intuitive, and aesthetically pleasing interface, including features like dark mode and smooth animations, to make the tool a pleasure to use.

🔮 Future Enhancements
While the current version is fully functional, here are some potential improvements:

Export to File: Add a button to download the generated JSON data as a .json file.

Data Visualization: Use a library like Chart.js to create charts based on the content analysis (e.g., words per page).

OCR for Scanned PDFs: Integrate a client-side OCR library (like Tesseract.js) to handle image-based PDFs.

Advanced Search: Implement a search functionality to find keywords within the full extracted text.
