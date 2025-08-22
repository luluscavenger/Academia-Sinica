import re
import os
import sys
import PyPDF2
import pdfplumber
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader  # Fixed import path
from langchain.docstore.document import Document

# Add workspace root to path to import helper_functions
sys.path.append('/home/luluscavenger/AI_literature_agent-3')
try:
    from helper_functions import replace_t_with_space, replace_double_lines_with_one_line
except ImportError:
    # Fallback: define basic helper functions if not available
    def replace_t_with_space(text):
        return text.replace('\t', ' ')
    
    def replace_double_lines_with_one_line(text):
        return re.sub(r'\n+', '\n', text)

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter, defaultdict
from datetime import datetime

# Ensure nltk data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    print("✅ NLTK punkt data already exists")
except LookupError:
    print("⬇️ Downloading NLTK punkt data...")
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
    print("✅ NLTK punkt_tab data already exists")
except LookupError:
    print("⬇️ Downloading NLTK punkt_tab data...")
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
    print("✅ NLTK stopwords data already exists")
except LookupError:
    print("⬇️ Downloading NLTK stopwords data...")
    nltk.download('stopwords')

def extract_paragraph_beginnings(text, max_length=80):
    """
    Extract the beginning of each paragraph to validate paragraph segmentation
    """
    paragraphs = []
    seen_beginnings = set()
    
    # Split by double newlines for paragraph detection
    potential_paragraphs = text.split('\n\n')
    
    for paragraph in potential_paragraphs:
        paragraph_text = paragraph.strip()
        if len(paragraph_text) > 20:  # Ignore very short paragraphs
            beginning = paragraph_text[:max_length]
            if len(paragraph_text) > max_length:
                beginning += "..."
            
            if beginning not in seen_beginnings:
                paragraphs.append(beginning)
                seen_beginnings.add(beginning)
    
    # Also try sentence-based splitting for better paragraph detection
    sentences = sent_tokenize(text)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 30:  # Longer sentences are more likely to be paragraph starts
            beginning = sentence[:max_length]
            if len(sentence) > max_length:
                beginning += "..."
            
            if beginning not in seen_beginnings:
                paragraphs.append(beginning)
                seen_beginnings.add(beginning)
    
    return paragraphs[:10]  # Limit to first 10 paragraphs

def extract_paragraph_with_keywords(text, max_paragraphs=8):
    """
    Extract paragraph beginnings with associated keywords for each paragraph
    """
    paragraphs_with_keywords = []
    seen_beginnings = set()
    
    # Split by double newlines for paragraph detection
    potential_paragraphs = text.split('\n\n')
    
    for paragraph in potential_paragraphs:
        paragraph_text = paragraph.strip()
        if len(paragraph_text) > 30:  # Ignore very short paragraphs
            beginning = paragraph_text[:100]
            if len(paragraph_text) > 100:
                beginning += "..."
            
            if beginning not in seen_beginnings:
                # Extract keywords for this paragraph
                paragraph_keywords = extract_key_terms(paragraph_text, min_freq=1, max_terms=5)
                keyword_list = [f"{term}({freq})" for term, freq in list(paragraph_keywords.items())[:3]]
                
                paragraphs_with_keywords.append({
                    'beginning': beginning,
                    'keywords': keyword_list
                })
                seen_beginnings.add(beginning)
    
    return paragraphs_with_keywords[:max_paragraphs]

