import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime
import pandas as pd
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import tarfile
import textwrap

class ArxivFormulaExtractor:
    """arXiv 公式擷取器 - 優先提取文字內容保存為MD，無法提取才保存PNG"""
    
    def __init__(self, arxiv_id):
        """
        初始化擷取器
        
        Args:
            arxiv_id (str): arXiv 論文代碼，如 "2507.21856"
        """
        self.arxiv_id = arxiv_id
        self.base_dir = f"./arxiv_{arxiv_id}_formulas"
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 不同格式的 URL
        self.urls = {
            'html': f"https://arxiv.org/html/{arxiv_id}",
            'latex': f"https://arxiv.org/e-print/{arxiv_id}",
            'pdf': f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        }
        
        self.formulas = {
            'html': [],
            'latex': [],
            'pdf': []
        }
        
        # 創建圖片儲存目錄
        self.images_dir = os.path.join(self.base_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        # 創建 Markdown 文件路徑
        self.markdown_file = os.path.join(self.base_dir, f"formulas_{arxiv_id}.md")
    
    def extract_all_formats(self):
        """按優先順序擷取公式：HTML > LaTeX > PDF，優先保存為MD文字格式"""
        print(f"🚀 開始擷取 arXiv:{self.arxiv_id} 的公式...")
        
        # 初始化 Markdown 文件
        with open(self.markdown_file, 'w', encoding='utf-8') as f:
            f.write(f"# arXiv {self.arxiv_id} 公式集合\n\n")
            f.write(f"提取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        extracted = False
        
        # 優先嘗試 HTML 擷取
        try:
            print("📄 嘗試擷取 HTML 格式公式...")
            self.extract_html_formulas()
            if self.formulas['html']:
                print(f"✅ HTML: 找到 {len(self.formulas['html'])} 個公式")
                extracted = True
            else:
                print("⚠️ HTML 格式沒有找到公式")
        except Exception as e:
            print(f"⚠️ HTML 擷取失敗: {e}")
        
        # 如果 HTML 沒有成功，嘗試 LaTeX
        if not extracted:
            try:
                print("📝 嘗試擷取 LaTeX 格式公式...")
                self.extract_latex_formulas()
                if self.formulas['latex']:
                    print(f"✅ LaTeX: 找到 {len(self.formulas['latex'])} 個公式")
                    extracted = True
                else:
                    print("⚠️ LaTeX 格式沒有找到公式")
            except Exception as e:
                print(f"⚠️ LaTeX 擷取失敗: {e}")
        
        # 如果 HTML 和 LaTeX 都沒有成功，嘗試 PDF
        if not extracted:
            try:
                print("📊 嘗試擷取 PDF 格式公式...")
                self.extract_pdf_formulas()
                if self.formulas['pdf']:
                    print(f"✅ PDF: 找到 {len(self.formulas['pdf'])} 個公式")
                    extracted = True
                else:
                    print("⚠️ PDF 格式沒有找到公式")
            except Exception as e:
                print(f"⚠️ PDF 擷取失敗: {e}")
        
        if not extracted:
            print("❌ 所有格式都無法成功擷取公式")
        
        self.filter_and_save_formulas()
        return self.formulas
    def filter_and_save_formulas(self):
        """篩選有意義的公式，並儲存統計結果到 xlsx，公式內容已保存在 MD"""
        excel_data = []
        total_found = 0
        markdown_count = 0
        png_count = 0
        
        for format_type in ['html', 'latex', 'pdf']:
            format_count = 0
            for formula in self.formulas.get(format_type, []):
                total_found += 1
                
                content = formula.get('content', '')
                if content and len(content.strip()) > 2:
                    format_count += 1
                    
                    # 統計格式類型
                    if formula.get('format') == 'markdown':
                        markdown_count += 1
                        file_reference = "已保存到 MD 文件"
                        file_status = "✅ Markdown 格式"
                    elif formula.get('format') == 'png':
                        png_count += 1
                        file_reference = formula.get('image_path', '')
                        file_status = "📷 PNG 圖片"
                    else:
                        file_reference = "無文件"
                        file_status = "❌ 未處理"
                    
                    excel_data.append({
                        '來源格式': format_type.upper(),
                        '公式類型': formula.get('type', 'unknown'),
                        '擷取來源': formula.get('source', 'unknown'),
                        '頁數': formula.get('page', ''),
                        '公式內容': content[:100] + ('...' if len(content) > 100 else ''),  # 截斷長內容
                        '儲存格式': formula.get('format', 'unknown'),
                        '文件狀態': file_status,
                        '文件參考': file_reference,
                        '原始資料': formula.get('raw_data', '')[:50] + ('...' if len(formula.get('raw_data', '')) > 50 else '')
                    })
                    
            if format_count > 0:
                print(f"✅ {format_type.upper()}: 找到 {format_count} 個公式")
        
        if not excel_data:
            print(f"⚠️ 從 {total_found} 個原始項目中沒有找到公式")
            return
            
        df = pd.DataFrame(excel_data)
        
        # 重新排列欄位順序
        column_order = ['來源格式', '公式類型', '儲存格式', '文件狀態', '公式內容', '文件參考', '擷取來源', '頁數', '原始資料']
        df = df[column_order]
        
        excel_path = os.path.join(self.base_dir, f"formulas_summary_{self.arxiv_id}.xlsx")
        
        # 使用更好的 Excel 格式設定
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='公式摘要')
            
            # 獲取工作表並調整欄位寬度
            worksheet = writer.sheets['公式摘要']
            
            # 設定欄位寬度
            column_widths = {
                'A': 12,  # 來源格式
                'B': 15,  # 公式類型
                'C': 12,  # 儲存格式
                'D': 15,  # 文件狀態
                'E': 60,  # 公式內容
                'F': 30,  # 文件參考
                'G': 20,  # 擷取來源
                'H': 8,   # 頁數
                'I': 30   # 原始資料
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        # 在 Markdown 文件末尾添加摘要
        with open(self.markdown_file, 'a', encoding='utf-8') as md_file:
            md_file.write("\n## 提取摘要\n\n")
            md_file.write(f"- **總共找到公式**: {len(excel_data)} 個\n")
            md_file.write(f"- **Markdown 格式**: {markdown_count} 個\n")
            md_file.write(f"- **PNG 圖片格式**: {png_count} 個\n")
            md_file.write(f"- **Excel 摘要文件**: `{os.path.basename(excel_path)}`\n\n")
            md_file.write("### 格式分佈\n\n")
            
            for format_type in ['html', 'latex', 'pdf']:
                count = len([f for f in self.formulas.get(format_type, [])])
                if count > 0:
                    md_file.write(f"- **{format_type.upper()}**: {count} 個公式\n")
        
        print(f"📊 公式摘要已保存到 Excel 文件: {excel_path}")
        print(f"📝 公式內容已保存到 Markdown 文件: {self.markdown_file}")
        print(f"📈 共處理 {len(excel_data)} 個公式")
        print(f"📄 其中 {markdown_count} 個保存為 Markdown，{png_count} 個保存為 PNG")
        return len(excel_data)
    
    def extract_html_formulas(self):
        """從 HTML 版本擷取公式，優先保存為文字內容"""
        try:
            response = requests.get(self.urls['html'])
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"HTML 版本不可用: {e}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尋找所有可能的數學公式元素
        math_selectors = [
            'math',  # MathML
            '.math',  # 數學類別
            '.katex',  # KaTeX
            '.MJX-container',  # MathJax v3
            '.mjx-container',  # MathJax
            '.ltx_Math',  # LaTeX
            '[data-math]',  # 有數學屬性的元素
        ]
        
        formula_elements = []
        for selector in math_selectors:
            elements = soup.select(selector)
            formula_elements.extend(elements)
        
        # 也尋找包含數學符號的文字
        all_text = soup.get_text()
        
        # 添加到 Markdown 文件
        with open(self.markdown_file, 'a', encoding='utf-8') as md_file:
            md_file.write("## HTML 格式公式\n\n")
        
        # 尋找內聯公式 $...$
        inline_formulas = re.findall(r'\$([^$]+)\$', all_text)
        for idx, formula in enumerate(inline_formulas):
            if formula.strip() and len(formula.strip()) > 2 and self._is_meaningful_formula(formula.strip()):
                # 檢查公式後面是否有編號 (1), (2) 等
                formula_with_context = self._extract_numbered_formula_from_html(all_text, f'${formula}$')
                if formula_with_context:
                    formula_content, equation_number = formula_with_context
                    
                    if self._save_formula_to_markdown(formula_content, 'HTML', f'inline_eq_{equation_number}', idx):
                        self.formulas['html'].append({
                            'type': f'inline_equation_{equation_number}',
                            'content': formula_content,
                            'source': 'html_text',
                            'raw_data': formula_content,
                            'format': 'markdown',
                            'equation_number': equation_number
                        })
                    else:
                        # 無法保存為文字時，創建 PNG
                        screenshot_path = os.path.join(self.images_dir, f"html_inline_eq_{equation_number}_{idx}.png")
                        if self._create_formula_screenshot(formula_content, screenshot_path):
                            self.formulas['html'].append({
                                'type': f'inline_equation_{equation_number}',
                                'content': formula_content,
                                'source': 'html_screenshot',
                                'raw_data': formula_content,
                                'image_path': screenshot_path,
                                'format': 'png',
                                'equation_number': equation_number
                            })
        
        # 尋找顯示公式 $$...$$
        display_formulas = re.findall(r'\$\$([^$]+)\$\$', all_text)
        for idx, formula in enumerate(display_formulas):
            if formula.strip() and len(formula.strip()) > 2 and self._is_meaningful_formula(formula.strip()):
                # 檢查公式後面是否有編號 (1), (2) 等
                formula_with_context = self._extract_numbered_formula_from_html(all_text, f'$${formula}$$')
                if formula_with_context:
                    formula_content, equation_number = formula_with_context
                    
                    if self._save_formula_to_markdown(formula_content, 'HTML', f'display_eq_{equation_number}', idx):
                        self.formulas['html'].append({
                            'type': f'display_equation_{equation_number}',
                            'content': formula_content,
                            'source': 'html_text',
                            'raw_data': formula_content,
                            'format': 'markdown',
                            'equation_number': equation_number
                        })
                    else:
                        screenshot_path = os.path.join(self.images_dir, f"html_display_eq_{equation_number}_{idx}.png")
                        if self._create_formula_screenshot(formula_content, screenshot_path):
                            self.formulas['html'].append({
                                'type': f'display_equation_{equation_number}',
                                'content': formula_content,
                                'source': 'html_screenshot',
                                'raw_data': formula_content,
                                'image_path': screenshot_path,
                                'format': 'png',
                                'equation_number': equation_number
                            })
        
        # 處理找到的數學元素
        for idx, element in enumerate(formula_elements):
            # 嘗試獲取 LaTeX 內容
            latex_content = element.get('data-math') or element.get('title') or element.get_text().strip()
            
            if latex_content and len(latex_content) > 2 and self._is_meaningful_formula(latex_content):
                if self._save_formula_to_markdown(latex_content, 'HTML', 'math_element', idx):
                    self.formulas['html'].append({
                        'type': 'math_element',
                        'content': latex_content,
                        'source': 'html_text',
                        'raw_data': str(element)[:200] + '...',
                        'format': 'markdown'
                    })
                else:
                    screenshot_path = os.path.join(self.images_dir, f"html_element_{idx}.png")
                    if self._create_formula_screenshot(latex_content, screenshot_path):
                        self.formulas['html'].append({
                            'type': 'math_element',
                            'content': latex_content,
                            'source': 'html_screenshot',
                            'raw_data': str(element)[:200] + '...',
                            'image_path': screenshot_path,
                            'format': 'png'
                        })
    
    def _save_formula_to_markdown(self, formula_content, source_format, formula_type, idx):
        """將公式保存到 Markdown 文件"""
        try:
            with open(self.markdown_file, 'a', encoding='utf-8') as md_file:
                md_file.write(f"### {source_format} {formula_type} 公式 {idx + 1}\n\n")
                
                # 如果是 LaTeX 格式，用代碼塊包圍
                if formula_content.startswith('$') and formula_content.endswith('$'):
                    md_file.write(f"```latex\n{formula_content}\n```\n\n")
                else:
                    md_file.write(f"```\n{formula_content}\n```\n\n")
                
                # 添加渲染版本
                md_file.write(f"**渲染版本:** {formula_content}\n\n")
                md_file.write("---\n\n")
                
            return True
        except Exception as e:
            print(f"⚠️ 無法保存到 Markdown: {e}")
            return False
    
    def _is_meaningful_formula(self, content):
        """判斷公式是否有意義 - 通用版本"""
        content = content.strip()
        
        # 長度檢查
        if len(content) < 3 or len(content) > 200:
            return False
        
        # 包含數學運算符或等式
        has_math_ops = bool(re.search(r'[=+\-*/^_{}\\]', content))
        
        # 包含數字和字母的組合
        has_alphanumeric = bool(re.search(r'[a-zA-Z].*[0-9]|[0-9].*[a-zA-Z]', content))
        
        # 包含常見數學符號
        has_math_symbols = bool(re.search(r'[∑∏∫∂∇∆Ω±×÷≤≥≠≈∈∉⊂⊃∪∩]', content))
        
        # 包含希臘字母
        has_greek = bool(re.search(r'[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]', content))
        
        # 包含 LaTeX 命令
        has_latex_cmd = bool(re.search(r'\\(frac|sum|int|prod|lim|sqrt|begin|end)', content))
        
        # 排除純文字或簡單內容
        simple_patterns = [
            r'^[a-zA-Z]+$',  # 純字母
            r'^[0-9]+$',     # 純數字
            r'^[a-zA-Z]{1,3}[0-9]{1,3}$',  # 簡單變數如 x1, a2
            r'^[()[\]{}]+$',  # 純括號
            r'^\s*$'          # 空白
        ]
        
        for pattern in simple_patterns:
            if re.match(pattern, content):
                return False
        
        # 至少滿足兩個數學條件
        math_conditions = sum([has_math_ops, has_alphanumeric, has_math_symbols, has_greek, has_latex_cmd])
        
        return math_conditions >= 2
    
    def _extract_numbered_formula_from_html(self, text, formula_pattern):
        """從 HTML 文本中提取帶編號的公式"""
        # 尋找公式後面緊跟著編號的模式
        # 匹配公式後面的 (1), (2), (3) 等編號
        escaped_pattern = re.escape(formula_pattern)
        numbered_pattern = escaped_pattern + r'\s*\((\d+)\)'
        
        match = re.search(numbered_pattern, text)
        if match:
            equation_number = match.group(1)
            return (formula_pattern, equation_number)
        
        return None
    
    def _save_svg_image(self, svg_element, filename):
        """儲存 SVG 圖片"""
        try:
            svg_content = str(svg_element)
            svg_path = os.path.join(self.images_dir, f"{filename}.svg")
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return svg_path
        except Exception as e:
            print(f"儲存 SVG 失敗: {e}")
            return ""
    
    def _save_base64_image(self, base64_src, filename):
        """儲存 base64 圖片"""
        try:
            # 解析 base64 資料
            header, data = base64_src.split(',', 1)
            img_format = header.split(';')[0].split('/')[1]
            
            # 解碼並儲存
            img_data = base64.b64decode(data)
            img_path = os.path.join(self.images_dir, f"{filename}.{img_format}")
            
            with open(img_path, 'wb') as f:
                f.write(img_data)
            
            return img_path
        except Exception as e:
            print(f"儲存 base64 圖片失敗: {e}")
            return ""
    
    def extract_latex_formulas(self):
        """從 LaTeX 原始檔擷取公式，優先保存為文字內容"""
        try:
            # 下載 LaTeX 源碼 (通常是 tar.gz 格式)
            response = requests.get(self.urls['latex'])
            response.raise_for_status()
            
            # 保存為臨時文件
            latex_file = os.path.join(self.base_dir, f"{self.arxiv_id}.tar.gz")
            with open(latex_file, 'wb') as f:
                f.write(response.content)
            
            # 添加到 Markdown 文件
            with open(self.markdown_file, 'a', encoding='utf-8') as md_file:
                md_file.write("## LaTeX 格式公式\n\n")
            
            # 解壓縮並尋找 .tex 文件
            try:
                with tarfile.open(latex_file, 'r:gz') as tar:
                    tar.extractall(self.base_dir)
                    
                # 尋找 .tex 文件
                tex_files = []
                for root, dirs, files in os.walk(self.base_dir):
                    for file in files:
                        if file.endswith('.tex'):
                            tex_files.append(os.path.join(root, file))
                
                # 處理每個 .tex 文件
                for tex_file in tex_files:
                    self._extract_formulas_from_tex_file(tex_file)
                    
            except tarfile.ReadError:
                # 可能是單個 .tex 文件
                try:
                    with open(latex_file, 'r', encoding='utf-8', errors='ignore') as f:
                        tex_content = f.read()
                        self._extract_formulas_from_tex_content(tex_content)
                except Exception as e:
                    print(f"無法讀取 LaTeX 內容: {e}")
                    
        except Exception as e:
            print(f"LaTeX 下載失敗: {e}")
    
    def _extract_formulas_from_tex_file(self, tex_file):
        """從 .tex 文件中擷取公式"""
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self._extract_formulas_from_tex_content(content)
        except Exception as e:
            print(f"讀取 {tex_file} 失敗: {e}")
    
    def _extract_formulas_from_tex_content(self, content):
        """從 TeX 內容中擷取公式，優先保存文字內容"""
        
        # 1. 內聯公式 $...$
        inline_matches = re.findall(r'(?<!\\)\$([^$]+?)\$', content)
        meaningful_inline = []
        for match in inline_matches:
            if self._is_meaningful_latex_formula(match.strip()):
                meaningful_inline.append(match.strip())
        
        # 去重並取前50個最複雜的
        meaningful_inline = list(dict.fromkeys(meaningful_inline))
        meaningful_inline.sort(key=lambda x: self._formula_complexity_score(x), reverse=True)
        meaningful_inline = meaningful_inline[:50]
        
        for idx, match in enumerate(meaningful_inline):
            formula_content = f'${match}$'
            
            # 檢查是否為帶編號的公式
            formula_with_context = self._extract_numbered_formula_from_latex(content, formula_content)
            if formula_with_context:
                formula_content, equation_number = formula_with_context
                
                if self._save_formula_to_markdown(formula_content, 'LaTeX', f'inline_eq_{equation_number}', idx):
                    self.formulas['latex'].append({
                        'type': f'inline_equation_{equation_number}',
                        'content': formula_content,
                        'source': 'latex_text',
                        'raw_data': formula_content,
                        'format': 'markdown',
                        'equation_number': equation_number
                    })
                else:
                    screenshot_path = os.path.join(self.images_dir, f"latex_inline_eq_{equation_number}_{idx}.png")
                    if self._create_formula_screenshot(formula_content, screenshot_path):
                        self.formulas['latex'].append({
                            'type': f'inline_equation_{equation_number}',
                            'content': formula_content,
                            'source': 'latex_screenshot',
                            'raw_data': formula_content,
                            'image_path': screenshot_path,
                            'format': 'png',
                            'equation_number': equation_number
                        })
        
        # 2. 顯示公式 $$...$$
        display_matches = re.findall(r'\$\$([^$]+?)\$\$', content, re.DOTALL)
        meaningful_display = []
        for match in display_matches:
            cleaned = re.sub(r'\s+', ' ', match.strip())
            if self._is_meaningful_latex_formula(cleaned):
                meaningful_display.append(cleaned)
        
        meaningful_display = list(dict.fromkeys(meaningful_display))
        meaningful_display.sort(key=lambda x: self._formula_complexity_score(x), reverse=True)
        meaningful_display = meaningful_display[:30]
        
        for idx, match in enumerate(meaningful_display):
            formula_content = f'$${match}$$'
            
            # 檢查是否為帶編號的公式
            formula_with_context = self._extract_numbered_formula_from_latex(content, formula_content)
            if formula_with_context:
                formula_content, equation_number = formula_with_context
                
                if self._save_formula_to_markdown(formula_content, 'LaTeX', f'display_eq_{equation_number}', idx):
                    self.formulas['latex'].append({
                        'type': f'display_equation_{equation_number}',
                        'content': formula_content,
                        'source': 'latex_text',
                        'raw_data': formula_content,
                        'format': 'markdown',
                        'equation_number': equation_number
                    })
                else:
                    screenshot_path = os.path.join(self.images_dir, f"latex_display_eq_{equation_number}_{idx}.png")
                    if self._create_formula_screenshot(formula_content, screenshot_path):
                        self.formulas['latex'].append({
                            'type': f'display_equation_{equation_number}',
                            'content': formula_content,
                            'source': 'latex_screenshot',
                            'raw_data': formula_content,
                            'image_path': screenshot_path,
                            'format': 'png',
                            'equation_number': equation_number
                        })
        
        # 3. equation 環境
        equation_patterns = [
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{align\}(.*?)\\end\{align\}',
            r'\\begin\{gather\}(.*?)\\end\{gather\}',
        ]
        
        for pattern in equation_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            env_name = pattern.split('{')[1].split('}')[0]
            meaningful_env = []
            
            for match in matches:
                cleaned = re.sub(r'\s+', ' ', match.strip())
                if len(cleaned) > 10 and self._is_meaningful_latex_formula(cleaned):
                    meaningful_env.append(cleaned)
            
            meaningful_env = list(dict.fromkeys(meaningful_env))
            meaningful_env.sort(key=lambda x: self._formula_complexity_score(x), reverse=True)
            meaningful_env = meaningful_env[:20]
            
            for idx, match in enumerate(meaningful_env):
                full_env = f'\\begin{{{env_name}}}{match}\\end{{{env_name}}}'
                
                # 檢查是否為帶編號的公式環境
                formula_with_context = self._extract_numbered_formula_from_latex(content, full_env)
                if formula_with_context:
                    formula_content, equation_number = formula_with_context
                    
                    if self._save_formula_to_markdown(formula_content, 'LaTeX', f'{env_name}_eq_{equation_number}', idx):
                        self.formulas['latex'].append({
                            'type': f'{env_name}_equation_{equation_number}',
                            'content': formula_content,
                            'source': 'latex_text',
                            'raw_data': formula_content,
                            'format': 'markdown',
                            'equation_number': equation_number
                        })
                    else:
                        screenshot_path = os.path.join(self.images_dir, f"latex_{env_name}_eq_{equation_number}_{idx}.png")
                        if self._create_formula_screenshot(full_env, screenshot_path):
                            self.formulas['latex'].append({
                                'type': f'{env_name}_equation_{equation_number}',
                                'content': full_env,
                                'source': 'latex_screenshot',
                                'raw_data': full_env,
                                'image_path': screenshot_path,
                                'format': 'png',
                                'equation_number': equation_number
                            })
    
    def _extract_numbered_formula_from_latex(self, text, formula_pattern):
        """從 LaTeX 文本中提取帶編號的公式"""
        # LaTeX 中公式編號的常見模式
        patterns = [
            # 在公式後面的標籤和編號
            re.escape(formula_pattern) + r'\s*\\label\{[^}]*\}.*?\((\d+)\)',
            # 直接在公式後面的編號
            re.escape(formula_pattern) + r'\s*\((\d+)\)',
            # equation 環境會自動編號
            r'\\begin\{equation\}.*?' + re.escape(formula_pattern.replace('\\begin{equation}', '').replace('\\end{equation}', '')) + r'.*?\\end\{equation\}.*?\((\d+)\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                equation_number = match.group(1)
                return (formula_pattern, equation_number)
        
        # 如果沒有找到編號，嘗試從 \label{} 提取
        label_match = re.search(r'\\label\{([^}]*)\}', formula_pattern)
        if label_match:
            # 使用標籤名稱作為編號
            return (formula_pattern, label_match.group(1))
        
        return None
    
    def _is_meaningful_latex_formula(self, formula):
        """判斷 LaTeX 公式是否有意義"""
        if len(formula) < 3 or len(formula) > 150:
            return False
        
        # 包含重要數學元素
        important_patterns = [
            r'\\frac\{.*?\}\{.*?\}',  # 分數
            r'\\sum|\\int|\\prod|\\lim',  # 運算符
            r'\\sqrt\{.*?\}',  # 平方根
            r'[=+\-*/^_]',  # 基本運算
            r'[αβγδεζηθικλμνξοπρστυφχψω]',  # 希臘字母
            r'\\begin\{.*?\}',  # 環境
        ]
        
        score = 0
        for pattern in important_patterns:
            if re.search(pattern, formula):
                score += 1
        
        return score >= 2
    
    def _formula_complexity_score(self, formula):
        """計算公式複雜度分數"""
        score = 0
        score += len(re.findall(r'\\frac', formula)) * 3  # 分數
        score += len(re.findall(r'\\sum|\\int|\\prod', formula)) * 4  # 積分求和
        score += len(re.findall(r'[=+\-*/^_]', formula))  # 運算符
        score += len(re.findall(r'[αβγδεζηθικλμνξοπρστυφχψω]', formula)) * 2  # 希臘字母
        score += len(formula) // 10  # 長度獎勵
        return score
    
    def extract_pdf_formulas(self):
        """從 PDF 擷取公式，優先保存為文字內容"""
        pdf_path = os.path.join(self.base_dir, f"{self.arxiv_id}.pdf")
        
        try:
            # 下載 PDF
            response = requests.get(self.urls['pdf'])
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # 添加到 Markdown 文件
            with open(self.markdown_file, 'a', encoding='utf-8') as md_file:
                md_file.write("## PDF 格式公式\n\n")
            
            # 使用 PyMuPDF 擷取
            self._extract_pdf_with_pymupdf(pdf_path)
            
            # 如果沒有找到公式，嘗試 pdfplumber
            if not self.formulas['pdf']:
                self._extract_pdf_with_pdfplumber(pdf_path)
            
        except Exception as e:
            print(f"PDF 下載或處理失敗: {e}")
    
    def _extract_pdf_with_pymupdf(self, pdf_path):
        """使用 PyMuPDF 擷取 PDF 中的公式文字內容"""
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 擷取文字
                text = page.get_text()
                
                # 尋找數學符號和模式
                math_patterns = [
                    r'[∑∏∫∂∇∆Ω∅∞±×÷≤≥≠≈∈∉⊂⊃∪∩]',  # 數學符號
                    r'[αβγδεζηθικλμνξοπρστυφχψω]',  # 希臘字母
                    r'[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]',  # 大寫希臘字母
                    r'[a-zA-Z]\s*=\s*[^,.\s]+',  # 等式
                    r'\([^)]*[∑∏∫][^)]*\)',  # 包含積分求和的表達式
                ]
                
                # 尋找可能的公式區域（基於字體和位置）
                blocks = page.get_text("dict")
                
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                line_text += span["text"]
                            
                            # 尋找包含編號的公式行
                            numbered_formula = self._extract_numbered_formula_from_pdf(line_text)
                            if numbered_formula:
                                formula_content, equation_number = numbered_formula
                                
                                if self._save_formula_to_markdown(formula_content, 'PDF', f'equation_{equation_number}', page_num):
                                    self.formulas['pdf'].append({
                                        'type': f'equation_{equation_number}',
                                        'content': formula_content,
                                        'source': 'pdf_text',
                                        'page': page_num + 1,
                                        'raw_data': line_text,
                                        'format': 'markdown',
                                        'equation_number': equation_number
                                    })
                                else:
                                    # 無法保存為文字時，創建截圖
                                    bbox = line["bbox"]
                                    screenshot_path = self._crop_formula_region(doc, page_num, bbox, equation_number)
                                    if screenshot_path:
                                        self.formulas['pdf'].append({
                                            'type': f'equation_{equation_number}',
                                            'content': formula_content,
                                            'source': 'pdf_screenshot',
                                            'page': page_num + 1,
                                            'raw_data': f"bbox: {bbox}",
                                            'image_path': screenshot_path,
                                            'format': 'png',
                                            'equation_number': equation_number
                                        })
            
            doc.close()
            
        except Exception as e:
            print(f"PyMuPDF 處理失敗: {e}")
    
    def _extract_numbered_formula_from_pdf(self, line_text):
        """從 PDF 文本行中提取帶編號的公式"""
        # 尋找以編號結尾的公式行，如 "some formula content (1)"
        # 匹配模式：公式內容 + 空格 + (數字)
        pattern = r'^(.*?)(\s*\((\d+)\)\s*)$'
        match = re.match(pattern, line_text.strip())
        
        if match:
            formula_content = match.group(1).strip()
            equation_number = match.group(3)
            
            # 放寬檢查條件，重點檢查是否包含數學符號
            math_symbols = ['=', '∑', '∫', '∂', '→', '≤', '≥', '+', '-', '*', '/', '^', 
                           'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'φ', 'ω', 
                           'Q', 'K', 'V', 'W', 'softmax', 'Attention', 'head']
            
            # 檢查公式內容是否有意義（包含數學符號或關鍵字）
            if (len(formula_content) > 5 and 
                any(symbol in formula_content for symbol in math_symbols)):
                return (formula_content, equation_number)
        
        return None
    
    def _create_formula_screenshot(self, formula_text, screenshot_path):
        """創建公式截圖，改進圖片生成"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # 處理過長的公式文字
            if len(formula_text) > 60:
                wrapped_text = textwrap.fill(formula_text, width=60)
                lines = wrapped_text.split('\n')
            else:
                lines = [formula_text]
            
            # 計算圖片尺寸
            line_height = 25
            img_height = max(80, len(lines) * line_height + 30)
            max_line_length = max(len(line) for line in lines)
            img_width = max(300, min(800, max_line_length * 10))
            
            # 創建白色背景的圖片
            img = Image.new('RGB', (img_width, img_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # 嘗試載入更好的字體
            font = None
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/System/Library/Fonts/Arial.ttf',  # macOS
                'C:/Windows/Fonts/arial.ttf'  # Windows
            ]
            
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, 16)
                    break
                except:
                    continue
            
            if font is None:
                try:
                    font = ImageFont.load_default()
                except:
                    pass
            
            # 繪製邊框
            draw.rectangle([1, 1, img_width-2, img_height-2], outline='lightgray', width=1)
            
            # 繪製文字
            y_position = 15
            for line in lines:
                draw.text((10, y_position), line, fill='black', font=font)
                y_position += line_height
            
            # 儲存圖片
            img.save(screenshot_path, format='PNG', optimize=True)
            
            # 驗證文件是否正確創建
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 100:
                return screenshot_path
            else:
                print(f"⚠️ 圖片創建失敗或檔案太小: {screenshot_path}")
                return ""
                
        except Exception as e:
            print(f"創建公式截圖失敗: {e}")
            # 嘗試創建簡單的佔位圖片
            try:
                simple_img = Image.new('RGB', (200, 50), color='lightblue')
                simple_draw = ImageDraw.Draw(simple_img)
                simple_draw.text((5, 15), "Formula Image", fill='black')
                simple_img.save(screenshot_path)
                return screenshot_path if os.path.exists(screenshot_path) else ""
            except:
                return ""
    
    def _capture_pdf_page(self, doc, page_num):
        """截取 PDF 頁面圖片"""
        try:
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)  # 2x 放大
            pix = page.get_pixmap(matrix=mat)
            
            image_path = os.path.join(self.images_dir, f"pdf_page_{page_num + 1}.png")
            pix.save(image_path)
            pix = None  # 釋放記憶體
            
            return image_path
        except Exception as e:
            print(f"截取頁面失敗: {e}")
            return ""
    
    def _crop_formula_region(self, doc, page_num, bbox, equation_number=None):
        """裁切公式區域"""
        try:
            page = doc[page_num]
            
            # 擴展邊界框以包含更多上下文
            x0, y0, x1, y1 = bbox
            margin = 10
            crop_rect = fitz.Rect(
                max(0, x0 - margin),
                max(0, y0 - margin),
                min(page.rect.width, x1 + margin),
                min(page.rect.height, y1 + margin)
            )
            
            mat = fitz.Matrix(3.0, 3.0)  # 3x 放大以提高解析度
            pix = page.get_pixmap(matrix=mat, clip=crop_rect)
            
            if equation_number:
                image_path = os.path.join(self.images_dir, f"pdf_equation_{equation_number}_page_{page_num + 1}.png")
            else:
                image_path = os.path.join(self.images_dir, f"formula_crop_{page_num + 1}_{int(x0)}_{int(y0)}.png")
                
            pix.save(image_path)
            pix = None  # 釋放記憶體
            
            return image_path
        except Exception as e:
            print(f"裁切公式區域失敗: {e}")
            return ""
    
    def _extract_pdf_with_pdfplumber(self, pdf_path):
        """使用 pdfplumber 擷取 PDF 中的公式文字內容"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # 擷取文字
                    text = page.extract_text()
                    if text:
                        # 分割文本為行，專門尋找帶編號的公式
                        lines = text.split('\n')
                        for line in lines:
                            numbered_formula = self._extract_numbered_formula_from_pdf(line)
                            if numbered_formula:
                                formula_content, equation_number = numbered_formula
                                
                                if self._save_formula_to_markdown(formula_content, 'PDF', f'equation_{equation_number}', page_num):
                                    self.formulas['pdf'].append({
                                        'type': f'equation_{equation_number}',
                                        'content': formula_content,
                                        'source': 'pdfplumber_text',
                                        'page': page_num + 1,
                                        'raw_data': line,
                                        'format': 'markdown',
                                        'equation_number': equation_number
                                    })
                                else:
                                    # 創建截圖備選
                                    screenshot_path = os.path.join(self.images_dir, f"pdf_eq_{equation_number}_plumber_{page_num}.png")
                                    if self._create_formula_screenshot(formula_content, screenshot_path):
                                        self.formulas['pdf'].append({
                                            'type': f'equation_{equation_number}',
                                            'content': formula_content,
                                            'source': 'pdfplumber_screenshot',
                                            'page': page_num + 1,
                                            'raw_data': line,
                                            'image_path': screenshot_path,
                                            'format': 'png',
                                            'equation_number': equation_number
                                        })
                    
                    # 擷取表格中可能的公式
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            for row_idx, row in enumerate(table):
                                if row:
                                    for cell_idx, cell in enumerate(row):
                                        if cell and any(char in cell for char in ['=', '±', '×', '÷', '+', '-', '*', '/']):
                                            if self._is_meaningful_formula(cell):
                                                if self._save_formula_to_markdown(cell, 'PDF', 'table_formula', f"{table_idx}_{row_idx}_{cell_idx}"):
                                                    self.formulas['pdf'].append({
                                                        'type': 'table_formula',
                                                        'content': cell,
                                                        'source': 'pdfplumber_text',
                                                        'page': page_num + 1,
                                                        'raw_data': cell,
                                                        'format': 'markdown'
                                                    })
                                                else:
                                                    screenshot_path = os.path.join(self.images_dir, f"pdf_table_{page_num}_{table_idx}_{row_idx}_{cell_idx}.png")
                                                    if self._create_formula_screenshot(cell, screenshot_path):
                                                        self.formulas['pdf'].append({
                                                            'type': 'table_formula',
                                                            'content': cell,
                                                            'source': 'pdfplumber_screenshot',
                                                            'page': page_num + 1,
                                                            'raw_data': cell,
                                                            'image_path': screenshot_path,
                                                            'format': 'png'
                                                        })
        
        except Exception as e:
            print(f"pdfplumber 處理失敗: {e}")
    
    def merge_and_deduplicate(self):
        """合併和去重公式"""
        print("🔄 合併和去重公式...")
        
        # 收集所有公式
        all_formulas = []
        for format_type, formulas in self.formulas.items():
            for formula in formulas:
                formula['format'] = format_type
                all_formulas.append(formula)
        
        # 去重 (基於內容相似度)
        unique_formulas = []
        seen_contents = set()
        
        for formula in all_formulas:
            # 標準化內容用於比較
            normalized_content = re.sub(r'\s+', '', formula['content'].lower())
            normalized_content = re.sub(r'[{}$\\]', '', normalized_content)
            
            if normalized_content not in seen_contents and len(normalized_content) > 2:
                seen_contents.add(normalized_content)
                unique_formulas.append(formula)
        
        self.formulas['merged'] = unique_formulas
        print(f"✨ 去重後共 {len(unique_formulas)} 個唯一公式")
    
    # save_formulas 已移除，僅保留 filter_and_save_formulas

def main():
    """主函數"""
    print("🧮 arXiv 公式擷取器")
    print("=" * 50)
    
    # 輸入 arXiv 代碼
    arxiv_id = input("請輸入 arXiv 代碼 (例如: 2507.21856): ").strip()
    
    if not arxiv_id:
        print("❌ 請輸入有效的 arXiv 代碼")
        return
    
    # 創建擷取器並執行
    extractor = ArxivFormulaExtractor(arxiv_id)
    
    try:
        formulas = extractor.extract_all_formats()
        
        # 顯示統計結果
        print("\n📊 擷取統計:")
        print("-" * 30)
        for format_type, formula_list in formulas.items():
            if formula_list:
                print(f"{format_type.upper():>8}: {len(formula_list):>3} 個公式")
        
        print(f"\n✅ 擷取完成！結果已保存到: {extractor.base_dir}")
        
    except Exception as e:
        print(f"❌ 擷取過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()