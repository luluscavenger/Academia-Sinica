# Docling PDF Processing Toolkit

A comprehensive toolkit for extracting text and images from academic PDF papers using the Docling library, designed specifically for physics and scientific literature analysis.

## Overview

This toolkit provides two main functionalities:
1. **Text Extraction and Segmentation** - Extract structured text content from PDFs with automatic section detection
2. **Image Extraction** - Extract all images from PDFs with intelligent filtering and quality analysis

## Features

### Text Processing (`testing-text.py`)
- **Automatic Section Detection**: Identifies standard academic sections (Abstract, Introduction, Methodology, Results, etc.)
- **Content Segmentation**: Breaks down papers into structured paragraphs
- **Intelligent Filtering**: Handles references, figures, and technical content appropriately
- **Markdown Output**: Generates well-formatted reports with clear structure
- **Batch Processing**: Processes multiple papers simultaneously

### Image Extraction (`testing-images.py`)
- **Dual Extraction Method**: Uses both Docling and PyMuPDF for maximum coverage
- **Smart Filtering**: Automatically filters out small or low-quality images
- **Multiple Formats**: Supports PNG, JPEG, and other common image formats
- **Quality Analysis**: Analyzes image properties and characteristics
- **Batch Processing**: Processes multiple PDFs in one run

## Directory Structure

```
testing_docling/
├── README.md                                    # This documentation
├── testing-text.py                              # Text extraction tool
├── testing-images.py                            # Image extraction tool
├── paper1.pdf                                   # Sample physics paper
├── paper2.pdf                                   # Sample physics paper  
├── paper3.pdf                                   # Sample physics paper
├── extracted_papers/                            # Text extraction results
│   ├── paper1_text_segments.md                  # Structured text from paper1
│   ├── paper2_text_segments.md                  # Structured text from paper2
│   └── paper3_text_segments.md                  # Structured text from paper3
├── extracted_images/                            # Image extraction results
│   ├── paper1_page3_chart1.png                  # Images from paper1
│   ├── paper2_page1_img1.png                    # Images from paper2
│   ├── paper2_page3_img*.jpeg                   # Multiple images from paper2
│   ├── paper2_page7_img1.png                    # Additional images
│   ├── paper2_page8_img1.jpeg                   # Large scientific figures
│   └── paper3_page1_img1.png                    # Images from paper3

```

## Requirements

### Python Dependencies
```bash
pip install docling
pip install pymupdf  # For fallback image extraction
pip install pillow   # For image processing
pip install numpy    # For numerical operations
```

### System Requirements
- Python 3.7+
- CUDA support (optional, for accelerated processing)
- Sufficient disk space for extracted content

## Usage

### Text Extraction

Extract structured text content from all PDF papers:

```bash
python3 testing-text.py
```

**Output**: 
- Creates `extracted_papers/` directory
- Generates `{paper_name}_text_segments.md` for each paper
- Includes section-by-section breakdown with paragraph numbering
- Provides document statistics and processing metadata

**Features**:
- Automatic section detection for academic papers
- Intelligent paragraph segmentation
- Reference summarization
- Figure caption extraction
- Table description preservation

### Image Extraction

Extract all images from PDF papers:

```bash
python3 testing-images.py
```

**Output**:
- Creates `extracted_images/` directory
- Saves images with descriptive filenames: `{paper}_{page}_{img}.{format}`
- Filters out small or low-quality images (< 50x50 pixels)
- Provides detailed extraction logs

**Features**:
- Dual extraction method (Docling + PyMuPDF fallback)
- Smart image quality filtering
- Multiple format support
- Detailed image property analysis
- Batch processing with progress tracking

## Sample Output

### Text Extraction Results

Each paper generates a structured markdown file with:

```markdown
# Paper Text Segmentation Report: paper1.pdf

## Document Statistics
- **File:** `paper1.pdf`
- **Total Sections:** 6
- **Total Paragraphs:** 67

## Section Overview
| Section | Paragraphs |
|---------|------------|
| Introduction | 7 |
| Methodology | 12 |
| Results | 15 |
| Discussion | 8 |

## Paper Content by Sections

### Introduction
**1.** This paper presents a comprehensive analysis...
**2.** Previous studies have shown...
```

### Image Extraction Results

