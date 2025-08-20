# AI Physics Paper Analysis System

An intelligent self-evaluation system for analyzing physics papers using OpenAI's GPT-4 model. This system employs a dual-role approach with Generator and Reviewer components to automatically extract summaries, keywords, and provide quality assessments with iterative improvement.

## Overview

The AI Physics Paper Analysis System is designed to automatically analyze physics research papers and generate structured outputs including:

- **Key Findings**: 5 bullet-point summaries of the paper's main contributions
- **Abstract**: A comprehensive 120-180 word abstract
- **Keywords**: 15-25 relevant physics-specific keywords
- **Quality Evaluation**: Automated scoring across 4 criteria with 0.5-point increments
- **Automatic Result Storage**: Saves results to ArXiv-compatible filenames

## Features

### Core Functionality
- **Dual-Role AI System**: Generator creates content, Reviewer evaluates and suggests improvements
- **Iterative Optimization**: Automatic prompt improvement based on evaluation feedback
- **Intelligent Scoring**: 4-category evaluation system with 0.5-point increments (0.0-5.0 per category)
- **Auto-Save**: Automatically saves results to `{arxiv_id}sum&keyword.md` format
- **Multi-Encoding Support**: Reads files with various character encodings (UTF-8, Latin-1, GBK, Big5, etc.)

### Evaluation Criteria
1. **Summary Quality** (0-5.0 points): Accuracy and completeness of key findings
2. **Keyword Relevance** (0-5.0 points): Relevance and specificity of extracted keywords
3. **Format Compliance** (0-5.0 points): Adherence to JSON output format
4. **Physics Terminology** (0-5.0 points): Correct usage of physics concepts and terms

**Total Score**: 20.0 points maximum

### Automated Workflow
- **Auto-run Threshold**: Continues optimization if score < threshold (default: 15.0/20.0)
- **Maximum Iterations**: Configurable iteration limit (default: 3)
- **Prompt Optimization**: AI-driven prompt improvement between iterations
- **Result Persistence**: Updates saved files with improved results

## Files Description

### `ai_converation.py`
**Main application file containing:**

- **AIEvaluationSystem Class**: Core system managing the evaluation cycle
- **Generator Functions**: Extract summaries, abstracts, and keywords from papers
- **Reviewer Functions**: Evaluate content quality with detailed scoring
- **File I/O Operations**: Read input files and save results
- **ArXiv Integration**: Extract ArXiv IDs from file paths for proper naming
- **Command-line Interface**: Support for both interactive and batch modes

**Key Functions:**
- `extract_arxiv_id_from_path()`: Extract ArXiv ID from file paths
- `save_summary_and_keywords()`: Save results to formatted markdown files
- `run_evaluation_cycle()`: Execute complete analysis and optimization cycle
- `generator_extract()`: Generate summaries and keywords
- `reviewer_evaluate()`: Evaluate and score generated content

### `prompt_config.json`
**Configuration file containing:**

- **Prompt Template**: Detailed instructions for the AI model
- **JSON Structure**: Expected output format specification
- **Analysis Guidelines**: Specific instructions for physics paper analysis
- **Quality Requirements**: Standards for summaries, abstracts, and keywords

**Purpose:**
- Stores the current optimized prompt for consistent analysis
- Updated automatically when the system improves prompts
- Ensures reproducible analysis quality across runs

## Installation & Requirements

### Prerequisites
```bash
pip install openai
```

### System Requirements
- Python 3.7+
- OpenAI API key
- Internet connection for API calls

## Usage

### Command Line Mode
```bash
# Basic usage
python3 ai_converation.py --api-key YOUR_API_KEY --file-path /path/to/paper.md

# With custom parameters
python3 ai_converation.py -k YOUR_API_KEY -f /path/to/paper.md -i 5 -t 18.0

# Show help
python3 ai_converation.py --help
```

### Interactive Mode
```bash
python3 ai_converation.py
```
The system will prompt for:
1. OpenAI API Key
2. File path to analyze

### Command Line Arguments
- `-k, --api-key`: OpenAI API Key (optional, will prompt if not provided)
- `-f, --file-path`: File path to analyze (optional, will prompt if not provided)
- `-i, --max-iterations`: Maximum iterations (default: 3)
- `-t, --auto-threshold`: Auto-run threshold score (default: 15.0, max: 20.0)
- `-v, --version`: Show version information

## Input/Output Examples

### Input File Path Examples
```
/home/user/AI_literature_agent-3/2110.01975/text.md
/path/to/research/2507.15389/source.html
/documents/2507.21856v1/paper.txt
```

### Generated Output Files
```
/home/user/AI_literature_agent-3/2110.01975sum&keyword.md
/path/to/research/2507.15389sum&keyword.md
/documents/2507.21856sum&keyword.md
```

### Output File Format
```markdown
# Summary & Keywords Report
**Generated on:** 2025-08-20 12:30:45
**Source File:** /path/to/input/file.md
**Evaluation Score:** 18.5/20.0

## Abstract
[Generated abstract here...]

## Key Findings
1. [First key finding]
2. [Second key finding]
3. [Third key finding]
4. [Fourth key finding]
5. [Fifth key finding]

## Keywords
**Total:** 20 keywords

- cosmic rays
- particle physics
- [additional keywords...]
```

## Workflow Process

1. **Input Processing**: Read and validate input file with multiple encoding support
2. **Initial Generation**: AI generates summary, abstract, and keywords
3. **Auto-Save**: Save initial results to ArXiv-formatted file
4. **Quality Review**: Reviewer evaluates content across 4 criteria
5. **Decision Logic**:
   - Score ≥ threshold → Ask user to continue or stop
   - Score < threshold → Automatically continue to next iteration
6. **Prompt Optimization**: AI improves prompt based on reviewer feedback
7. **Iteration**: Repeat process with improved prompt
8. **Final Save**: Update file with best results and final score

## Error Handling

- **API Connection**: Graceful handling of OpenAI API failures
- **File Encoding**: Automatic detection and handling of various file encodings
- **JSON Parsing**: Multiple fallback methods for parsing AI responses
- **Path Validation**: Verification of file existence and readability
- **Score Validation**: Ensures scores are within valid ranges (0.0-5.0 in 0.5 increments)

## Scoring System Details

### Valid Scores
Each criterion accepts scores in 0.5 increments: 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0

### Score Interpretation
- **5.0**: Excellent, meets all requirements perfectly
- **4.0-4.5**: Good quality with minor areas for improvement  
- **3.0-3.5**: Satisfactory but missing some important elements
- **2.0-2.5**: Needs improvement, some major issues
- **1.0-1.5**: Poor quality, significant problems
- **0.0-0.5**: Unacceptable, major fundamental issues

## Configuration

The system automatically manages its configuration through `prompt_config.json`. Manual editing is possible but not recommended as the AI system optimizes prompts automatically.

## Troubleshooting

### Common Issues
1. **API Key Error**: Ensure valid OpenAI API key with sufficient credits
2. **File Not Found**: Verify file path exists and is readable
3. **Encoding Error**: System attempts multiple encodings automatically
4. **Network Issues**: Check internet connection for API access
5. **JSON Parse Error**: System has multiple fallback parsing methods

### Debug Information
The system provides detailed console output including:
- File reading status and encoding used
- API call progress and response lengths
- Score validation and adjustment messages
- File save confirmation and paths

## Version Information
- **Version**: 2.0
- **Last Updated**: August 2025
- **Python Compatibility**: 3.7+
- **API Compatibility**: OpenAI GPT-4

---

For additional support or feature requests, please refer to the main project repository.
