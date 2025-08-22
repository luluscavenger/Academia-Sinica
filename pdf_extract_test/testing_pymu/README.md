# PDF Analysis and Extraction Toolkit

A comprehensive toolkit for extracting and analyzing content from scientific PDF papers, with specialized focus on mathematical formulas, images, and text analysis.

## 🚀 Overview

This toolkit provides three main extraction and analysis capabilities:
- **Formula Extraction**: Extract numbered mathematical formulas like (1), (2), (3) from scientific papers
- **Image Extraction**: Extract high-quality charts, graphs, and figures from PDF documents  
- **Text Analysis**: Perform comprehensive text analysis with chapter segmentation and statistical insights

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
- [Output Structure](#output-structure)
- [Usage Examples](#usage-examples)
- [Requirements](#requirements)
- [Contributing](#contributing)

## ✨ Features

### 🔢 Mathematical Formula Extraction
- Extracts numbered formulas (1), (2), (3), etc. from scientific papers
- Supports LaTeX format detection
- Intelligent text filtering to avoid false positives
- Multiple extraction methods: PyMuPDF4LLM + PyMuPDF hybrid approach
- English output with professional formatting

### 🖼️ Advanced Image Extraction
- High-quality chart and graph extraction
- Smart graphics analysis for complex figures
- Embedded image object detection
- Quality scoring and filtering system
- Support for multi-panel figures
- Automatic file naming and organization

### 📊 Comprehensive Text Analysis
- Chapter and section segmentation
- Paragraph-level analysis
- Statistical text metrics
- Keyword extraction and frequency analysis
- Structured markdown output
- Multi-PDF batch processing

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup
1. Clone the repository and navigate to the toolkit directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Required Packages
- `pymupdf4llm`: Advanced PDF-to-markdown conversion
- `pymupdf`: PDF processing and image extraction
- `PyPDF2`: PDF text extraction
- `pdfplumber`: Enhanced PDF parsing
- `langchain-community`: Document processing
- `nltk`: Natural language processing
- `PIL`: Image processing
- `numpy`: Numerical computations

## 🚀 Quick Start

### Process All Sample Papers
The toolkit comes with three sample papers (`paper1.pdf`, `paper2.pdf`, `paper3.pdf`) for testing:

```bash
# Extract mathematical formulas
python testing_formulas.py

# Extract images and charts
python testing-images.py

# Perform text analysis
python testing-text.py
```

### Custom PDF Processing
Place your PDF files in the directory and modify the file lists in each script to process your own documents.

## 🔧 Tools Overview

### 1. Formula Extraction (`testing_formulas.py`)
**Purpose**: Extract numbered mathematical formulas from scientific papers

**Key Features**:
- Identifies formulas numbered as (1), (2), (3), etc.
- Uses PyMuPDF4LLM for markdown conversion
- Implements intelligent text filtering
- Generates detailed formula reports

**Output**: Markdown files in `testing-formula/` directory
- `paper1_formulas.md`
- `paper2_formulas.md` 
- `paper3_formulas.md`

### 2. Image Extraction (`testing-images.py`)
**Purpose**: Extract high-quality images, charts, and graphs from PDFs

**Key Features**:
- Smart graphics analysis algorithm
- Embedded image object detection
- Quality scoring (0-10 scale)
- Automatic chart boundary detection
- Multi-method extraction approach

**Output**: Image files in `testing-images/` directory
- Individual chart and figure files
- Organized by paper and page number
- PNG format with quality metadata

### 3. Text Analysis (`testing-text.py`)
**Purpose**: Comprehensive text analysis and chapter segmentation

**Key Features**:
- Intelligent chapter detection
- Paragraph-level segmentation
- Statistical analysis (word count, character count)
- Academic keyword extraction
- Structured markdown reporting

**Output**: Analysis files in `testing-text/` directory
- `paper1_text_analysis.md`
- `paper2_text_analysis.md`
- `paper3_text_analysis.md`

## 📁 Output Structure

```
testing_pymu/
├── testing-formula/          # Mathematical formulas
│   ├── paper1_formulas.md
│   ├── paper2_formulas.md
│   └── paper3_formulas.md
├── testing-images/           # Extracted images
│   ├── paper1_page2_chart1.png
│   ├── paper2_page3_obj1.png
│   └── ...
├── testing-text/            # Text analysis
│   ├── paper1_text_analysis.md
│   ├── paper2_text_analysis.md
│   └── paper3_text_analysis.md
└── output/                  # Legacy output directory
```

## 💻 Usage Examples

### Formula Extraction Example
```python
from testing_formulas import FormulaExtractor

extractor = FormulaExtractor()
results = extractor.extract_formulas_from_pdf("your_paper.pdf")
output_file = extractor.save_formulas_to_file("your_paper.pdf", results)
```

### Image Extraction Example
```python
from testing_images import PDFImageExtractor

extractor = PDFImageExtractor(output_dir="./my_images")
images = extractor.extract_images("your_paper.pdf")
```

### Text Analysis Example
```python
# Process single PDF
python testing-text.py

# The script automatically detects and processes paper1.pdf, paper2.pdf, paper3.pdf
# Generates comprehensive text analysis reports
```

## 📊 Sample Results

### Formula Extraction Results
- **Paper1**: No numbered formulas found (correctly identified)
- **Paper2**: 6 mathematical formulas extracted with smart filtering
- **Paper3**: 8 mathematical formulas extracted with proper sequencing

### Image Extraction Results  
- **Paper1**: 2 high-quality charts (average quality: 9.25/10.0)
- **Paper2**: 17 images including charts and figures (average quality: 9.47/10.0)
- **Paper3**: 2 high-quality images (average quality: 10.00/10.0)

### Text Analysis Results
- Comprehensive chapter-by-chapter breakdown
- Statistical summaries with word/character counts
- Academic keyword identification
- Structured markdown output for easy reading

## 🔍 Quality Features

### Smart Formula Detection
- Filters out text descriptions mistaken for formulas
- Validates mathematical content using symbol recognition
- Supports Greek letters, mathematical operators, and complex expressions
- Sequential formula numbering verification

### Advanced Image Processing
- Quality scoring algorithm (0-10 scale)
- Color variance and edge detection analysis
- Automatic chart boundary expansion
- Support for multi-panel scientific figures

### Intelligent Text Processing
- Academic paper structure recognition
- Multiple PDF loading methods for robustness
- Header and section detection
- Content extraction optimization

## 🛡️ Error Handling

The toolkit includes comprehensive error handling:
- File existence validation
- PDF corruption detection
- Graceful degradation when extraction fails
- Detailed error reporting and logging

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings to new functions
- Include error handling for new features
- Test with sample PDF files before submitting

## 📄 License

This project is part of the AI Literature Agent toolkit. Please refer to the main repository for licensing information.

## 🆘 Support

For issues, questions, or feature requests, please create an issue in the main repository or contact the development team.

---

**Last Updated**: August 22, 2025  
**Version**: 1.0.0  
**Compatibility**: Python 3.8+
