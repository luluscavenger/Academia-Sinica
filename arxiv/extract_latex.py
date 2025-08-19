import os
import re
import requests
import tarfile
import shutil

# 圖片轉 PNG：PDF/EPS
def convert_pdf_or_eps_to_png(src_path, dst_path_base):
    try:
        import fitz  # pymupdf
    except ImportError:
        print("Please install pymupdf: pip install pymupdf")
        return []
    out_imgs = []
    try:
        doc = fitz.open(src_path)
        for page_idx in range(len(doc)):
            pix = doc[page_idx].get_pixmap(dpi=300)
            out_name = f"{dst_path_base}_p{page_idx+1}.png"
            pix.save(out_name)
            out_imgs.append(out_name)
        doc.close()
        os.remove(src_path)  # 刪除原始 pdf/eps
    except Exception as e:
        print(f"Failed to convert {src_path}: {e}")
    return out_imgs

# 圖片轉 PNG：JPG
def convert_image_to_png(src_path, dst_path):
    try:
        from PIL import Image
    except ImportError:
        print("Please install pillow: pip install pillow")
        return False
    try:
        img = Image.open(src_path)
        img.save(dst_path)
        os.remove(src_path)
        return True
    except Exception as e:
        print(f"Failed to convert {src_path} to PNG: {e}")
        return False

# tex 轉 Markdown
def convert_tex_to_markdown(tex_content):
    content = tex_content
    content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\\documentclass.*?\n', '', content)
    content = re.sub(r'\\usepackage.*?\n', '', content)
    content = re.sub(r'\\newcommand.*?\n', '', content)
    content = re.sub(r'\\def\\.*?\n', '', content)
    content = re.sub(r'\\begin\{document\}', '', content)
    content = re.sub(r'\\end\{document\}', '', content)
    content = re.sub(r'\\title\{([^}]+)\}', r'# \1', content)
    content = re.sub(r'\\section\{([^}]+)\}', r'## \1', content)
    content = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', content)
    content = re.sub(r'\\subsubsection\{([^}]+)\}', r'#### \1', content)
    content = re.sub(r'\\paragraph\{([^}]+)\}', r'##### \1', content)
    content = re.sub(r'\\subparagraph\{([^}]+)\}', r'###### \1', content)
    content = re.sub(r'\\author\{([^}]+)\}', r'**作者**: \1', content)
    content = re.sub(r'\\begin\{abstract\}', r'## 摘要\n', content)
    content = re.sub(r'\\end\{abstract\}', r'', content)
    content = re.sub(r'\\begin\{itemize\}', '', content)
    content = re.sub(r'\\end\{itemize\}', '', content)
    content = re.sub(r'\\begin\{enumerate\}', '', content)
    content = re.sub(r'\\end\{enumerate\}', '', content)
    content = re.sub(r'\\item\s*', '- ', content)
    content = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', content)
    content = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', content)
    content = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', content)
    content = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', content)
    content = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'$$\1$$', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{align\}(.*?)\\end\{align\}', r'$$\1$$', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}', r'$$\1$$', content, flags=re.DOTALL)
    content = re.sub(r'\\cite\{[^}]+\}', '[citation]', content)
    content = re.sub(r'\\ref\{[^}]+\}', '[ref]', content)
    content = re.sub(r'\\label\{[^}]+\}', '', content)
    content = re.sub(r'\\begin\{figure\}.*?\\caption\{([^}]+)\}.*?\\end\{figure\}', r'**圖**: \1', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{table\}.*?\\caption\{([^}]+)\}.*?\\end\{table\}', r'**表**: \1', content, flags=re.DOTALL)
    content = re.sub(r'\\includegraphics.*?\{[^}]+\}', '[圖片]', content)
    content = re.sub(r'\\maketitle', '', content)
    content = re.sub(r'\\tableofcontents', '', content)
    content = re.sub(r'\\newpage', '', content)
    content = re.sub(r'\\clearpage', '', content)
    content = re.sub(r'\\pagebreak', '', content)
    content = re.sub(r'\\\\', '\n', content)
    content = re.sub(r'\\hline', '', content)
    content = re.sub(r'\\centering', '', content)
    content = re.sub(r'\\[a-zA-Z]+\*?\{[^}]*\}', '', content)
    content = re.sub(r'\\[a-zA-Z]+\*?', '', content)
    content = re.sub(r'\{([^{}]*)\}', r'\1', content)

    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            line = re.sub(r'\s+', ' ', line)
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != '':
            cleaned_lines.append('')
    paragraphs = []
    current = []
    for line in cleaned_lines:
        if line == '':
            if current:
                paragraphs.append(' '.join(current))
                current = []
        elif line.startswith('#') or line.startswith('**') or line.startswith('- ') or (line.startswith('$$') and line.endswith('$$')):
            if current:
                paragraphs.append(' '.join(current))
                current = []
            paragraphs.append(line)
        else:
            current.append(line)
    if current:
        paragraphs.append(' '.join(current))

    result = []
    for para in paragraphs:
        if para.strip():
            result.append(para.strip())
            result.append('')
    return '\n'.join(result).strip()

