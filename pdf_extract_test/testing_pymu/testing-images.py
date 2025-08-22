#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF圖片提取工具
專門用於從PDF文件中提取圖片並保存到輸出目錄
處理 paper1.pdf, paper2.pdf, paper3.pdf
"""

import os
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf as fitz
from PIL import Image
import numpy as np

class PDFImageExtractor:
    """PDF圖片提取器類別"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 導入模組
        self.fitz = fitz
        self.Image = Image
    
    def extract_images(self, pdf_path: str) -> List[Dict[str, Any]]:
        """改進的圖片提取，智能識別真正的圖表區域"""
        print(f"🖼️ 提取圖片: {Path(pdf_path).name}")
        
        images = []
        try:
            pdf_doc = self.fitz.open(pdf_path)
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                
                # 方法1: 提取嵌入的圖片物件
                image_list = page.get_images()
                print(f"   📄 頁面 {page_num+1}: 找到 {len(image_list)} 個嵌入圖片物件")
                
                # 先檢查是否有多個小圖片可以組合成大圖
                embedded_images = self._extract_embedded_images(page, page_num, pdf_path, image_list, pdf_doc)
                
                # 檢查是否需要組合圖片
                if len(embedded_images) > 3:  # 如果有多個小圖片
                    combined_image = self._try_combine_images(embedded_images, page, page_num, pdf_path)
                    if combined_image:
                        images.append(combined_image)
                        print(f"      ✅ 組合圖片: {combined_image['filename']} (組合了{len(embedded_images)}個片段)")
                    else:
                        # 如果組合失敗，加入個別圖片
                        images.extend(embedded_images)
                else:
                    images.extend(embedded_images)
                
                # 方法2: 只有在沒有找到有效嵌入圖片時，才嘗試頁面截圖法
                if len(embedded_images) == 0:
                    print(f"      🔄 沒有找到嵌入圖片，嘗試頁面圖形分析...")
                    page_images = self._extract_page_graphics_smart(page, page_num, pdf_path)
                    images.extend(page_images)
            
            pdf_doc.close()
            print(f"✅ 總共提取 {len(images)} 張高品質圖片")
            
        except Exception as e:
            print(f"❌ 圖片提取失敗: {e}")
            
        return images
    
    def _extract_embedded_images(self, page, page_num: int, pdf_path: str, image_list, pdf_doc) -> List[Dict[str, Any]]:
        """提取嵌入的圖片物件"""
        embedded_images = []
        
        for img_index, img in enumerate(image_list):
            try:
                # 提取圖片
                xref = img[0]
                pix = self.fitz.Pixmap(pdf_doc, xref)  # 使用pdf_doc而不是page.pdf
                
                # 圖片品質檢查
                if not self._is_valid_image(pix):
                    print(f"      ⚠️ 跳過低品質圖片 {img_index+1}: 尺寸 {pix.width}x{pix.height}")
                    pix = None
                    continue
                
                if pix.n - pix.alpha < 4:  # 確保是RGB圖片
                    if self._is_meaningful_image(pix):
                        # 生成圖片檔名
                        img_filename = f"{Path(pdf_path).stem}_page{page_num+1}_obj{img_index+1}.png"
                        img_path = self.output_dir / img_filename
                        
                        # 保存圖片
                        pix.save(str(img_path))
                        
                        # 計算圖片統計信息
                        stats = self._calculate_image_stats(pix)
                        
                        embedded_images.append({
                            'filename': img_filename,
                            'path': str(img_path),
                            'page': page_num + 1,
                            'index': img_index + 1,
                            'width': pix.width,
                            'height': pix.height,
                            'extraction_method': 'embedded_object',
                            'quality_score': stats['quality_score'],
                            'color_variance': stats['color_variance'],
                            'non_white_ratio': stats['non_white_ratio'],
                            'bbox': img[1:5] if len(img) > 4 else None  # 保存位置信息
                        })
                        
                        print(f"      ✅ 找到嵌入圖片: {img_filename} ({pix.width}x{pix.height}) 品質: {stats['quality_score']:.2f}")
                    else:
                        print(f"      ❌ 跳過無意義圖片 {img_index+1}: 主要為空白或單色")
                else:
                    print(f"      ⚠️ 跳過非RGB圖片 {img_index+1}")
                
                pix = None
            except Exception as e:
                print(f"      ❌ 圖片提取失敗 (頁面{page_num+1}, 圖片{img_index+1}): {e}")
        
        return embedded_images
    
    def _try_combine_images(self, embedded_images: List[Dict], page, page_num: int, pdf_path: str) -> Optional[Dict[str, Any]]:
        """嘗試組合多個小圖片成為一個大圖表"""
        try:
            if len(embedded_images) < 4:
                return None
            
            # 分析圖片的位置分佈
            positions = []
            for img in embedded_images:
                if img['bbox']:
                    x0, y0, x1, y1 = img['bbox']
                    positions.append({
                        'img': img,
                        'center_x': (x0 + x1) / 2,
                        'center_y': (y0 + y1) / 2,
                        'bbox': (x0, y0, x1, y1)
                    })
            
            if len(positions) < 4:
                return None
            
            # 檢查是否形成規則的網格佈局
            x_coords = sorted(set(pos['center_x'] for pos in positions))
            y_coords = sorted(set(pos['center_y'] for pos in positions))
            
            # 如果有2x2或更大的網格，可能是組合圖表
            if len(x_coords) >= 2 and len(y_coords) >= 2:
                # 計算整個圖表區域的邊界
                min_x = min(pos['bbox'][0] for pos in positions)
                min_y = min(pos['bbox'][1] for pos in positions)
                max_x = max(pos['bbox'][2] for pos in positions)
                max_y = max(pos['bbox'][3] for pos in positions)
                
                # 添加一些邊距
                margin = 20
                chart_region = self.fitz.Rect(min_x - margin, min_y - margin, max_x + margin, max_y + margin)
                
                # 檢查區域是否合理
                width = chart_region.x1 - chart_region.x0
                height = chart_region.y1 - chart_region.y0
                
                if width > 200 and height > 150 and width < 800 and height < 600:
                    # 截圖整個圖表區域
                    mat = self.fitz.Matrix(2.0, 2.0)  # 高解析度
                    pix = page.get_pixmap(matrix=mat, clip=chart_region)
                    
                    if self._is_meaningful_page_image(pix):
                        # 生成組合圖片檔名
                        img_filename = f"{Path(pdf_path).stem}_page{page_num+1}_combined.png"
                        img_path = self.output_dir / img_filename
                        
                        # 保存圖片
                        pix.save(str(img_path))
                        
                        # 計算統計信息
                        stats = self._calculate_image_stats(pix)
                        
                        # 刪除個別的小圖片文件
                        for img in embedded_images:
                            try:
                                if os.path.exists(img['path']):
                                    os.remove(img['path'])
                            except:
                                pass
                        
                        pix = None
                        
                        return {
                            'filename': img_filename,
                            'path': str(img_path),
                            'page': page_num + 1,
                            'index': 1,
                            'width': pix.width if pix else int(width * 2),
                            'height': pix.height if pix else int(height * 2),
                            'extraction_method': 'combined_chart',
                            'quality_score': stats['quality_score'],
                            'color_variance': stats['color_variance'],
                            'non_white_ratio': stats['non_white_ratio']
                        }
            
        except Exception as e:
            print(f"      ❌ 組合圖片失敗: {e}")
        
        return None
    
    def _extract_page_graphics_smart(self, page, page_num: int, pdf_path: str) -> List[Dict[str, Any]]:
        """智能頁面圖形提取，只提取真正包含圖表的區域"""
        graphics = []
        
        try:
            # 獲取頁面文字和繪圖信息
            text_blocks = page.get_text("dict")["blocks"]
            drawings = page.get_drawings()
            
            print(f"         📐 找到 {len(drawings)} 個繪圖對象")
            
            # 如果繪圖對象太少，可能不是圖表頁面
            if len(drawings) < 10:
                print(f"         ❌ 繪圖對象太少，跳過")
                return graphics
            
            # 分析文字分佈
            text_coverage = self._analyze_text_coverage(page, text_blocks)
            print(f"         📊 文字覆蓋率: {text_coverage:.1%}")
            
            # 只有在特定條件下才進行截圖
            should_extract = False
            extraction_reason = ""
            
            # 條件1: 繪圖對象很多且文字覆蓋率適中 (可能有圖表)
            if len(drawings) > 100 and 0.2 < text_coverage < 0.7:
                should_extract = True
                extraction_reason = "大量繪圖對象 + 適中文字覆蓋率"
            
            # 條件2: 繪圖對象非常多 (複雜圖表)
            elif len(drawings) > 500:
                should_extract = True
                extraction_reason = "超多繪圖對象，可能為複雜圖表"
            
            # 條件3: 文字很少但有一定繪圖對象 (圖表頁面)
            elif len(drawings) > 50 and text_coverage < 0.3:
                should_extract = True
                extraction_reason = "少量文字 + 中等繪圖對象"
            
            if should_extract:
                print(f"         ✅ 提取條件滿足: {extraction_reason}")
                
                # 嘗試找到圖表區域
                chart_regions = self._identify_chart_regions_smart(drawings, page)
                
                for i, region in enumerate(chart_regions):
                    if self._is_valid_chart_region(region):
                        # 截圖該區域
                        mat = self.fitz.Matrix(2.0, 2.0)  # 2倍縮放
                        pix = page.get_pixmap(matrix=mat, clip=region)
                        
                        if self._is_meaningful_page_image(pix):
                            # 生成圖片檔名
                            img_filename = f"{Path(pdf_path).stem}_page{page_num+1}_chart{i+1}.png"
                            img_path = self.output_dir / img_filename
                            
                            # 保存圖片
                            pix.save(str(img_path))
                            
                            # 計算統計信息
                            stats = self._calculate_image_stats(pix)
                            
                            graphics.append({
                                'filename': img_filename,
                                'path': str(img_path),
                                'page': page_num + 1,
                                'index': i + 1,
                                'width': pix.width,
                                'height': pix.height,
                                'extraction_method': 'smart_graphics',
                                'quality_score': stats['quality_score'],
                                'color_variance': stats['color_variance'],
                                'non_white_ratio': stats['non_white_ratio']
                            })
                            
                            print(f"         ✅ 保存圖表區域: {img_filename} ({pix.width}x{pix.height}) 品質: {stats['quality_score']:.2f}")
                        
                        pix = None
            else:
                print(f"         ❌ 不滿足圖表提取條件，跳過")
                
        except Exception as e:
            print(f"         ❌ 智能圖形提取失敗: {e}")
        
        return graphics
    
    def _analyze_text_coverage(self, page, text_blocks) -> float:
        """分析頁面的文字覆蓋率"""
        try:
            page_area = (page.rect.x1 - page.rect.x0) * (page.rect.y1 - page.rect.y0)
            text_area = 0
            
            for block in text_blocks:
                if "lines" in block:  # 文字塊
                    bbox = block["bbox"]
                    block_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    text_area += block_area
            
            return text_area / page_area if page_area > 0 else 0
        except:
            return 0.5  # 預設值
    
    def _identify_chart_regions_smart(self, drawings, page) -> List:
        """智能識別圖表區域"""
        import numpy as np
        
        if not drawings:
            return []
        
        # 提取所有繪圖對象的邊界
        coords = []
        for drawing in drawings:
            if 'rect' in drawing and drawing['rect']:
                rect = drawing['rect']
                coords.append([rect.x0, rect.y0, rect.x1, rect.y1])
        
        if not coords:
            return []
        
        coords = np.array(coords)
        
        # 計算繪圖對象的密度分佈
        regions = []
        
        # 方法1: 找到包含大部分繪圖對象的區域
        min_x, min_y = np.min(coords[:, [0, 1]], axis=0)
        max_x, max_y = np.max(coords[:, [2, 3]], axis=0)
        
        # 添加適當邊距
        margin = 30
        total_region = self.fitz.Rect(
            max(0, min_x - margin),
            max(0, min_y - margin),
            min(page.rect.x1, max_x + margin),
            min(page.rect.y1, max_y + margin)
        )
        
        # 檢查區域大小
        width = total_region.x1 - total_region.x0
        height = total_region.y1 - total_region.y0
        
        if 200 < width < 600 and 150 < height < 500:
            regions.append(total_region)
        
        return regions
    
    def _is_valid_chart_region(self, region) -> bool:
        """檢查是否為有效的圖表區域"""
        width = region.x1 - region.x0
        height = region.y1 - region.y0
        
        # 檢查尺寸
        if width < 100 or height < 100:
            return False
        if width > 600 or height > 800:
            return False
        
        # 檢查長寬比
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 5:
            return False
        
        return True
    
    def _is_meaningful_page_image(self, pix) -> bool:
        """檢查頁面截圖是否有意義"""
        # 對於頁面截圖，使用較寬鬆的標準
        if pix.width < 100 or pix.height < 100:
            return False
        
        try:
            # 快速檢查：計算非白色像素比例
            img_data = pix.tobytes("ppm")
            pil_img = self.Image.open(io.BytesIO(img_data))
            
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # 縮小以加速檢查
            pil_img.thumbnail((50, 50))
            
            import numpy as np
            img_array = np.array(pil_img)
            
            # 計算非白色像素比例
            white_threshold = 250  # 對頁面截圖使用更高的白色門檻
            is_white = np.all(img_array >= white_threshold, axis=2)
            non_white_ratio = 1 - np.mean(is_white)
            
            # 只要有足夠的非白色內容就認為有意義
            return non_white_ratio > 0.15
            
        except Exception:
            return True  # 如果檢查失敗，保守地認為有意義
    
    def _is_valid_image(self, pix) -> bool:
        """改進的圖片有效性檢查"""
        # 放寬最小尺寸要求，科學圖表可能較小但仍有價值
        if pix.width < 30 or pix.height < 30:
            return False
        
        # 檢查最大尺寸（避免過大的圖片）
        if pix.width > 6000 or pix.height > 6000:
            return False
        
        # 放寬長寬比限制，科學圖表可能有各種比例
        aspect_ratio = max(pix.width, pix.height) / min(pix.width, pix.height)
        if aspect_ratio > 20:  # 允許更極端的長寬比
            return False
        
        # 檢查最小像素數，確保圖片有足夠內容
        total_pixels = pix.width * pix.height
        if total_pixels < 1000:  # 至少1000像素
            return False
        
        return True
    
    def _is_meaningful_image(self, pix) -> bool:
        """改進的圖片意義檢查，專門針對科學論文圖片"""
        try:
            # 轉換為PIL圖片進行分析
            img_data = pix.tobytes("ppm")
            pil_img = self.Image.open(io.BytesIO(img_data))
            
            # 轉換為RGB
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # 保持較高解析度進行分析（提高準確性）
            max_analysis_size = 200
            if max(pil_img.size) > max_analysis_size:
                ratio = max_analysis_size / max(pil_img.size)
                new_size = (int(pil_img.width * ratio), int(pil_img.height * ratio))
                pil_img = pil_img.resize(new_size, self.Image.Resampling.LANCZOS)
            
            import numpy as np
            img_array = np.array(pil_img)
            
            # 多重檢查標準
            checks = self._perform_image_quality_checks(img_array)
            
            # 綜合評判
            meaningful_score = 0
            
            # 1. 顏色豐富度檢查
            if checks['color_variance'] > 50:  # 降低門檻
                meaningful_score += 2
            elif checks['color_variance'] > 20:
                meaningful_score += 1
            
            # 2. 非白色內容檢查
            if checks['non_white_ratio'] > 0.15:  # 降低門檻
                meaningful_score += 2
            elif checks['non_white_ratio'] > 0.05:
                meaningful_score += 1
            
            # 3. 非黑色內容檢查
            if checks['non_black_ratio'] > 0.05:
                meaningful_score += 1
            
            # 4. 邊緣特徵檢查
            if checks['edge_strength'] > 30:  # 降低門檻
                meaningful_score += 2
            elif checks['edge_strength'] > 10:
                meaningful_score += 1
            
            # 5. 顏色分佈檢查
            if checks['color_diversity'] > 3:  # 至少4種主要顏色
                meaningful_score += 2
            elif checks['color_diversity'] > 1:
                meaningful_score += 1
            
            # 6. 結構複雜度檢查
            if checks['structure_complexity'] > 0.3:
                meaningful_score += 1
            
            # 7. 特殊檢查：科學圖表特徵
            if self._has_scientific_chart_features(checks):
                meaningful_score += 3
            
            # 決定是否為有意義的圖片
            is_meaningful = meaningful_score >= 4  # 降低門檻，更容易通過
            
            print(f"        📊 圖片分析 - 分數: {meaningful_score}/12")
            print(f"           顏色變異: {checks['color_variance']:.1f}, 非白色: {checks['non_white_ratio']:.2f}")
            print(f"           邊緣強度: {checks['edge_strength']:.1f}, 顏色多樣性: {checks['color_diversity']}")
            print(f"           結構複雜度: {checks['structure_complexity']:.2f}")
            
            return is_meaningful
            
        except Exception as e:
            print(f"        ⚠️ 圖片分析失敗: {e}")
            # 分析失敗時採用更寬鬆的策略
            return pix.width * pix.height > 2000  # 只要足夠大就接受
    
    def _perform_image_quality_checks(self, img_array) -> Dict[str, float]:
        """執行詳細的圖片品質檢查"""
        import numpy as np
        
        checks = {}
        
        # 1. 顏色變異檢查
        checks['color_variance'] = np.var(img_array)
        
        # 2. 白色像素比例檢查
        white_threshold = 235  # 稍微降低白色門檻
        is_white = np.all(img_array >= white_threshold, axis=2)
        checks['non_white_ratio'] = 1 - np.mean(is_white)
        
        # 3. 黑色像素比例檢查
        black_threshold = 20  # 幾乎全黑
        is_black = np.all(img_array <= black_threshold, axis=2)
        checks['non_black_ratio'] = 1 - np.mean(is_black)
        
        # 4. 邊緣強度檢查
        gray = np.mean(img_array, axis=2)
        edge_h = np.var(np.diff(gray, axis=0))
        edge_v = np.var(np.diff(gray, axis=1))
        checks['edge_strength'] = edge_h + edge_v
        
        # 5. 顏色多樣性檢查
        # 將圖片分成主要顏色區域
        reshaped = img_array.reshape(-1, 3)
        unique_colors = len(np.unique(reshaped.view(np.dtype((np.void, reshaped.dtype.itemsize*3)))))
        total_pixels = reshaped.shape[0]
        checks['color_diversity'] = min(10, unique_colors / (total_pixels / 100))  # 標準化
        
        # 6. 結構複雜度檢查
        # 計算圖片的熵（信息量）
        hist, _ = np.histogram(gray.flatten(), bins=50)
        hist = hist / np.sum(hist)  # 正規化
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        checks['structure_complexity'] = entropy / 5.64  # 標準化到0-1
        
        return checks
    
    def _has_scientific_chart_features(self, checks) -> bool:
        """檢查是否具有科學圖表特徵"""
        # 科學圖表通常具有：
        # 1. 中等到高的邊緣強度（座標軸、線條）
        # 2. 多樣的顏色分佈（數據點、線條）
        # 3. 結構化的內容（不是純隨機）
        
        has_edges = checks['edge_strength'] > 20
        has_colors = checks['color_diversity'] > 2
        has_structure = checks['structure_complexity'] > 0.2
        reasonable_content = checks['non_white_ratio'] > 0.1
        
        return has_edges and has_colors and has_structure and reasonable_content
    
    def _calculate_image_stats(self, pix) -> Dict[str, float]:
        """改進的圖片統計信息計算"""
        try:
            # 轉換為PIL圖片
            img_data = pix.tobytes("ppm")
            pil_img = self.Image.open(io.BytesIO(img_data))
            
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # 保持適當解析度進行分析
            max_size = 150
            if max(pil_img.size) > max_size:
                ratio = max_size / max(pil_img.size)
                new_size = (int(pil_img.width * ratio), int(pil_img.height * ratio))
                pil_img = pil_img.resize(new_size, self.Image.Resampling.LANCZOS)
            
            import numpy as np
            img_array = np.array(pil_img)
            
            # 執行詳細檢查
            checks = self._perform_image_quality_checks(img_array)
            
            # 計算綜合品質分數（0-10）
            quality_score = 0
            
            # 1. 顏色豐富度 (0-2.5分)
            if checks['color_variance'] > 100:
                quality_score += 2.5
            elif checks['color_variance'] > 50:
                quality_score += 2.0
            elif checks['color_variance'] > 20:
                quality_score += 1.5
            elif checks['color_variance'] > 10:
                quality_score += 1.0
            
            # 2. 內容豐富度 (0-2.5分)
            if checks['non_white_ratio'] > 0.3:
                quality_score += 2.5
            elif checks['non_white_ratio'] > 0.2:
                quality_score += 2.0
            elif checks['non_white_ratio'] > 0.1:
                quality_score += 1.5
            elif checks['non_white_ratio'] > 0.05:
                quality_score += 1.0
            
            # 3. 邊緣清晰度 (0-2分)
            if checks['edge_strength'] > 100:
                quality_score += 2.0
            elif checks['edge_strength'] > 50:
                quality_score += 1.5
            elif checks['edge_strength'] > 20:
                quality_score += 1.0
            elif checks['edge_strength'] > 10:
                quality_score += 0.5
            
            # 4. 顏色多樣性 (0-2分)
            if checks['color_diversity'] > 5:
                quality_score += 2.0
            elif checks['color_diversity'] > 3:
                quality_score += 1.5
            elif checks['color_diversity'] > 2:
                quality_score += 1.0
            elif checks['color_diversity'] > 1:
                quality_score += 0.5
            
            # 5. 結構複雜度加分 (0-1分)
            if checks['structure_complexity'] > 0.5:
                quality_score += 1.0
            elif checks['structure_complexity'] > 0.3:
                quality_score += 0.5
            
            # 科學圖表特徵加分
            if self._has_scientific_chart_features(checks):
                quality_score += 1.0
            
            # 確保分數在合理範圍內
            quality_score = min(10.0, max(0.0, quality_score))
            
            return {
                'quality_score': quality_score,
                'color_variance': checks['color_variance'],
                'non_white_ratio': checks['non_white_ratio'],
                'edge_strength': checks['edge_strength'],
                'color_diversity': checks['color_diversity'],
                'structure_complexity': checks['structure_complexity']
            }
            
        except Exception as e:
            print(f"        ⚠️ 統計計算失敗: {e}")
            return {
                'quality_score': 5.0,
                'color_variance': 0.0,
                'non_white_ratio': 0.0,
                'edge_strength': 0.0,
                'color_diversity': 0.0,
                'structure_complexity': 0.0
            }
    
    def display_results(self, filename: str, images: List[Dict]):
        """顯示圖片提取結果"""
        print(f"\n" + "="*80)
        print(f"📄 PDF文件: {filename}")
        print(f"="*80)
        
        # 顯示基本統計
        print(f"📊 圖片提取統計:")
        print(f"   🖼️ 圖片數量: {len(images)}")
        
        # 顯示圖片信息
        if images:
            print(f"\n🖼️ 圖片詳細信息:")
            for img in images:
                print(f"   📷 {img['filename']}")
                print(f"      頁面: {img['page']}, 尺寸: {img['width']}x{img['height']}")
                print(f"      提取方法: {img['extraction_method']}")
                print(f"      品質分數: {img['quality_score']:.2f}/10.0")
                print(f"      檔案路徑: {img['path']}")
        else:
            print(f"\n⚠️ 未找到任何圖片")
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """處理單個PDF文件，只提取圖片"""
        filename = Path(pdf_path).name
        print(f"\n🚀 開始處理PDF: {filename}")
        
        # 提取圖片
        images = self.extract_images(pdf_path)
        
        # 顯示結果
        self.display_results(filename, images)
        
        return {
            'filename': filename,
            'images': images
        }

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
    """主函數"""
    print("🚀 PDF圖片提取工具")
    print("=" * 50)

    # PDF file list - search for files in multiple locations
    pdf_filenames = ['paper1.pdf', 'paper2.pdf', 'paper3.pdf']
    
    # Find existing PDF files
    existing_files = []
    for filename in pdf_filenames:
        pdf_path = find_pdf_file(filename)
        if pdf_path:
            existing_files.append(pdf_path)
            print(f"✅ 找到PDF文件: {Path(pdf_path).name}")
        else:
            print(f"❌ PDF文件不存在: {filename}")
    
    if not existing_files:
        print("❌ 沒有找到任何PDF文件！")
        return
    
    # 創建圖片提取器
    extractor = PDFImageExtractor()
    
    # 處理所有PDF文件
    all_results = []
    for pdf_path in existing_files:
        try:
            result = extractor.process_pdf(pdf_path)
            all_results.append(result)
        except Exception as e:
            print(f"❌ 處理 {Path(pdf_path).name} 時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    # 總結報告
    print(f"\n" + "="*80)
    print("📊 總體圖片提取報告")
    print("="*80)
    
    total_images = sum(len(r['images']) for r in all_results)
    
    print(f"✅ 成功處理 {len(all_results)} 個PDF文件")
    print(f"🖼️ 總圖片數量: {total_images}")
    
    for result in all_results:
        print(f"\n📄 {result['filename']}:")
        print(f"   🖼️ 圖片: {len(result['images'])} 張")
        
        # 顯示品質統計
        if result['images']:
            quality_scores = [img['quality_score'] for img in result['images']]
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"   📊 平均品質: {avg_quality:.2f}/10.0")
    
    print(f"\n🎉 所有PDF圖片提取完成！輸出檔案保存在: ./output/")

if __name__ == "__main__":
    main()
