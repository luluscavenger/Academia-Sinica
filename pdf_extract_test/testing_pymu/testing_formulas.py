#!/usr/bin/env python3
"""
PyMuPDF4LLM 數學公式提取工具
專門提取帶有編號標示的數學公式，如 (1), (2), (3) 等
"""

import os
import re
import pymupdf4llm
import pymupdf as fitz
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime

class FormulaExtractor:
    """使用 PyMuPDF4LLM 的數學公式提取器"""
    
    def __init__(self, output_dir: str = "testing-formula"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 數學公式模式
        self.formula_patterns = [
            # 帶編號的公式 (最重要)
            r'([^.!?]*?[=≈≡≤≥<>∝∞∑∏∫∇∂][^.!?]*?)\s*\((\d+)\)',  # 公式 (1)
            r'([^.!?]*?[α-ωΑ-Ωμνπρστθφψχξλκγδεζηιβ][^.!?]*?)\s*\((\d+)\)',  # 希臘字母公式 (1)
            
            # LaTeX 格式
            r'\$\$([^$]+)\$\$',  # 獨立數學環境
            r'\$([^$]+)\$',      # 行內數學
            r'\\begin\{equation\}(.*?)\\end\{equation\}',  # equation 環境
            r'\\begin\{align\}(.*?)\\end\{align\}',        # align 環境
            r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}',  # eqnarray 環境
            
            # 含特殊符號的表達式
            r'([A-Za-z][^.!?]*?[=≈≡≤≥<>±∓×÷∙·∘∗⊙⊗⊕][^.!?]*?[A-Za-z0-9αβγδεζηθικλμνξοπρστυφχψω])',
            
            # 單位和量綱
            r'([A-Za-z]+\s*=\s*[0-9.×\-\+\s]+\s*[A-Za-z/\-\+\s]*)',
            
            # 科學記數法
            r'([A-Za-z]+\s*[=≈]\s*[0-9.]+\s*×?\s*10[\-\+]?[0-9]+)',
        ]
        
        # 數學符號集合
        self.math_symbols = {
            'operators': '=≈≡≤≥<>±∓×÷∙·∘∗⊙⊗⊕⊖⊘⊚⊛⊜⊝⊞⊟⊠⊡',
            'greek': 'αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ',
            'calculus': '∫∬∭∮∯∰∱∲∳∑∏∐∇∂',
            'relations': '∈∉∋∌∍⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋',
            'special': '∞∝√∛∜∅∪∩∧∨¬→←↑↓↔'
        }
        
    def extract_formulas_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """從 PDF 提取數學公式"""
        print(f"🔬 開始提取PDF數學公式: {pdf_path}")
        
        results = {
            'numbered_formulas': [],  # 帶編號的公式
            'latex_formulas': [],     # LaTeX 格式公式
            'inline_formulas': [],    # 行內公式
            'other_formulas': [],     # 其他公式
            'all_formulas': [],       # 所有提取的公式
            'statistics': {}
        }
        
        try:
            # Use pymupdf4llm to extract markdown format
            print("📖 Using pymupdf4llm to extract markdown format...")
            md_text = pymupdf4llm.to_markdown(pdf_path)
            
            # Analyze formulas in markdown content
            self._extract_from_markdown(md_text, results)
            
            # Use PyMuPDF to get raw text for additional extraction
            print("📖 Using PyMuPDF to get raw text...")
            doc = fitz.open(pdf_path)
            raw_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                raw_text += page.get_text()
            doc.close()
            
            # Extract formulas from raw text
            self._extract_from_raw_text(raw_text, results)
            
            # 去重和排序
            self._process_and_deduplicate(results)
            
            # 去重並排序帶編號的公式
            self._deduplicate_and_sort_formulas(results)
            
            # 統計信息
            results['statistics'] = {
                'total_formulas': len(results['all_formulas']),
                'numbered_formulas': len(results['numbered_formulas']),
                'latex_formulas': len(results['latex_formulas']),
                'inline_formulas': len(results['inline_formulas'])
            }
            
            print(f"✅ Formula extraction completed:")
            print(f"   📊 Total formulas: {results['statistics']['total_formulas']}")
            print(f"   🔢 Numbered formulas: {results['statistics']['numbered_formulas']}")
            if results['numbered_formulas']:
                numbers = [f['number'] for f in results['numbered_formulas']]
                print(f"   📋 Formula numbers: {sorted(numbers)}")
            print(f"   📐 LaTeX formulas: {results['statistics']['latex_formulas']}")
            print(f"   📝 Inline formulas: {results['statistics']['inline_formulas']}")
            
        except Exception as e:
            print(f"❌ Error during extraction: {str(e)}")
            
        return results
    
    def _deduplicate_and_sort_formulas(self, results: Dict[str, Any]):
        """Deduplicate and sort formulas"""
        
        # Deduplicate and sort numbered formulas
        unique_numbered = {}
        for formula_data in results['numbered_formulas']:
            number = formula_data['number']
            # 如果編號不存在，或者新的公式更長（可能更完整），則使用新的
            if (number not in unique_numbered or 
                len(formula_data['formula']) > len(unique_numbered[number]['formula'])):
                unique_numbered[number] = formula_data
        
        # 按編號排序
        results['numbered_formulas'] = sorted(unique_numbered.values(), key=lambda x: x['number'])
        
        # 其他公式去重
        unique_others = []
        seen_formulas = set()
        
        for formula_data in results['other_formulas']:
            formula_clean = formula_data['formula'].replace(' ', '').lower()
            if formula_clean not in seen_formulas:
                seen_formulas.add(formula_clean)
                unique_others.append(formula_data)
        
        results['other_formulas'] = unique_others
        
        # 更新總公式列表
        results['all_formulas'] = (results['numbered_formulas'] + 
                                 results['latex_formulas'] + 
                                 results['inline_formulas'] + 
                                 results['other_formulas'])
    
    def _extract_from_markdown(self, md_text: str, results: Dict[str, Any]):
        """從 markdown 文本中提取公式"""
        
        # 預處理：清理換行和多餘空格
        text = re.sub(r'\n+', ' ', md_text)
        text = re.sub(r'\s+', ' ', text)
        
        # 改進的帶編號公式提取
        # 尋找 (數字) 模式，然後往前找公式
        numbered_formula_patterns = [
            # 模式1: 公式內容 (數字)
            r'([^.!?\n]{10,200}?(?:[=≈≡≤≥<>∝∞∑∏∫∇∂±×÷]|[α-ωΑ-Ω])[^.!?\n]{5,100}?)\s*\((\d+)\)',
            
            # 模式2: 更寬鬆的數學表達式 (數字)
            r'([A-Za-z_]+[^.!?\n]{5,150}?[=≈≡≤≥<>∝±×÷][^.!?\n]{5,100}?)\s*\((\d+)\)',
            
            # 模式3: 包含希臘字母的表達式 (數字)
            r'([^.!?\n]{5,150}?[α-ωΑ-Ωμνπρστθφψχξλκγδεζηιβ][^.!?\n]{5,100}?)\s*\((\d+)\)',
            
            # 模式4: 包含數學符號的表達式 (數字)
            r'([^.!?\n]{5,150}?[∫∑∏∇∂∞∝√][^.!?\n]{5,100}?)\s*\((\d+)\)'
        ]
        
        all_numbered_matches = []
        
        for pattern in numbered_formula_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                formula_text = match.group(1).strip()
                formula_number = match.group(2)
                
                # 清理公式文本
                formula_text = self._clean_formula_text(formula_text)
                
                if self._is_valid_numbered_formula(formula_text, formula_number):
                    all_numbered_matches.append({
                        'formula': formula_text,
                        'number': int(formula_number),
                        'type': 'numbered',
                        'source': 'markdown'
                    })
        
        # 去重並按編號排序
        unique_formulas = {}
        for formula_data in all_numbered_matches:
            key = formula_data['number']
            if key not in unique_formulas or len(formula_data['formula']) > len(unique_formulas[key]['formula']):
                unique_formulas[key] = formula_data
        
        # 轉換回列表並排序
        results['numbered_formulas'] = sorted(unique_formulas.values(), key=lambda x: x['number'])
        
        # 尋找缺失的編號並嘗試補充
        self._find_missing_numbered_formulas(text, results)
        
        # 提取 LaTeX 格式公式
        latex_patterns = [
            r'\$\$([^$]+)\$\$',
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{align\}(.*?)\\end\{align\}',
            r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}'
        ]
        
        for pattern in latex_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                formula = match.group(1).strip()
                if formula and len(formula) > 2:
                    results['latex_formulas'].append({
                        'formula': formula,
                        'type': 'latex',
                        'source': 'markdown'
                    })
        
        # 提取行內數學公式
        inline_pattern = r'\$([^$\n]{3,50})\$'
        inline_matches = re.finditer(inline_pattern, text)
        
        for match in inline_matches:
            formula = match.group(1).strip()
            if self._is_valid_formula(formula) and len(formula) > 2:
                results['inline_formulas'].append({
                    'formula': formula,
                    'type': 'inline',
                    'source': 'markdown'
                })
    
    def _find_missing_numbered_formulas(self, text: str, results: Dict[str, Any]):
        """尋找缺失的編號公式"""
        
        # 找出目前已有的編號
        existing_numbers = set(f['number'] for f in results['numbered_formulas'])
        
        # 在文本中搜索所有 (數字) 模式
        all_numbers = set()
        number_pattern = r'\((\d+)\)'
        for match in re.finditer(number_pattern, text):
            num = int(match.group(1))
            if 1 <= num <= 50:  # 合理的公式編號範圍
                all_numbers.add(num)
        
        # Find missing numbers
        missing_numbers = all_numbers - existing_numbers
        
        print(f"   🔍 Found numbers: {sorted(all_numbers)}")
        print(f"   ✅ Extracted: {sorted(existing_numbers)}")
        if missing_numbers:
            print(f"   ❓ Missing numbers: {sorted(missing_numbers)}")
        
        # Try to find formulas for missing numbers
        for num in missing_numbers:
            formula = self._extract_specific_numbered_formula(text, num)
            if formula:
                results['numbered_formulas'].append({
                    'formula': formula,
                    'number': num,
                    'type': 'numbered',
                    'source': 'markdown_recovery'
                })
                print(f"   🔧 Recovered formula ({num}): {formula[:50]}...")
    
    def _extract_specific_numbered_formula(self, text: str, target_number: int) -> str:
        """嘗試提取特定編號的公式"""
        
        # 尋找 (target_number) 及其前後文
        pattern = rf'(.{{50,300}}?)\s*\({target_number}\)'
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            context = match.group(1).strip()
            
            # 嘗試從上下文中提取公式
            # 從後往前找到一個完整的數學表達式
            sentences = re.split(r'[.!?]\s+', context)
            for sentence in reversed(sentences):
                sentence = sentence.strip()
                if self._is_valid_numbered_formula(sentence, str(target_number)):
                    return self._clean_formula_text(sentence)
        
        return None
    
    def _clean_formula_text(self, text: str) -> str:
        """清理公式文本"""
        # 移除多餘的空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除開頭的非數學字符
        text = re.sub(r'^[^A-Za-z0-9α-ωΑ-Ω∑∏∫∇∂=≈≡]+', '', text)
        
        # 移除結尾的非數學字符（但保留括號）
        text = re.sub(r'[^A-Za-z0-9α-ωΑ-Ω∑∏∫∇∂=≈≡≤≥<>±×÷·∙()[\]{}.,\s]+$', '', text)
        
        return text.strip()
    
    def _is_valid_numbered_formula(self, text: str, number: str) -> bool:
        """檢查是否為有效的帶編號公式"""
        if not text or len(text.strip()) < 5:
            return False
            
        text = text.strip()
        
        # 編號必須是數字
        try:
            num = int(number)
            if num < 1 or num > 100:  # 合理的編號範圍
                return False
        except ValueError:
            return False
        
        # 檢查是否包含數學內容
        all_symbols = ''.join(self.math_symbols.values())
        has_math_symbol = any(char in all_symbols for char in text)
        has_variable = bool(re.search(r'[A-Za-z]', text))
        has_number_or_subscript = bool(re.search(r'[0-9_]', text))
        
        # 排除純文字描述
        if '.' in text and text.count(' ') > 8 and not has_math_symbol:
            return False
            
        # 必須包含數學符號或變數
        return has_math_symbol or (has_variable and has_number_or_subscript)
    
    def _extract_from_raw_text(self, raw_text: str, results: Dict[str, Any]):
        """從原始文本中提取公式"""
        
        # 清理文本，但保留段落結構
        text = re.sub(r'\n{3,}', '\n\n', raw_text)  # 保留段落分隔
        text = re.sub(r'[ \t]+', ' ', text)  # 清理空格但保留換行
        
        # 先找出所有可能的編號位置
        existing_numbered = {f['number'] for f in results['numbered_formulas']}
        
        # 更精確的帶編號公式提取
        numbered_patterns = [
            # 模式1: 行內公式 (數字)
            r'([^\n.!?]{15,300}?(?:[=≈≡≤≥<>∝∞∑∏∫∇∂±×÷]|[α-ωΑ-Ω])[^\n.!?]{10,200}?)\s*\((\d+)\)',
            
            # 模式2: 跨行公式 (數字)
            r'([^\n]{10,200}?\n[^\n]{10,200}?(?:[=≈≡≤≥<>∝∞∑∏∫∇∂±×÷]|[α-ωΑ-Ω])[^\n]{5,150}?)\s*\((\d+)\)',
            
            # 模式3: 變數定義型公式 (數字)
            r'(\b[A-Za-z_][A-Za-z0-9_]*[^\n.!?]{5,200}?[=≈≡≤≥<>∝][^\n.!?]{5,150}?)\s*\((\d+)\)',
            
            # 模式4: 包含希臘字母的公式 (數字)
            r'([^\n.!?]{5,250}?[α-ωΑ-Ωμνπρστθφψχξλκγδεζηιβ][^\n.!?]{5,150}?)\s*\((\d+)\)'
        ]
        
        for pattern in numbered_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                formula_text = match.group(1).strip()
                formula_number = match.group(2)
                
                # 清理和標準化公式文本
                formula_text = self._clean_formula_text(formula_text)
                
                # 檢查是否已存在
                if (formula_number not in existing_numbered and 
                    self._is_valid_numbered_formula(formula_text, formula_number)):
                    
                    # 檢查是否與已有公式重複（內容相似）
                    is_duplicate = False
                    for existing in results['numbered_formulas']:
                        if (self._similarity_ratio(formula_text, existing['formula']) > 0.8 or
                            formula_number == str(existing['number'])):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        results['numbered_formulas'].append({
                            'formula': formula_text,
                            'number': int(formula_number),
                            'type': 'numbered',
                            'source': 'raw_text'
                        })
                        existing_numbered.add(formula_number)
                        print(f"   📝 Supplemented formula from raw text ({formula_number}): {formula_text[:50]}...")
        
        # 提取包含特殊符號的其他公式
        special_symbols_pattern = rf'([^\n.!?]{{15,200}}?[{re.escape("".join(self.math_symbols.values()))}][^\n.!?]{{10,150}}?)'
        special_matches = re.finditer(special_symbols_pattern, text, re.MULTILINE)
        
        for match in special_matches:
            formula = match.group(1).strip()
            formula = self._clean_formula_text(formula)
            
            if self._is_valid_formula(formula) and len(formula) > 15:
                # 避免與已有的帶編號公式重複
                is_duplicate = any(
                    self._similarity_ratio(formula, existing['formula']) > 0.7
                    for existing in results['numbered_formulas'] + results['other_formulas']
                )
                
                if not is_duplicate:
                    results['other_formulas'].append({
                        'formula': formula,
                        'type': 'special_symbols',
                        'source': 'raw_text'
                    })
    
    def _similarity_ratio(self, text1: str, text2: str) -> float:
        """計算兩個文本的相似度"""
        # 簡單的字符集合相似度計算
        set1 = set(text1.lower().replace(' ', ''))
        set2 = set(text2.lower().replace(' ', ''))
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _is_valid_formula(self, text: str) -> bool:
        """檢查是否為有效的數學公式"""
        if not text or len(text.strip()) < 3:
            return False
            
        text = text.strip()
        
        # 檢查是否包含數學符號
        all_symbols = ''.join(self.math_symbols.values())
        has_math_symbol = any(char in all_symbols for char in text)
        
        # 檢查是否包含數字和變數
        has_variable = bool(re.search(r'[A-Za-z]', text))
        has_number = bool(re.search(r'[0-9]', text))
        
        # 排除純文字句子
        if text.count(' ') > 10 and not has_math_symbol:
            return False
            
        # 必須包含數學符號，或者包含變數和數字
        return has_math_symbol or (has_variable and has_number)
    
    def _process_and_deduplicate(self, results: Dict[str, Any]):
        """處理和去重公式"""
        
        # 合併所有公式
        all_formulas = (results['numbered_formulas'] + 
                       results['latex_formulas'] + 
                       results['inline_formulas'])
        
        # 去重
        seen_formulas = set()
        unique_formulas = []
        
        for formula_data in all_formulas:
            formula_key = formula_data['formula'].strip().lower()
            if formula_key not in seen_formulas:
                seen_formulas.add(formula_key)
                unique_formulas.append(formula_data)
        
        results['all_formulas'] = unique_formulas
        
        # 對帶編號的公式按編號排序
        results['numbered_formulas'].sort(key=lambda x: int(x.get('number', 0)))
    
    def save_formulas_to_file(self, pdf_path: str, results: Dict[str, Any]) -> str:
        """Save formulas to file in English"""
        pdf_name = Path(pdf_path).stem
        output_file = self.output_dir / f"{pdf_name}_formulas.md"
        
        # Filter out text descriptions from numbered formulas
        filtered_numbered_formulas = []
        for formula_data in results['numbered_formulas']:
            if self._is_real_mathematical_formula(formula_data['formula']):
                filtered_numbered_formulas.append(formula_data)
            else:
                print(f"   🗑️ Filtered out text description: ({formula_data['number']}) {formula_data['formula'][:50]}...")
        
        # Update results with filtered formulas
        results['numbered_formulas'] = filtered_numbered_formulas
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📐 Mathematical Formula Extraction Results: {pdf_name}\n\n")
            f.write(f"**Extraction Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Source File**: {pdf_path}\n\n")
            
            # Statistics
            stats = results['statistics']
            # Update stats after filtering
            stats['numbered_formulas'] = len(filtered_numbered_formulas)
            stats['total_formulas'] = len(filtered_numbered_formulas) + stats['latex_formulas'] + stats['inline_formulas']
            
            f.write("## 📊 Statistics Summary\n\n")
            f.write(f"- **Total Formulas**: {stats['total_formulas']}\n")
            f.write(f"- **Numbered Formulas**: {stats['numbered_formulas']}\n")
            f.write(f"- **LaTeX Formulas**: {stats['latex_formulas']}\n")
            f.write(f"- **Inline Formulas**: {stats['inline_formulas']}\n\n")
            
            # Numbered formulas (most important)
            if filtered_numbered_formulas:
                f.write("## 🔢 Numbered Formulas\n\n")
                for formula_data in filtered_numbered_formulas:
                    f.write(f"**Formula ({formula_data['number']})**:\n")
                    f.write(f"```\n{formula_data['formula']}\n```\n")
                    f.write(f"*Source: {formula_data['source']}*\n\n")
            else:
                f.write("## 🔢 Numbered Formulas\n\n")
                f.write("No numbered mathematical formulas found in this document.\n\n")
            
            # LaTeX formulas
            if results['latex_formulas']:
                f.write("## 📐 LaTeX Format Formulas\n\n")
                for i, formula_data in enumerate(results['latex_formulas'], 1):
                    f.write(f"**LaTeX Formula {i}**:\n")
                    f.write(f"```latex\n{formula_data['formula']}\n```\n")
                    f.write(f"*Source: {formula_data['source']}*\n\n")
            
            # Inline formulas
            if results['inline_formulas']:
                f.write("## 📝 Inline Mathematical Formulas\n\n")
                for i, formula_data in enumerate(results['inline_formulas'], 1):
                    f.write(f"**Inline Formula {i}**: `{formula_data['formula']}`\n\n")
            
            # Complete formula list
            if filtered_numbered_formulas or results['latex_formulas'] or results['inline_formulas']:
                f.write("## 📋 Complete Formula List\n\n")
                counter = 1
                for formula_data in filtered_numbered_formulas:
                    f.write(f"{counter}. **Numbered Formula ({formula_data['number']})**: {formula_data['formula']}\n")
                    counter += 1
                for formula_data in results['latex_formulas']:
                    f.write(f"{counter}. **LaTeX Formula**: {formula_data['formula']}\n")
                    counter += 1
                for formula_data in results['inline_formulas']:
                    f.write(f"{counter}. **Inline Formula**: {formula_data['formula']}\n")
                    counter += 1
            else:
                f.write("## 📋 Complete Formula List\n\n")
                f.write("No mathematical formulas found in this document.\n")
        
        return str(output_file)
    
    def _is_real_mathematical_formula(self, text: str) -> bool:
        """Enhanced validation to ensure text is a real mathematical formula"""
        if not text or len(text.strip()) < 3:
            return False
            
        text = text.strip()
        
        # Check for mathematical content first
        math_symbols = ['=', '≈', '≡', '≤', '≥', '<', '>', '∝', '∞', '∑', '∏', '∫', '∇', '∂', '±', '×', '÷', '→', '←', '↔']
        greek_letters = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω',
                        'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω']
        
        has_math_symbol = any(symbol in text for symbol in math_symbols)
        has_greek = any(letter in text for letter in greek_letters)
        has_subscript_superscript = bool(re.search(r'[_^]', text))
        has_variables = bool(re.search(r'\b[A-Za-z]\b', text))
        has_numbers = bool(re.search(r'\d', text))
        
        # Check for clear mathematical patterns
        has_equation = bool(re.search(r'[A-Za-z_]+\s*[=≈≡]\s*', text))
        has_fraction = bool(re.search(r'[A-Za-z_]+\s*/\s*[A-Za-z_]+', text))
        has_power = bool(re.search(r'[A-Za-z_]+\s*\^\s*[A-Za-z0-9_]+', text))
        has_matrix_bracket = bool(re.search(r'[\[\(\{].*[\]\)\}]', text))
        
        # Strong mathematical indicators
        strong_math_indicators = has_math_symbol or has_greek or has_equation or has_fraction or has_power
        
        # If it has strong mathematical content, it's likely a formula
        if strong_math_indicators:
            return True
        
        # Check for problematic text patterns that indicate pure description
        problematic_phrases = [
            'due to energy conservation',
            'after the fireball simulation',
            'strong ramp-up',
            'emission of heavier nuclei',
            'the rough criteria to choose',
            'the spread describes',
            'if we include',
            'the energy ejected as',
            'prior model',
            'we specify',
            'starting from the',
            'completes, the',
            'examples we motivated'
        ]
        
        text_lower = text.lower()
        for phrase in problematic_phrases:
            if phrase in text_lower:
                return False
        
        # If text starts with descriptive words, likely not a formula
        descriptive_starts = [
            'due to', 'after the', 'the rough', 'emission of', 'if we',
            'the energy', 'prior model', 'we specify', 'starting from'
        ]
        
        for start in descriptive_starts:
            if text_lower.startswith(start):
                return False
        
        # Check for excessive English text vs mathematical content ratio
        words = text.split()
        if len(words) > 10:  # Long text
            math_word_count = 0
            for word in words:
                if (any(symbol in word for symbol in math_symbols) or 
                    any(letter in word for letter in greek_letters) or
                    bool(re.search(r'[_^]', word)) or
                    bool(re.search(r'^[A-Za-z]$', word))):  # Single letter variables
                    math_word_count += 1
            
            # If less than 30% mathematical content in long text, likely description
            if math_word_count / len(words) < 0.3:
                return False
        
        # For shorter text with some mathematical content
        if (has_subscript_superscript or has_variables) and len(text) < 100:
            return True
        
        # Final check: if it has mathematical symbols and reasonable length
        if has_math_symbol and len(text) < 150:
            return True
            
        return False
    
    def process_pdf(self, pdf_path: str) -> str:
        """處理單個 PDF 檔案"""
        results = self.extract_formulas_from_pdf(pdf_path)
        output_file = self.save_formulas_to_file(pdf_path, results)
        return output_file

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
    """Main function"""
    print("🔬 PyMuPDF4LLM Mathematical Formula Extraction Tool")
    print("Specialized in extracting numbered formulas like (1), (2), (3)")
    print("=" * 60)
    
    # PDF file list
    pdf_files = ['paper1.pdf', 'paper2.pdf', 'paper3.pdf']
    
    # Create extractor
    extractor = FormulaExtractor()
    
    # Process each PDF
    for pdf_filename in pdf_files:
        # Find the actual path to the PDF file
        pdf_path = find_pdf_file(pdf_filename)
        if not pdf_path:
            print(f"❌ File not found: {pdf_filename}")
            continue
            
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_filename} -> {pdf_path}")
        print(f"{'='*60}")
        
        try:
            output_file = extractor.process_pdf(pdf_path)
            print(f"✅ **Formula extraction completed**: `{output_file}`")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_filename}: {str(e)}")
            continue
    
    print(f"\n🎉 All PDF formula extraction completed! Results saved in: ./{extractor.output_dir}/")

if __name__ == "__main__":
    main()