def extract_key_terms(text, min_freq=2, max_terms=20):
    """
    Extract key terms and technical vocabulary from text
    """
    # Tokenize and clean text
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    
    # Filter words: keep only meaningful terms
    filtered_words = []
    for word in words:
        if (len(word) > 3 and 
            word.isalpha() and 
            word not in stop_words and
            not word.isdigit()):
            filtered_words.append(word)
    
    # Count word frequencies
    word_freq = Counter(filtered_words)
    
    # Extract technical terms (often capitalized or contain specific patterns)
    technical_terms = []
    sentences = sent_tokenize(text)
    
    for sentence in sentences:
        # Find capitalized terms that might be technical
        capitalized_terms = re.findall(r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b', sentence)
        for term in capitalized_terms:
            if len(term) > 3 and term.lower() not in stop_words:
                technical_terms.append(term.lower())
    
    # Combine regular and technical terms
    all_terms = Counter(filtered_words + technical_terms)
    
    # Filter by frequency and return top terms
    key_terms = {term: freq for term, freq in all_terms.items() if freq >= min_freq}
    return dict(sorted(key_terms.items(), key=lambda x: x[1], reverse=True)[:max_terms])

def extract_important_sentences(text, key_terms, max_sentences=3):
    """
    Extract the most important sentences based on key term density
    """
    sentences = sent_tokenize(text)
    sentence_scores = []
    
    for sentence in sentences:
        score = 0
        sentence_lower = sentence.lower()
        sentence_words = word_tokenize(sentence_lower)
        
        # Score based on key terms
        for term, freq in key_terms.items():
            if term in sentence_lower:
                score += freq * 2  # Weight by term frequency
        
        # Bonus for sentence length (avoid too short sentences)
        if len(sentence_words) > 10:
            score += 1
        
        # Bonus for academic indicators
        academic_indicators = ['study', 'research', 'analysis', 'method', 'result', 'conclusion']
        for indicator in academic_indicators:
            if indicator in sentence_lower:
                score += 1
        
        sentence_scores.append((sentence, score))
    
    # Sort by score and return top sentences
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    return [sent for sent, score in sentence_scores[:max_sentences] if score > 0]

def generate_intelligent_summary(text, title="Section"):
    """
    Generate intelligent summary based on key terms and important sentences
    """
    if len(text.strip()) < 100:
        return f"**{title}**: Content too short for meaningful summary."
    
    # Extract key terms for the entire chapter
    key_terms = extract_key_terms(text)
    
    # Extract important sentences for overall summary
    important_sentences = extract_important_sentences(text, key_terms)
    
    # Extract paragraphs with their keywords
    paragraphs_with_keywords = extract_paragraph_with_keywords(text)
    
    # Generate summary
    summary_parts = []
    
    # Add title
    summary_parts.append(f"**{title}**")
    
    # Add overall key terms for the chapter
    if key_terms:
        terms_with_freq = [f"{term}({freq})" for term, freq in list(key_terms.items())[:5]]
        summary_parts.append(f"*Chapter Key Terms*: {', '.join(terms_with_freq)}")
    
    # Add paragraph analysis with keywords
    if paragraphs_with_keywords:
        summary_parts.append("*Paragraph Analysis*:")
        for i, para_info in enumerate(paragraphs_with_keywords, 1):
            beginning = para_info['beginning']
            keywords = para_info['keywords']
            
            # Format paragraph entry
            summary_parts.append(f"{i}. **Paragraph {i}**: {beginning}")
            if keywords:
                summary_parts.append(f"   *Keywords*: {', '.join(keywords)}")
            else:
                summary_parts.append(f"   *Keywords*: (no significant keywords)")
    
    # Add chapter summary based on important sentences
    if important_sentences:
        summary_parts.append("*Chapter Summary*:")
        for i, sentence in enumerate(important_sentences, 1):
            # Clean and truncate sentence if too long
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 200:
                clean_sentence = clean_sentence[:200] + "..."
            summary_parts.append(f"{i}. {clean_sentence}")
    else:
        # Fallback: use first and last sentences
        sentences = sent_tokenize(text)
        if len(sentences) >= 2:
            first_sentence = sentences[0].strip()
            last_sentence = sentences[-1].strip()
            if len(first_sentence) > 200:
                first_sentence = first_sentence[:200] + "..."
            if len(last_sentence) > 200:
                last_sentence = last_sentence[:200] + "..."
            summary_parts.append("*Chapter Overview*:")
            summary_parts.append(f"1. {first_sentence}")
            if first_sentence != last_sentence:
                summary_parts.append(f"2. {last_sentence}")
    
    return "\n".join(summary_parts)

def filter_url_from_chapters(text):
    """
    Filter out URLs and links from chapter text
    """
    url_patterns = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ]
    
    for pattern in url_patterns:
        if re.search(pattern, text):
            return False
    return True

