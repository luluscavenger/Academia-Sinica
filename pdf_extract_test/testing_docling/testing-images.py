#!/usr/bin/env python3
"""
PDF 圖像提取工具
使用 Docling + PyMuPDF 混合方法提取 PDF 文件中的所有圖像
"""

import os
import io
import logging
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFImageExtractor:
    """PDF 圖像提取器"""
    
    def __init__(self, output_dir: str = "extracted_images"):
        """
        初始化圖像提取器
        
        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化 Docling 轉換器 - 使用默認配置
        logger.info("初始化 Docling 轉換器...")
        self.converter = DocumentConverter()
    
    def convert_bbox_coordinates(self, bbox, page_height: float):
        """
        轉換座標系統：從 BOTTOMLEFT (Docling) 到 TOPLEFT (PyMuPDF)
        
        Args:
            bbox: Docling 的 bbox 物件
            page_height: 頁面高度
            
        Returns:
            fitz.Rect: PyMuPDF 格式的矩形
        """
        # Docling: BOTTOMLEFT 原點 (左下角為 0,0)
        # PyMuPDF: TOPLEFT 原點 (左上角為 0,0)
        
        left = bbox.l
        bottom = bbox.b
        right = bbox.r
        top = bbox.t
        
        # 轉換 Y 座標
        new_top = page_height - top
        new_bottom = page_height - bottom
        
        return fitz.Rect(left, new_top, right, new_bottom)
    
    def extract_image_from_page(self, pdf_doc, page_num: int, rect: fitz.Rect) -> Image.Image:
        """
        從指定頁面和區域提取圖像
        
        Args:
            pdf_doc: PyMuPDF 文檔物件
            page_num: 頁面編號 (0-based)
            rect: 圖像區域
            
        Returns:
            PIL Image 物件
        """
        page = pdf_doc[page_num]
        
        # 獲取頁面像素圖
        mat = fitz.Matrix(2.0, 2.0)  # 提高解析度
        pix = page.get_pixmap(matrix=mat, clip=rect)
        
        # 轉換為 PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        return image
    
    def analyze_image_properties(self, image: Image.Image) -> Dict[str, Any]:
        """
        分析圖像屬性
        
        Args:
            image: PIL Image 物件
            
        Returns:
            包含圖像屬性的字典
        """
        # 轉換為 numpy 陣列進行分析
        img_array = np.array(image)
        
        properties = {
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'channels': len(img_array.shape) if len(img_array.shape) > 2 else 1,
            'size_bytes': len(image.tobytes()),
        }
        
        # 計算亮度統計
        if len(img_array.shape) == 3:  # 彩色圖像
            gray = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        else:  # 灰階圖像
            gray = img_array
            
        properties.update({
            'brightness_mean': float(np.mean(gray)),
            'brightness_std': float(np.std(gray)),
            'brightness_min': float(np.min(gray)),
            'brightness_max': float(np.max(gray))
        })
        
        return properties
    
    def process_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        處理單個 PDF 文件
        
        Args:
            pdf_path: PDF 文件路徑
            
        Returns:
            提取的圖像信息列表
        """
        logger.info(f"正在處理PDF: {pdf_path.name}")
        
        # 使用 Docling 進行文檔分析
        result = self.converter.convert(pdf_path)
        doc = result.document
        
        # 調試：檢查所有元素
        all_elements = []
        for element in doc.iterate_items():
            all_elements.append(element)
        
        logger.info(f"文檔共有 {len(all_elements)} 個元素")
        
        # 查找圖像元素 - 使用多種檢測方法
        images = []
        for element in doc.iterate_items():
            # 方法1: 檢查 label 屬性
            if hasattr(element, 'label') and element.label:
                logger.debug(f"元素標籤: {element.label}")
                if 'image' in element.label.lower() or 'figure' in element.label.lower() or 'picture' in element.label.lower():
                    images.append(element)
                    logger.info(f"找到圖像元素: {element.label}")
            
            # 方法2: 檢查元素類型
            element_type = type(element).__name__
            if 'image' in element_type.lower() or 'picture' in element_type.lower() or 'figure' in element_type.lower():
                images.append(element)
                logger.info(f"找到圖像元素 (類型): {element_type}")
        
        logger.info(f"檢測到 {len(images)} 個圖像")
        
        # 如果沒有找到圖像，嘗試使用純 PyMuPDF 方法
        if not images:
            logger.warning("Docling 沒有檢測到圖像，嘗試使用 PyMuPDF 直接提取")
            return self.extract_images_with_pymupdf(pdf_path)
        
        # 使用 PyMuPDF 開啟 PDF 進行圖像提取
        pdf_doc = fitz.open(pdf_path)
        extracted_images = []
        paper_name = pdf_path.stem
        
        logger.info(f"處理論文: {paper_name}")
        
        for i, image_element in enumerate(images, 1):
            try:
                logger.info(f"處理圖像 {i}")
                
                # 獲取圖像的位置信息
                bbox = image_element.bbox
                page_num = image_element.prov[0].page_no - 1  # 轉換為 0-based
                
                logger.info(f"頁面: {page_num + 1}, bbox: l={bbox.l} t={bbox.t} r={bbox.r} b={bbox.b} coord_origin={bbox.coord_origin}")
                
                # 獲取頁面尺寸
                page = pdf_doc[page_num]
                page_height = page.rect.height
                
                # 轉換座標系統
                fitz_rect = self.convert_bbox_coordinates(bbox, page_height)
                logger.info(f"轉換後的fitz rect: {fitz_rect}")
                
                # 提取圖像
                image = self.extract_image_from_page(pdf_doc, page_num, fitz_rect)
                logger.info(f"成功提取圖像: {image.size}")
                
                # 分析圖像屬性
                properties = self.analyze_image_properties(image)
                
                # 保存圖像
                image_filename = f"{paper_name}_image_{i}.png"
                image_path = self.output_dir / image_filename
                image.save(image_path)
                logger.info(f"保存圖像: {image_path}")
                logger.info(f"圖像模式: {properties['mode']}")
                logger.info(f"尺寸: {properties['width']}x{properties['height']}")
                
                # 記錄圖像信息
                image_info = {
                    'paper_name': paper_name,
                    'image_id': i,
                    'filename': image_filename,
                    'page_num': page_num + 1,
                    'bbox': {
                        'left': bbox.l,
                        'top': bbox.t,
                        'right': bbox.r,
                        'bottom': bbox.b
                    },
                    'properties': properties
                }
                extracted_images.append(image_info)
                
            except Exception as e:
                logger.error(f"處理圖像 {i} 時發生錯誤: {str(e)}")
                continue
        
        pdf_doc.close()
        logger.info(f"成功提取 {len(extracted_images)} 張圖像")
        
        return extracted_images
    
    def extract_images_with_pymupdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        使用純 PyMuPDF 提取圖像
        
        Args:
            pdf_path: PDF 文件路徑
            
        Returns:
            提取的圖像信息列表
        """
        logger.info(f"使用 PyMuPDF 提取圖像: {pdf_path.name}")
        
        pdf_doc = fitz.open(pdf_path)
        extracted_images = []
        paper_name = pdf_path.stem
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            image_list = page.get_images()
            
            logger.info(f"頁面 {page_num + 1} 找到 {len(image_list)} 個圖像")
            
            for img_index, img in enumerate(image_list):
                try:
                    # 獲取圖像數據
                    xref = img[0]
                    base_image = pdf_doc.extract_image(xref)
                    img_data = base_image["image"]
                    img_ext = base_image["ext"]
                    
                    # 轉換為 PIL Image
                    image = Image.open(io.BytesIO(img_data))
                    
                    # 分析圖像屬性
                    properties = self.analyze_image_properties(image)
                    
                    # 過濾太小的圖像
                    if properties['width'] < 50 or properties['height'] < 50:
                        logger.debug(f"跳過小圖像: {properties['width']}x{properties['height']}")
                        continue
                    
                    # 保存圖像
                    image_filename = f"{paper_name}_page{page_num + 1}_img{img_index + 1}.{img_ext}"
                    image_path = self.output_dir / image_filename
                    image.save(image_path)
                    
                    logger.info(f"保存圖像: {image_filename}")
                    logger.info(f"尺寸: {properties['width']}x{properties['height']}")
                    
                    # 保存圖像信息
                    image_info = {
                        'filename': image_filename,
                        'path': str(image_path),
                        'page_number': page_num + 1,
                        'size': image.size,
                        'format': img_ext.upper(),
                        'properties': properties
                    }
                    extracted_images.append(image_info)
                    
                except Exception as e:
                    logger.error(f"處理頁面 {page_num + 1} 圖像 {img_index + 1} 時發生錯誤: {str(e)}")
                    continue
        
        pdf_doc.close()
        logger.info(f"PyMuPDF 成功提取 {len(extracted_images)} 張圖像")
        
        return extracted_images

    def extract_from_directory(self, pdf_dir: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        從目錄中提取所有 PDF 文件的圖像
        
        Args:
            pdf_dir: PDF 文件目錄
            
        Returns:
            按文件名分組的圖像信息字典
        """
        pdf_path = Path(pdf_dir)
        pdf_files = list(pdf_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.error(f"在目錄 {pdf_dir} 中沒有找到 PDF 文件")
            return {}
        
        logger.info(f"找到 {len(pdf_files)} 個PDF文件")
        
        all_results = {}
        total_images = 0
        
        for pdf_file in sorted(pdf_files):
            logger.info(f"\n{'='*60}")
            logger.info(f"處理論文: {pdf_file.stem}")
            logger.info(f"{'='*60}")
            
            try:
                results = self.process_pdf(pdf_file)
                all_results[pdf_file.stem] = results
                total_images += len(results)
            except Exception as e:
                logger.error(f"處理文件 {pdf_file.name} 時發生錯誤: {str(e)}")
                all_results[pdf_file.stem] = []
        
        logger.info(f"\n{'='*60}")
        logger.info(f"所有PDF處理完成！")
        logger.info(f"總圖像數量: {total_images}")
        logger.info(f"結果保存在: {self.output_dir}")
        logger.info(f"{'='*60}")
        
        return all_results


def main():
    """主函數"""
    import io
    
    # 設定路徑
    current_dir = Path(__file__).parent
    pdf_directory = current_dir  # 假設 PDF 文件在同一目錄
    
    # 創建提取器
    extractor = PDFImageExtractor(output_dir="extracted_images")
    
    # 提取圖像
    results = extractor.extract_from_directory(pdf_directory)
    
    # 統計結果
    total_images = sum(len(images) for images in results.values())
    logger.info(f"提取完成，共處理 {total_images} 張圖像")
    
    # 打印詳細結果
    for paper_name, images in results.items():
        if images:
            logger.info(f"{paper_name}: {len(images)} 張圖像")
            for img_info in images:
                logger.info(f"  - {img_info['filename']} ({img_info['properties']['width']}x{img_info['properties']['height']})")


if __name__ == "__main__":
    main()