# 主流程：從 LaTeX tarball 擷取資訊
def extract_from_latex(latex_url, base_dir):
    latex_tar = os.path.join(base_dir, "source_latex.tar")
    r = requests.get(latex_url, stream=True)
    with open(latex_tar, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    if not tarfile.is_tarfile(latex_tar):
        print("Invalid tar file.")
        os.remove(latex_tar)
        return False
    extract_dir = os.path.join(base_dir, "latex_src")
    os.makedirs(extract_dir, exist_ok=True)
    with tarfile.open(latex_tar, "r:*") as tar:
        tar.extractall(path=extract_dir)
    tex_files = []
    img_files = []
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".tex"):
                tex_files.append(os.path.join(root, file))
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.eps')):
                img_files.append(os.path.join(root, file))
    main_tex = None
    for name in ["main.tex", "paper.tex", "manuscript.tex"]:
        for path in tex_files:
            if os.path.basename(path).lower() == name:
                main_tex = path
                break
    if not main_tex:
        for path in tex_files:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if r'\begin{document}' in f.read():
                    main_tex = path
                    break
    if not main_tex:
        main_tex = sorted(tex_files, key=lambda x: len(os.path.basename(x)))[0]
    with open(main_tex, "r", encoding="utf-8", errors="ignore") as f:
        tex_content = f.read()
    markdown = convert_tex_to_markdown(tex_content)
    with open(os.path.join(base_dir, "text.md"), "w", encoding="utf-8") as f:
        f.write(markdown)
    formulas = re.findall(r"\$\$.*?\$\$|\$.*?\$", tex_content, flags=re.DOTALL)
    with open(os.path.join(base_dir, "formulas.md"), "w", encoding="utf-8") as f:
        for formula in formulas:
            f.write(formula.strip() + '\n\n')
    img_dir = os.path.join(base_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    img_count = 1
    for img_path in img_files:
        ext = os.path.splitext(img_path)[1].lower()
        img_name_base = f"1-{img_count}"
        dst_png = os.path.join(img_dir, f"{img_name_base}.png")
        if ext in [".pdf", ".eps"]:
            convert_pdf_or_eps_to_png(img_path, os.path.join(img_dir, img_name_base))
            img_count += 1
        elif ext == ".png":
            shutil.copy2(img_path, dst_png)
            os.remove(img_path)
            img_count += 1
        elif ext in [".jpg", ".jpeg"]:
            convert_image_to_png(img_path, dst_png)
            img_count += 1
    print(f"LaTeX extraction complete. Output at: {base_dir}")
    return True

# 測試用主程序
def test_latex_extraction():
    test_url = "https://arxiv.org/e-print/2301.00001"
    test_dir = "./test_latex_extract"
    os.makedirs(test_dir, exist_ok=True)
    result = extract_from_latex(test_url, test_dir)
    if result:
        print("✅ 成功轉換 tex → Markdown + 公式 + 圖片")
    else:
        print("❌ 轉換失敗")

if __name__ == "__main__":
    test_latex_extraction()