def improve_two_column_reading_order(text):
    """
    Improve reading order for two-column PDFs
    """
    # Simple heuristic: if lines are very short, they might be from two columns
    lines = text.split('\n')
    improved_lines = []
    
    for line in lines:
        if len(line.strip()) > 0:
            improved_lines.append(line)
    
    return '\n'.join(improved_lines)

def extract_all_headers(text):
    """
    Extract all possible headers: bold, large font, all caps, etc.
    """
    headers = []
    
    # Various header patterns
    header_patterns = [
        # Academic paper standard format: number + all caps title
        (r'(?m)^\d+\s+[A-Z][A-Z\s]+[A-Z](?:\s*$|\s+[A-Z])', 'Academic Numbered Section'),
        # Pure all caps titles (like ABSTRACT, REFERENCES)
        (r'(?m)^[A-Z][A-Z\s]{3,}[A-Z](?:\s*$)', 'All Caps Title'),
        # Subsections: number.number format
        (r'(?m)^\d+\.\d+\s+[A-Z][A-Za-z\s]+', 'Subsection'),
        # Roman numeral titles
        (r'(?m)^[IVX]+\.\s+[A-Z][A-Za-z\s]+', 'Roman Numeral Title'),
        # Numbered titles with dots
        (r'(?m)^\d+\.\s+[A-Z][A-Za-z\s,.-]+$', 'Numbered Title'),
        # Common academic keywords
        (r'(?m)^(ABSTRACT|INTRODUCTION|METHODS|METHODOLOGY|RESULTS|DISCUSSION|CONCLUSION|ACKNOWLEDGEMENTS?|REFERENCES|APPENDIX|DATA AVAILABILITY|IMPLICATIONS)(?:\s*$)', 'Academic Keywords'),
    ]
    
    for pattern, pattern_type in header_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            line_start = text.rfind('\n', 0, match.start()) + 1
            line_end = text.find('\n', match.end())
            if line_end == -1:
                line_end = match.end() + 50
                
            full_line = text[line_start:line_end].strip()
            
            # ⭐ New: Filter URLs and links
            if not filter_url_from_chapters(full_line):
                print(f"   🚫 Skip URL/Link: {full_line[:50]}...")
                continue
            
            headers.append({
                'start': match.start(),
                'end': match.end(), 
                'text': full_line,
                'type': pattern_type,
                'line_start': line_start
            })
    
    # Sort by position and remove duplicates
    headers.sort(key=lambda x: x['start'])
    
    # Remove duplicate headers (based on position proximity)
    unique_headers = []
    for header in headers:
        if not unique_headers or abs(header['start'] - unique_headers[-1]['start']) > 10:
            unique_headers.append(header)
    
    return unique_headers

