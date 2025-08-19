import os
import re
import fitz  # PyMuPDF
import requests
import tempfile

def format_text_with_positions(text_with_positions):
    """
    基於位置變化的智能分段處理：
    - 檢測行首位置的明顯變化來判斷段落開始
    - 粗體文字自動成為章節標題
    - 公式和特殊格式保持獨立
    """
    if not text_with_positions:
        return ""
    
    paragraphs = []
    current_paragraph = []
    
    # 分析所有行的 x 位置，找出常見的左邊距模式
    x_positions = [item['x_position'] for item in text_with_positions if item['x_position'] is not None]
    
    # 計算位置的統計資訊
    if x_positions:
        min_x = min(x_positions)
        max_x = max(x_positions)
        
        # 將位置分組，容忍度為 5 像素
        position_groups = {}
        for x in x_positions:
            rounded_x = round(x / 5) * 5  # 將位置四捨五入到最近的 5 像素
            position_groups[rounded_x] = position_groups.get(rounded_x, 0) + 1
        
        # 找出最常見的左邊距（正文位置）
        main_x_position = max(position_groups.keys(), key=position_groups.get)
        
        # 設定位置變化的閾值
        position_threshold = 10  # 像素
    else:
        main_x_position = 0
        position_threshold = 10
    
    for i, item in enumerate(text_with_positions):
        text = item['text']
        x_pos = item['x_position']
        is_bold = item['is_bold']
        
        # 檢查是否為粗體標題
        is_bold_title = bool(re.match(r'^\*\*.*\*\*$', text))
        
        # 如果是粗體標題，直接作為獨立段落
        if is_bold_title:
            # 完成當前段落
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph).strip()
                if paragraph_text:
                    paragraphs.append(paragraph_text)
                current_paragraph = []
            
            # 粗體標題轉換為 Markdown 標題
            title_text = text.replace('**', '').strip()
            paragraphs.append(f"## {title_text}")
            continue
        
        # 檢查是否為新段落開始
        is_paragraph_start = False
        
        # 條件1：位置變化檢測 - 這是核心邏輯
        if i > 0 and x_pos is not None:
            prev_item = text_with_positions[i-1]
            prev_x_pos = prev_item['x_position']
            
            if prev_x_pos is not None:
                # 檢測位置的明顯變化
                x_diff = abs(x_pos - prev_x_pos)
                
                # 如果位置變化超過閾值，且當前行首字母大寫，可能是新段落
                if x_diff > position_threshold and text and text[0].isupper():
                    is_paragraph_start = True
                
                # 如果從縮排位置回到主位置，也是新段落
                if (abs(prev_x_pos - main_x_position) > position_threshold and 
                    abs(x_pos - main_x_position) <= position_threshold and 
                    text and text[0].isupper()):
                    is_paragraph_start = True
                
                # 如果從主位置移動到明顯的縮排位置，也是新段落
                if (abs(prev_x_pos - main_x_position) <= position_threshold and 
                    abs(x_pos - main_x_position) > position_threshold and 
                    text and text[0].isupper()):
                    is_paragraph_start = True
        
        # 條件2：學術章節標題（全大寫短詞）
        academic_sections = [
            'ABSTRACT', 'INTRODUCTION', 'METHODOLOGY', 'METHODS', 'RESULTS',
            'DISCUSSION', 'CONCLUSION', 'CONCLUSIONS', 'ACKNOWLEDGEMENTS',
            'ACKNOWLEDGMENTS', 'REFERENCES', 'BIBLIOGRAPHY', 'APPENDIX',
            'KEYWORDS', 'KEY WORDS'
        ]
        
        if text.upper() in academic_sections:
            is_paragraph_start = True
        
        # 條件3：編號列表
        if re.match(r'^\d+\.\s+', text) or re.match(r'^[a-z]\.\s+', text):
            is_paragraph_start = True
        
        # 條件4：圖表引用
        if re.match(r'^(Fig\.|Figure|Table|Equation)\s+\d+', text, re.IGNORECASE):
            is_paragraph_start = True
        
        # 條件5：明顯的段落開始標誌詞
        paragraph_indicators = [
            'However,', 'Therefore,', 'Moreover,', 'Furthermore,', 'Nevertheless,',
            'Additionally,', 'Similarly,', 'Consequently,', 'Meanwhile,', 'Thus,',
            'In particular,', 'For example,', 'In contrast,', 'On the other hand,'
        ]
        
        for indicator in paragraph_indicators:
            if text.startswith(indicator):
                is_paragraph_start = True
                break
        
        # 如果檢測到新段落開始且當前段落不為空
        if is_paragraph_start and current_paragraph:
            paragraph_text = ' '.join(current_paragraph).strip()
            if paragraph_text:
                paragraphs.append(paragraph_text)
            current_paragraph = []
        
        # 添加到當前段落
        current_paragraph.append(text)
    
    # 處理最後一個段落
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph).strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)
    
    # 合併成最終文字，段落間用雙換行分隔
    return '\n\n'.join(paragraphs)