The tool extracts and catalogs images with detailed information:

```
📊 Processing Summary:
- paper1.pdf: 0 images (small images filtered)
- paper2.pdf: 11 images (charts, figures, diagrams)
- paper3.pdf: 1 image (large scientific figure)

Total: 12 images extracted
```

## Advanced Features

### Text Processing Capabilities

1. **Section Recognition**: Automatically identifies standard academic sections
2. **Content Classification**: Distinguishes between main content, references, and metadata
3. **Structure Preservation**: Maintains document hierarchy and organization
4. **Reference Handling**: Summarizes extensive reference lists
5. **Figure Integration**: Preserves figure captions and descriptions

### Image Processing Capabilities

1. **Quality Filtering**: Removes thumbnails, icons, and low-resolution images
2. **Format Detection**: Handles multiple image formats automatically
3. **Metadata Extraction**: Captures image properties and characteristics
4. **Fallback Processing**: Uses PyMuPDF when Docling detection fails
5. **Batch Optimization**: Efficient processing of multiple documents

## Technical Details

### Text Extraction Method
- **Primary Tool**: Docling Document Converter
- **Section Detection**: SectionHeaderItem identification with pattern matching
- **Content Processing**: Hierarchical text extraction with intelligent filtering
- **Output Format**: Structured Markdown with consistent formatting

### Image Extraction Method
- **Primary Method**: Docling-based image detection
- **Fallback Method**: PyMuPDF direct extraction
- **Quality Control**: Size and content-based filtering
- **Storage**: Organized by paper and page number

## Troubleshooting

### Common Issues

1. **No Images Extracted**
   - Check if PDF contains embedded images
   - Verify image size meets minimum requirements (50x50 pixels)
   - Some PDFs may have images as vector graphics (not extractable)

2. **Text Extraction Incomplete**
   - Ensure PDF is not password-protected
   - Check for proper encoding (UTF-8 recommended)
   - Some scanned PDFs may require OCR preprocessing

3. **Performance Issues**
   - Large PDFs may take several minutes to process
   - CUDA acceleration can improve processing speed
   - Consider processing papers individually for very large documents

### Error Handling

Both tools include comprehensive error handling:
- Individual file failures don't stop batch processing
- Detailed error messages with troubleshooting hints
- Graceful fallback methods for maximum reliability

## Sample Papers

The included sample papers represent typical academic physics literature:

- **paper1.pdf**: Neutrino astrophysics research (5 pages)
- **paper2.pdf**: Multi-messenger astrophysics study (15 pages)
- **paper3.pdf**: Ultra-high-energy cosmic ray analysis (8 pages)

These papers provide diverse content types including:
- Mathematical equations and formulas
- Scientific figures and charts
- Tables and data visualizations
- Reference lists and citations
- Author affiliations and metadata

## Output Analysis

### Text Segments
- **Format**: Markdown with clear section hierarchy
- **Structure**: Numbered paragraphs within identified sections
- **Metadata**: Document statistics and processing information
- **Quality**: Maintains scientific terminology and mathematical notation

### Extracted Images
- **Naming**: Descriptive filenames with paper, page, and image identifiers
- **Quality**: Automatic filtering of low-quality images
- **Formats**: Preserves original formats (PNG, JPEG, etc.)
- **Organization**: Grouped by source paper for easy reference

## Future Enhancements

Potential improvements for this toolkit:

1. **Formula Extraction**: OCR-based mathematical equation extraction
2. **Table Processing**: Structured table data extraction
3. **Cross-Reference Resolution**: Link figures, tables, and citations
4. **Multilingual Support**: Enhanced processing for non-English papers
5. **API Integration**: Web service interface for remote processing

## Contributing

To extend this toolkit:

1. **Text Processing**: Modify section patterns in `PaperTextSegmenter`
2. **Image Filtering**: Adjust quality thresholds in image processing functions
3. **Output Formats**: Add support for additional export formats
4. **Error Handling**: Enhance robustness for edge cases

## License

This toolkit is designed for academic and research purposes. Please ensure compliance with copyright restrictions when processing proprietary documents.

---

**Version**: 1.0  
**Last Updated**: August 2025  
**Compatibility**: Python 3.7+, Docling 2.x  
**Dependencies**: See requirements section above
