# ArXiv Paper Extraction Toolkit

This directory contains a comprehensive set of tools for extracting content from arXiv papers, supporting multiple formats and content analysis.

## 📁 File Descriptions

### Core Extraction Tools

#### `extract_pdf.py`
- **Purpose**: Text extractor for PDF format papers
- **Features**: 
  - Extracts text content from PDF files using PyMuPDF (fitz)
  - Intelligent paragraph segmentation based on position changes
  - Automatic detection of section headers (bold text)
  - Preserves formulas and special formatting integrity
  - Outputs formatted Markdown files

#### `extract_html.py`
- **Purpose**: Content extractor for HTML format papers
- **Features**:
  - Extracts paper content from arXiv HTML versions
  - Parses HTML structure using BeautifulSoup
  - Automatically downloads and processes embedded images
  - Converts HTML structure to Markdown format
  - Maintains section hierarchy and formatting

#### `extract_latex.py`
- **Purpose**: LaTeX source code processing tool
- **Features**:
  - Downloads and extracts arXiv LaTeX source (.tar files)
  - Converts PDF/EPS images to PNG format
  - Handles image format conversion (JPG → PNG)
  - Organizes LaTeX project structure
  - Preserves original LaTeX files for further processing

#### `extract_formula.py`
- **Purpose**: Specialized mathematical formula extractor
- **Features**:
  - Prioritizes text-based mathematical formula extraction
  - Supports LaTeX mathematical symbol conversion
  - Falls back to PNG image format when text extraction fails
  - Handles complex mathematical expressions
  - Generates formula Markdown files

#### `extract_summary.py`
- **Purpose**: Document structural analysis and summarization tool
- **Features**:
  - Analyzes Markdown file structure
  - Segments document content by section hierarchy
  - Creates structured document dictionaries
  - Generates independent section Markdown files
  - Supports multi-level heading parsing

### Testing and Utilities

#### `test.py`
- **Purpose**: Functionality testing and demonstration script
- **Features**:
  - Queries available resource formats for arXiv papers
  - Tests availability of PDF, HTML, LaTeX formats
  - Demonstrates usage of various extraction tools
  - Validates URL existence and accessibility

#### `requirements.txt`
- **Purpose**: Python dependency package list
- **Status**: Contains required packages for all extraction tools

### System Files

#### `__pycache__/` Directory
- **Purpose**: Python bytecode cache directory
- **Function**:
  - Stores compiled Python bytecode files (.pyc)
  - Accelerates Python module loading times
  - Auto-generated, no manual management required
- **File Format**: `module_name.cpython-version.pyc`
  - Example: `extract_pdf.cpython-312.pyc` (Python 3.12)
  - Example: `extract_html.cpython-39.pyc` (Python 3.9)
- **Explanation**: When Python first imports a module, it compiles the .py file to bytecode and caches it in this directory. Subsequent imports use the cached file directly, significantly improving execution speed.

## 🔧 Dependencies

The following packages are included in `requirements.txt`:
```
requests>=2.25.0
beautifulsoup4>=4.9.0
pymupdf>=1.23.0
pdfplumber>=0.7.0
pillow>=8.0.0
pandas>=1.3.0
arxiv>=1.4.0
pypandoc>=1.6.0
pathlib2>=2.3.0
```

## 🚀 Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test System**:
   ```python
   python test.py
   ```

3. **Extract Specific Formats**:
   ```python
   # Extract PDF
   from extract_pdf import extract_from_pdf
   
   # Extract HTML
   from extract_html import extract_from_html
   
   # Extract Formulas
   from extract_formula import ArxivFormulaExtractor
   
   # Process Summary
   from extract_summary import split_MD
   ```

## 💡 Example Usage

### Basic PDF Extraction
```python
from extract_pdf import extract_from_pdf

# Extract content from PDF
arxiv_id = "2507.21856"
pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
output_dir = f"./{arxiv_id}"

extract_from_pdf(pdf_url, output_dir)
```

### Formula Extraction
```python
from extract_formula import ArxivFormulaExtractor

# Extract formulas from paper
extractor = ArxivFormulaExtractor("2507.21856")
extractor.extract_all_formulas()
```

### Document Analysis
```python
from extract_summary import split_MD

# Analyze document structure
sections = split_MD("./2507.21856/text.md")
print(f"Found {len(sections)} sections")
```

## 📝 Notes

- Ensure stable internet connection for downloading arXiv resources
- Different paper formats may require different processing approaches
- Recommend using `test.py` first to check available formats for papers
- The `__pycache__` directory can be safely deleted; Python will regenerate it automatically
- Some papers may not be available in all formats (PDF/HTML/LaTeX)

## 🔍 Workflow Recommendation

1. **Check Format Availability**: Run `test.py` with target arXiv ID
2. **Choose Extraction Method**: Based on available formats and requirements
3. **Extract Content**: Use appropriate extractor tool
4. **Process Results**: Use `extract_summary.py` for structural analysis
5. **Extract Formulas**: Use `extract_formula.py` for mathematical content

## 🐛 Troubleshooting

- **Network Issues**: Check internet connection and arXiv server status
- **Missing Dependencies**: Run `pip install -r requirements.txt`
- **Format Not Available**: Try alternative formats (PDF → HTML → LaTeX)
- **Extraction Errors**: Check paper complexity and format quality