def split_into_chapters(pdf_path):
    """
    Use multiple PDF loading methods and intelligent header recognition
    Ensure chapter titles and content separation
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file does not exist: {pdf_path}")
    
    print(f"🔍 Starting PDF file processing...")
    print(f"📂 Using PDF file: {pdf_path}")
    
    # Get file size
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
    print(f"📊 File size: {file_size:.2f} MB")
    
    # Use PyPDF2 as the main loading method
    try:
        print(f"📖 Loading PDF file using PyPDF2: {pdf_path}")
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"📄 Total PDF pages: {len(pdf_reader.pages)}")
            
            print("🔄 Extracting page text...")
            full_text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if i < 3:  # Only show character count for first 3 pages
                    print(f"   Page {i+1}: {len(page_text)} characters")
                full_text += page_text + "\n"
            
            print(f"📊 Total character count: {len(full_text)}")
            
            # Show first few lines to understand text format
            print("\n📖 Preview of first 30 lines:")
            lines = full_text.split('\n')[:30]
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"   {i:2d}: {line.strip()[:80]}")
            
            # If PyPDF2 extracts too little text, try other methods
            if len(full_text.strip()) < 100:
                print("⚠️ PyPDF2 extracted too little text, trying other methods...")
                raise Exception("Text too short, try other methods")
            
    except Exception as e:
        print(f"❌ PyPDF2 loading failed: {e}")
        print("🔄 Trying pdfplumber...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                print(f"📄 Total PDF pages: {len(pdf.pages)}")
                full_text = ""
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        if i < 3:  # Only show character count for first 3 pages
                            print(f"   Page {i+1}: {len(page_text)} characters")
                        full_text += page_text + "\n"
                
                print(f"✅ pdfplumber loading successful, total character count: {len(full_text)}")
                
                if len(full_text.strip()) < 100:
                    print("⚠️ pdfplumber also extracted too little text, trying LangChain...")
                    raise Exception("Text still too short, try LangChain")
                
        except Exception as e2:
            print(f"❌ pdfplumber loading failed: {e2}")
            print("🔄 Trying LangChain PyPDFLoader...")
            try:
                loader = PyPDFLoader(pdf_path)
                full_doc = loader.load()
                full_text = "\n".join([page.page_content for page in full_doc])
                print(f"✅ LangChain loading successful, total character count: {len(full_text)}")
            except Exception as e3:
                print(f"❌ All PDF loading methods failed: {e3}")
                return []

    # ⭐ New: Improve two-column reading order
    print("\n🔄 Improving two-column reading order...")
    full_text = improve_two_column_reading_order(full_text)

    # Use intelligent header recognition
    print("\n🔍 Intelligent header recognition...")
    headers = extract_all_headers(full_text)
    
    if headers:
        print(f"✅ Found {len(headers)} headers:")
        for i, header in enumerate(headers, 1):
            print(f"   {i:2d}. [{header['type']}] {header['text'][:60]}")
        
        # Split chapters based on headers, ensuring title and content separation
        chapters = []
        for i in range(len(headers)):
            start = headers[i]['line_start']
            end = headers[i+1]['line_start'] if i+1 < len(headers) else len(full_text)
            
            # Extract chapter text
            chapter_text = full_text[start:end].strip()
            
            # Generate intelligent summary for this chapter
            header_title = headers[i]['text']
            chapter_summary = generate_intelligent_summary(chapter_text, header_title)
            
            # Clean chapter text
            chapter_text = replace_t_with_space(chapter_text)
            chapter_text = replace_double_lines_with_one_line(chapter_text)
            
            chapter_info = {
                'title': header_title,
                'content': chapter_text,
                'summary': chapter_summary,
                'type': headers[i]['type'],
                'word_count': len(chapter_text.split()),
                'char_count': len(chapter_text)
            }
            
            chapters.append(chapter_info)
            print(f"   📝 Chapter: {header_title[:50]}... ({len(chapter_text)} chars)")
    
    else:
        print("⚠️ No headers found, treating entire document as single chapter")
        # If no headers found, treat entire document as one chapter
        full_text = replace_t_with_space(full_text)
        full_text = replace_double_lines_with_one_line(full_text)
        
        # Generate summary for entire document
        doc_summary = generate_intelligent_summary(full_text, "Complete Document")
        
        chapters = [{
            'title': 'Complete Document',
            'content': full_text,
            'summary': doc_summary,
            'type': 'Full Document',
            'word_count': len(full_text.split()),
            'char_count': len(full_text)
        }]
    
    print(f"\n✅ Successfully extracted {len(chapters)} chapters")
    
    # Print summary statistics
    total_words = sum(chapter['word_count'] for chapter in chapters)
    total_chars = sum(chapter['char_count'] for chapter in chapters)
    
    print(f"📊 Document Statistics:")
    print(f"   Total words: {total_words:,}")
    print(f"   Total characters: {total_chars:,}")
    print(f"   Average words per chapter: {total_words // len(chapters):,}")
    
    return chapters

def create_markdown_report(chapters, pdf_path):
    """
    Create a comprehensive markdown report with intelligent summaries
    """
    from pathlib import Path
    
    pdf_name = Path(pdf_path).stem
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create markdown content
    markdown_content = []
    
    # Header
    markdown_content.append(f"# Document Analysis Report")
    markdown_content.append(f"**Source**: {pdf_name}")
    markdown_content.append(f"**Generated**: {timestamp}")
    markdown_content.append(f"**Total Chapters**: {len(chapters)}")
    markdown_content.append("")
    
    # Document overview
    total_words = sum(chapter['word_count'] for chapter in chapters)
    total_chars = sum(chapter['char_count'] for chapter in chapters)
    
    markdown_content.append("## Document Overview")
    markdown_content.append(f"- **Total Words**: {total_words:,}")
    markdown_content.append(f"- **Total Characters**: {total_chars:,}")
    markdown_content.append(f"- **Average Words per Chapter**: {total_words // len(chapters):,}")
    markdown_content.append("")
    
    # Chapter summaries
    markdown_content.append("## Chapter Summaries")
    markdown_content.append("")
    
    for i, chapter in enumerate(chapters, 1):
        markdown_content.append(f"### Chapter {i}")
        markdown_content.append(chapter['summary'])
        markdown_content.append("")
        markdown_content.append(f"*Word Count*: {chapter['word_count']:,} | *Type*: {chapter['type']}")
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")
    
    # Full content (optional, can be commented out to keep file smaller)
    markdown_content.append("## Full Content")
    markdown_content.append("")
    
    for i, chapter in enumerate(chapters, 1):
        markdown_content.append(f"### {chapter['title']}")
        markdown_content.append("")
        markdown_content.append(chapter['content'])
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")
    
    return "\n".join(markdown_content)

def find_pdf_file(filename: str) -> str:
    """Find PDF file in multiple possible locations"""
    search_paths = [
        # Current directory
        filename,
        # Parent directories
        f"../{filename}",
        f"../../{filename}",
        f"../../../{filename}",
        # Specific AS_IoP_project directory
        f"../../../AS_IoP_project/{filename}",
        f"../../AS_IoP_project/{filename}",
        f"../AS_IoP_project/{filename}",
        # Absolute path if running from workspace root
        f"/home/luluscavenger/AI_literature_agent-3/AS_IoP_project/{filename}",
        f"/home/luluscavenger/AI_literature_agent-3/AS_IoP_project/pdf_extract_test/testing_pymu/{filename}"
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            print(f"✅ Found PDF: {path}")
            return path
    
    print(f"❌ Could not find {filename} in any of these locations:")
    for path in search_paths:
        print(f"   - {path}")
    return None

def main():
    """
    Main function to process PDF and generate markdown report
    """
    print("🚀 Starting PDF text analysis and markdown generation...")
    
    # PDF file list - search for files in multiple locations
    pdf_filenames = ['paper1.pdf', 'paper2.pdf', 'paper3.pdf']
    
    # Find existing PDF files
    pdf_files = []
    for filename in pdf_filenames:
        pdf_path = find_pdf_file(filename)
        if pdf_path:
            pdf_files.append(pdf_path)
            print(f"✅ 找到PDF檔案: {Path(pdf_path).name}")
        else:
            print(f"❌ PDF檔案不存在: {filename}")
    
    # If no predefined files found, scan current directory for any PDF files
    if not pdf_files:
        print("🔍 未找到預定義PDF檔案，掃描目錄中的所有PDF檔案...")
        for file in os.listdir('.'):
            if file.lower().endswith('.pdf'):
                pdf_files.append(file)
                print(f"✅ 發現PDF檔案: {file}")
    
    if not pdf_files:
        print("❌ 沒有找到任何PDF檔案！")
        return
    
    # Output directory - 保存到 testing-text 目錄
    output_dir = Path('testing-text')
    output_dir.mkdir(exist_ok=True)
    
    for pdf_path in pdf_files:
        try:
            print(f"\n{'='*60}")
            print(f"📄 Processing: {Path(pdf_path).name}")
            print(f"{'='*60}")
            
            # Extract chapters with intelligent summaries
            chapters = split_into_chapters(pdf_path)
            
            if not chapters:
                print("❌ No chapters extracted")
                continue
            
            # Create markdown report
            markdown_content = create_markdown_report(chapters, pdf_path)
            
            # Save to file
            output_file = output_dir / f"{Path(pdf_path).stem}_text_analysis.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ Markdown report saved: {output_file}")
            print(f"📊 Report contains {len(chapters)} chapters with intelligent summaries")
            
        except Exception as e:
            print(f"❌ Error processing {Path(pdf_path).name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 All PDF processing completed! Results saved in: {output_dir}")

if __name__ == "__main__":
    main()
