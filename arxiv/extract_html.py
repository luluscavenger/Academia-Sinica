import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_from_html(html_url, base_dir):
    os.makedirs(base_dir, exist_ok=True)
    img_dir = os.path.join(base_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    # 下載 HTML
    r = requests.get(html_url)
    html = r.text
    with open(os.path.join(base_dir, "source.html"), "w", encoding="utf-8") as f:
        f.write(html)
    soup = BeautifulSoup(html, 'html.parser')

    md_lines = []

    # 找主要內容區域，通常在 <main>, <article> 或有特定 class 的 <div>
    main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    if main_content:
        # 專注於章節標題(h2)和段落內容(p)的處理
        processed_elements = set()  # 避免重複處理
        
        # 首先處理所有元素，按文檔順序
        all_elements = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        
        for element in all_elements:
            # 跳過已處理的元素
            if id(element) in processed_elements:
                continue
                
            # 跳過導航、側邊欄等非內容區域
            classes = element.get('class', [])
            if any(cls in ['nav', 'sidebar', 'menu', 'footer', 'header', 'ad', 'advertisement', 'toc'] for cls in classes):
                continue
            
            tag_name = element.name
            
            # 處理章節標題 (h2 為主要章節)
            if tag_name == 'h2':
                title_text = extract_text_with_math(element)
                if title_text.strip():
                    md_lines.append(f"## {title_text.strip()}")
                    md_lines.append("")  # 標題後加空行
                    processed_elements.add(id(element))
            
            # 處理其他標題層級
            elif tag_name in ['h1', 'h3', 'h4', 'h5', 'h6']:
                level = int(tag_name[1])
                title_text = extract_text_with_math(element)
                if title_text.strip():
                    md_lines.append(f"{'#' * level} {title_text.strip()}")
                    md_lines.append("")
                    processed_elements.add(id(element))
            
            # 處理段落內容 (p 為主要文章內容)
            elif tag_name == 'p':
                paragraph_content = extract_text_with_math(element)
                if paragraph_content.strip():
                    # 清理段落內容，移除多餘空白
                    clean_content = ' '.join(paragraph_content.split())
                    if len(clean_content) > 10:  # 只保留有意義的段落
                        md_lines.append(clean_content)
                        md_lines.append("")  # 段落後加空行
                    processed_elements.add(id(element))
        
        # 如果沒有找到h2標題，嘗試查找其他可能的章節標識
        if not any('## ' in line for line in md_lines):
            print("⚠️ 未找到 h2 標題，嘗試查找其他章節標識...")
            
            # 尋找可能的章節標題 (具有特定class或id的div)
            section_divs = main_content.find_all(['div', 'section'], 
                class_=lambda x: x and any(keyword in str(x).lower() 
                for keyword in ['title', 'heading', 'section', 'chapter']))
            
            for div in section_divs:
                if id(div) not in processed_elements:
                    div_text = extract_text_with_math(div)
                    if div_text.strip() and len(div_text.strip()) < 100:  # 可能是標題
                        md_lines.append(f"## {div_text.strip()}")
                        md_lines.append("")
                        processed_elements.add(id(div))

    # 清理和優化Markdown內容
    cleaned_md_lines = []
    for line in md_lines:
        if line.strip():  # 只保留非空行
            cleaned_md_lines.append(line)
        elif cleaned_md_lines and cleaned_md_lines[-1] != "":
            # 避免連續空行，只在需要時加入單個空行
            cleaned_md_lines.append("")
    
    # 儲存為Markdown格式
    with open(os.path.join(base_dir, "text.md"), "w", encoding="utf-8") as f:
        if cleaned_md_lines:
            f.write('\n'.join(cleaned_md_lines))
            # 確保文件以換行結束
            if not cleaned_md_lines[-1] == "":
                f.write('\n')
        else:
            f.write("# 無法提取內容\n\n未能從HTML中提取到有效的文字內容。")
    
    print(f"✅ Markdown文件已保存，共 {len([l for l in cleaned_md_lines if l.strip()])} 行內容")

    # 下載圖片，仍用你的策略
    img_count = 1
    if not html_url.endswith('/'):
        html_url += '/'
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        img_url = urljoin(html_url, src)
        try:
            r_img = requests.get(img_url, timeout=15)
            if r_img.status_code == 200:
                fname = f"img_{img_count}.png"
                with open(os.path.join(img_dir, fname), "wb") as fout:
                    fout.write(r_img.content)
                img_count += 1
            else:
                print(f"Failed to download image {img_url}: HTTP {r_img.status_code}")
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")

    print(f"HTML extraction complete. Images and text.md saved in: {base_dir}")


def extract_text_with_math(element):
    """從HTML元素中提取文字和數學公式，轉換為Markdown格式"""
    if not element:
        return ""
    
    result = ""
    
    # 檢查是否包含子元素
    if element.find():
        for child in element.children:
            if hasattr(child, 'name') and child.name:
                # 處理數學公式
                if child.name in ['span', 'div']:
                    classes = child.get('class', [])
                    if any(c.lower() in ['math', 'katex', 'mjx', 'mathjax', 'mathml'] for c in classes):
                        latex = child.get_text().strip()
                        if latex:
                            if '\n' in latex or len(latex) > 40:
                                result += f" $$\n{latex}\n$$ "
                            else:
                                result += f" ${latex}$ "
                    else:
                        # 遞歸處理其他 span/div
                        nested_text = extract_text_with_math(child)
                        if nested_text.strip():
                            result += nested_text
                
                elif child.name == 'math':
                    latex = child.get_text().strip()
                    if latex:
                        result += f" $$\n{latex}\n$$ "
                
                # 處理強調格式
                elif child.name in ['strong', 'b']:
                    text = child.get_text().strip()
                    if text:
                        result += f" **{text}** "
                elif child.name in ['em', 'i']:
                    text = child.get_text().strip()
                    if text:
                        result += f" *{text}* "
                elif child.name == 'code':
                    text = child.get_text().strip()
                    if text:
                        result += f" `{text}` "
                
                # 處理連結
                elif child.name == 'a':
                    href = child.get('href', '')
                    text = child.get_text().strip()
                    if text:
                        if href and not href.startswith('#'):  # 跳過錨點連結
                            result += f" [{text}]({href}) "
                        else:
                            result += f" {text} "
                
                # 處理換行和空格
                elif child.name == 'br':
                    result += " \n"
                
                # 跳過不需要的標籤
                elif child.name in ['script', 'style', 'noscript']:
                    continue
                
                # 其他標籤遞歸處理
                else:
                    nested_text = extract_text_with_math(child)
                    if nested_text.strip():
                        result += nested_text
            else:
                # 純文字節點
                text = str(child).strip()
                if text:
                    result += f" {text} "
    else:
        # 沒有子元素，直接取文字
        text = element.get_text().strip()
        if text:
            result += f" {text} "
    
    # 清理結果：移除多餘空白，保持數學公式格式
    result = result.replace('\n\n', '\n').strip()
    # 標準化空白字符
    import re
    result = re.sub(r' +', ' ', result)  # 多個空格變成一個
    result = re.sub(r' *\n+ *', '\n', result)  # 清理換行周圍的空格
    
    return result

def test_html_extraction():
    """測試HTML提取功能"""
    test_url = "https://arxiv.org/html/2507.21856"
    test_dir = "./test_html_extract"
    
    print(f"🧪 Testing HTML extraction with: {test_url}")
    try:
        extract_from_html(test_url, test_dir)
        
        # 檢查生成的文件
        text_file = os.path.join(test_dir, "text.md")
        if os.path.exists(text_file):
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Markdown文件生成成功")
            print(f"📊 文件大小: {len(content)} 字符")
            print(f"📝 行數: {len(content.split(chr(10)))}")
            
            # 顯示前幾行預覽
            lines = content.split('\n')[:10]
            print("📖 內容預覽:")
            for line in lines:
                if line.strip():
                    print(f"  {line}")
        else:
            print("❌ Markdown文件未生成")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

# ====== 測試方式 ======
def simple_test():
    """簡單測試函數"""
    test_url = "https://arxiv.org/html/2507.21856"
    test_dir = "./test_h2_p_extract"
    
    print(f"🧪 測試 h2 標題 + p 段落提取模式")
    print(f"URL: {test_url}")
    print(f"輸出目錄: {test_dir}")
    
    try:
        extract_from_html(test_url, test_dir)
        
        # 檢查結果
        text_file = os.path.join(test_dir, "text.md")
        if os.path.exists(text_file):
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ 提取完成!")
            print(f"📊 文件大小: {len(content)} 字符")
            
            # 統計章節數量
            h2_count = content.count('## ')
            paragraph_count = len([line for line in content.split('\n') if line.strip() and not line.startswith('#')])
            
            print(f"📚 找到 {h2_count} 個 h2 章節標題")
            print(f"📝 找到 {paragraph_count} 個段落")
            
            # 顯示前幾行
            lines = content.split('\n')[:20]
            print("📖 內容預覽:")
            for line in lines:
                if line.strip():
                    print(f"  {line}")
                    
        else:
            print("❌ 文件未生成")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

# extract_from_html("https://arxiv.org/html/2507.21856", "./2507.21856")
# test_html_extraction()  # 執行測試
# simple_test()  # 執行新的簡單測試