def download_arxiv_pdf(arxiv_id, output_path):
    """下載 arXiv 論文 PDF"""
    import urllib.request
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    print(f"📥 正在下載: {url}")
    urllib.request.urlretrieve(url, output_path)
    print(f"✅ 下載完成: {output_path}")

def extract_from_pdf(pdf_path, output_dir):
    """
    從 PDF 檔案中提取所有文字、公式、圖片，儲存為 Markdown 與 PNG 格式。
    支援本地檔案路徑和 URL。
    """
    os.makedirs(output_dir, exist_ok=True)
    img_dir = os.path.join(output_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    text_md_path = os.path.join(output_dir, "text.md")
    formulas_path = os.path.join(output_dir, "formulas.tex")

    # 檢查是否為 URL，如果是則下載到記憶體
    if pdf_path.startswith(('http://', 'https://')):
        print(f"📥 正在下載 PDF 從: {pdf_path}")
        try:
            response = requests.get(pdf_path, timeout=30)
            response.raise_for_status()
            print(f"✅ PDF 下載成功，大小: {len(response.content)} bytes")
            
            # 直接從記憶體開啟 PDF
            doc = fitz.open(stream=response.content, filetype="pdf")
            
        except Exception as e:
            print(f"❌ PDF 下載失敗: {e}")
            return False
    else:
        # 本地檔案路徑
        if not os.path.exists(pdf_path):
            print(f"❌ PDF 檔案不存在: {pdf_path}")
            return False
        doc = fitz.open(pdf_path)

    # 收集所有頁面的文字和位置資訊
    all_text_with_positions = []
    all_formulas = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 使用字典模式獲取詳細的位置和格式資訊
        blocks = page.get_text("dict")
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    line_x_position = None
                    is_bold_line = False
                    
                    for span in line["spans"]:
                        text = span["text"]
                        flags = span["flags"]  # 字體格式標誌
                        bbox = span["bbox"]  # 邊界框 [x0, y0, x1, y1]
                        
                        # 記錄行的 x 位置（左邊距）
                        if line_x_position is None:
                            line_x_position = bbox[0]
                        
                        # 檢查是否為粗體
                        if flags & 16:
                            is_bold_line = True
                            text = f"**{text.strip()}**"
                        
                        line_text += text
                    
                    if line_text.strip():
                        # 儲存文字、位置和格式資訊
                        all_text_with_positions.append({
                            'text': line_text.strip(),
                            'x_position': line_x_position,
                            'is_bold': is_bold_line,
                            'page': page_num
                        })
                        
                        # 檢查是否為公式行
                        if re.search(r"[=√∑∫≤≥≠πταβγ]", line_text):
                            all_formulas.append(line_text.strip())
        
        # 擷取圖片
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:
                pix.save(os.path.join(img_dir, f"page{page_num+1}_img{img_idx+1}.png"))
            else:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(os.path.join(img_dir, f"page{page_num+1}_img{img_idx+1}.png"))
            pix = None  # 清理記憶體
    
    # 應用智能分段處理（基於位置變化）
    formatted_text = format_text_with_positions(all_text_with_positions)
    
    # 寫入處理後的文字
    with open(text_md_path, "w", encoding="utf-8") as text_file, \
         open(formulas_path, "w", encoding="utf-8") as formula_file:
        
        text_file.write("# PDF 文字提取結果\n\n")
        text_file.write(formatted_text)
        
        # 寫入公式
        for formula in all_formulas:
            formula_file.write(formula + "\n")

    doc.close()
    print(f"✅ 提取完成：{pdf_path}")
    print(f"📄 文字檔：{text_md_path}")
    print(f"📐 公式檔：{formulas_path}")
    print(f"🖼️ 圖片資料夾：{img_dir}")
    return True


def process_arxiv_paper(arxiv_id):
    """處理指定的 arXiv 論文"""
    
    # 設定路徑
    base_dir = f"/home/luluscavenger/AI_literature_agent-3/{arxiv_id}"
    pdf_path = os.path.join(base_dir, f"{arxiv_id}.pdf")
    
    print(f"🔬 開始處理 arXiv 論文: {arxiv_id}")
    print(f"📁 輸出目錄: {base_dir}")
    
    # 檢查並下載 PDF
    if not os.path.exists(pdf_path):
        print(f"📁 PDF 不存在，正在下載...")
        try:
            download_arxiv_pdf(arxiv_id, pdf_path)
        except Exception as e:
            print(f"❌ 下載失敗: {e}")
            return False
    else:
        print(f"📁 PDF 已存在: {pdf_path}")
    
    # 提取內容
    try:
        print(f"🔄 開始提取內容...")
        extract_from_pdf(pdf_path, base_dir)
        
        # 顯示結果統計
        text_file = os.path.join(base_dir, "text.md")
        formula_file = os.path.join(base_dir, "formulas.tex")
        img_dir = os.path.join(base_dir, "images")
        
        print(f"\n📊 提取結果統計:")
        print(f"=" * 50)
        
        # 文字檔案統計
        if os.path.exists(text_file):
            with open(text_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
            print(f"📄 文字檔案:")
            print(f"   - 檔案大小: {len(text_content):,} 字符")
            print(f"   - 行數: {len(text_content.splitlines()):,} 行")
            print(f"   - 檔案路徑: {text_file}")
        
        # 公式檔案統計
        if os.path.exists(formula_file):
            with open(formula_file, 'r', encoding='utf-8') as f:
                formula_content = f.read()
            formula_lines = [line for line in formula_content.splitlines() if line.strip()]
            print(f"📐 公式檔案:")
            print(f"   - 公式行數: {len(formula_lines)} 行")
            print(f"   - 檔案路徑: {formula_file}")
        
        # 圖片統計
        if os.path.exists(img_dir):
            images = [f for f in os.listdir(img_dir) if f.endswith('.png')]
            print(f"🖼️ 圖片檔案:")
            print(f"   - 圖片數量: {len(images)} 張")
            print(f"   - 圖片目錄: {img_dir}")
            
            if images:
                print(f"   - 圖片清單:")
                for img in sorted(images):
                    img_path = os.path.join(img_dir, img)
                    img_size = os.path.getsize(img_path)
                    print(f"     * {img} ({img_size:,} bytes)")
        
        print(f"=" * 50)
        print(f"✅ 所有檔案已成功提取並儲存到: {base_dir}")
        return True
        
    except Exception as e:
        print(f"❌ 提取失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arxiv_2507_15389():
    """測試 arXiv 2507.15389 論文提取"""
    return process_arxiv_paper("2507.15389")


if __name__ == "__main__":
    import sys
    
    # 檢查是否有命令行參數
    if len(sys.argv) > 1:
        arxiv_id = sys.argv[1]
        print(f"🎯 接收到 arXiv ID: {arxiv_id}")
        success = process_arxiv_paper(arxiv_id)
        if success:
            print(f"🎉 處理完成！")
        else:
            print(f"💥 處理失敗！")
            sys.exit(1)
    else:
        # 沒有參數時，運行預設測試
        print("📋 沒有提供 arXiv ID，運行預設測試...")
        test_arxiv_2507_15389()
