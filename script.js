document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selections ---
    const uploadContainer = document.getElementById('upload-container');
    const uploadInput = document.getElementById('pdf-upload');
    const resultsContainer = document.getElementById('results-container');
    const processingIndicator = document.getElementById('processing-indicator');
    const resultCardTemplate = document.getElementById('result-card-template');
    const themeSwitcher = document.getElementById('theme-switcher');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');

    // --- Theme Switcher Logic ---
    const setInitialTheme = () => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        sunIcon.classList.toggle('active-icon', savedTheme === 'light');
        moonIcon.classList.toggle('active-icon', savedTheme === 'dark');
    };
    
    themeSwitcher.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        sunIcon.classList.toggle('active-icon');
        moonIcon.classList.toggle('active-icon');
    });

    setInitialTheme(); // Set theme on page load

    // --- Drag and Drop Event Handlers ---
    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadContainer.classList.add('dragover');
    });

    uploadContainer.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadContainer.classList.remove('dragover');
    });

    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadContainer.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    // Handle file selection via click
    uploadInput.addEventListener('change', () => {
        if (uploadInput.files.length) {
            handleFiles(uploadInput.files);
        }
    });

    // --- Main File Handler ---
    async function handleFiles(files) {
        resultsContainer.innerHTML = ''; // Clear previous results
        processingIndicator.classList.remove('hidden');
        uploadContainer.classList.add('hidden');

        const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf');
        
        for (const file of pdfFiles) {
            try {
                const data = await processPdf(file);
                displayResult(data);
            } catch (error) {
                console.error(`Error processing ${file.name}:`, error);
                // Future improvement: display an error card to the user
            }
        }
        
        processingIndicator.classList.add('hidden');
        uploadContainer.classList.remove('hidden');
        uploadInput.value = ''; // Reset file input
    }

    // --- Core PDF Processing Logic ---
    async function processPdf(file) {
        const fileData = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: fileData }).promise;
        const metadata = await pdf.getMetadata();
        const pagesContent = [];

        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const text = textContent.items.map(item => item.str).join(' ');
            
            // Simple image detection
            const operatorList = await page.getOperatorList();
            const hasImages = operatorList.fnArray.includes(pdfjsLib.OPS.paintImageXObject);
            
            pagesContent.push({
                page_number: i,
                text: text,
                word_count: text.split(/\s+/).filter(Boolean).length,
                has_images: hasImages,
                headings: extractHeadings(text),
            });
        }
        
        const documentStructure = analyzeDocument(pagesContent);
        return buildOutputData(file, metadata, pagesContent, documentStructure);
    }
    
    // --- Helper functions to mimic Python script's analysis ---
    function extractHeadings(text) {
        const headings = [];
        const lines = text.split('\n').filter(line => line.trim().length > 0);
        
        lines.forEach((line, i) => {
            line = line.trim();
            // All caps lines
            if (line.length > 3 && line.length < 100 && line === line.toUpperCase() && !line.match(/\d/)) {
                headings.push({ text: line, type: 'uppercase', line_number: i + 1 });
            }
            // Numbered lines
            else if (line.match(/^\d+\.?\s+[A-Z]/)) {
                headings.push({ text: line, type: 'numbered', line_number: i + 1 });
            }
        });
        return headings.slice(0, 20); // Limit results
    }
    
    function analyzeDocument(pages) {
        const allText = pages.map(p => p.text).join(' ');
        const total_words = pages.reduce((sum, p) => sum + p.word_count, 0);
        
        // Keyword extraction
        const words = allText.toLowerCase().match(/\b[a-z]{4,}\b/g) || [];
        const wordFreq = words.reduce((acc, word) => {
            acc[word] = (acc[word] || 0) + 1;
            return acc;
        }, {});
        
        const commonWords = new Set(['this', 'that', 'with', 'from', 'have', 'will', 'they', 'been', 'said', 'each', 'which', 'their', 'about', 'other', 'were', 'more']);
        
        const sortedKeywords = Object.entries(wordFreq)
            .filter(([word]) => !commonWords.has(word))
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10)
            .map(([word, frequency]) => ({ word, frequency }));
            
        return {
            total_words: total_words,
            total_headings: pages.reduce((sum, p) => sum + p.headings.length, 0),
            pages_with_images: pages.filter(p => p.has_images).length,
            keywords: sortedKeywords,
            average_words_per_page: Math.round(total_words / pages.length) || 0,
        };
    }

    // Structures the final data object to be displayed
    function buildOutputData(file, metadata, pagesContent, documentStructure) {
        const info = metadata.info || {};
        return {
            document_info: {
                filename: file.name,
                processing_timestamp: new Date().toISOString(),
                metadata: {
                    title: info.Title || 'N/A',
                    author: info.Author || 'N/A',
                    subject: info.Subject || 'N/A',
                    creator: info.Creator || 'N/A',
                    producer: info.Producer || 'N/A',
                    page_count: pagesContent.length,
                    file_size_bytes: file.size,
                },
            },
            content_analysis: {
                structure: documentStructure,
                pages: pagesContent.map(p => ({
                    page_number: p.page_number,
                    word_count: p.word_count,
                    has_images: p.has_images,
                    heading_count: p.headings.length,
                    preview_text: p.text.substring(0, 200) + (p.text.length > 200 ? '...' : ''),
                })),
            },
            extracted_data: {
                headings: pagesContent.flatMap(p => p.headings),
                full_text: pagesContent.map(p => p.text).join('\n').substring(0, 10000), // Limit text
            },
        };
    }
    
    // --- DOM Manipulation to Display Results ---
    function displayResult(data) {
        const card = resultCardTemplate.content.cloneNode(true);
        const cardElement = card.querySelector('.result-card');
        
        card.querySelector('.filename').textContent = data.document_info.filename;
        
        // Populate Summary Tab
        const summaryTab = card.querySelector('#summary');
        const stats = data.content_analysis.structure;
        summaryTab.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item"><h3>Total Words</h3><p>${stats.total_words.toLocaleString()}</p></div>
                <div class="summary-item"><h3>Total Pages</h3><p>${data.document_info.metadata.page_count}</p></div>
                <div class="summary-item"><h3>Images Found</h3><p>${stats.pages_with_images}</p></div>
                <div class="summary-item"><h3>Headings Found</h3><p>${stats.total_headings}</p></div>
            </div>
            <h3 style="margin-top: 1.5rem;">Top Keywords</h3>
            <p>${stats.keywords.map(kw => `<span class="keyword-tag">${kw.word}</span>`).join('') || 'No significant keywords found.'}</p>
        `;
        
        // Populate Page Details Tab
        const detailsTab = card.querySelector('#details');
        detailsTab.innerHTML = `<div class="page-details">${data.content_analysis.pages.map(page => `
            <div class="page-item">
                <h4>Page ${page.page_number}</h4>
                <p><strong>Words:</strong> ${page.word_count} | <strong>Headings:</strong> ${page.heading_count} | <strong>Has Images:</strong> ${page.has_images ? '✔️' : '❌'}</p>
                <code class="preview-text">${page.preview_text || 'No text found.'}</code>
            </div>`).join('')}</div>`;
        
        // Populate Raw JSON Tab
        card.querySelector('.json-output').textContent = JSON.stringify(data, null, 2);
        
        // Tab switching logic
        const tabButtons = card.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                card.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.toggle('active', content.id === button.dataset.tab);
                });
            });
        });

        resultsContainer.appendChild(cardElement);
    }
});