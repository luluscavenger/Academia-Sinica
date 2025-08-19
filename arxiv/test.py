import os
import re
import requests
from bs4 import BeautifulSoup
import pypandoc
import pymupdf as fitz  # pymupdf
import arxiv
from pathlib import Path
import tarfile

def query_arxiv_resources(arxiv_id):
    result = arxiv.Client().results(arxiv.Search(id_list=[arxiv_id]))
    try:
        record = next(result)
    except Exception as e:
        print("arXiv id not found:", e)
        return {}

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    latex_url = f"https://arxiv.org/e-print/{arxiv_id}"
    html_url = f"https://arxiv.org/html/{arxiv_id}"
    def url_exists(url):
        try:
            r = requests.head(url, allow_redirects=True, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
    html_ok = url_exists(html_url)
    latex_ok = url_exists(latex_url)
    pdf_ok = url_exists(pdf_url)
    return {
        "html": html_url if html_ok else None,
        "latex": latex_url if latex_ok else None,
        "pdf": pdf_url if pdf_ok else None,
        "title": record.title if hasattr(record, "title") else arxiv_id
    }

def main():
    arxiv_id = input("Enter arXiv ID (e.g., 2110.08629): ").strip()
    resources = query_arxiv_resources(arxiv_id)
    print("Resources found:")
    for k, v in resources.items():
        if k in ["html", "latex", "pdf"]:
            print(f"  {k.upper()}:", "Available -" if v else "Unavailable -", v if v else "")

    # 資料夾
    base_dir = os.path.join(os.getcwd(), arxiv_id)
    os.makedirs(base_dir, exist_ok=True)

    # 優先順序
    if resources.get("html"):
        from extract_html import extract_from_html
        extract_from_html(resources["html"], base_dir)
    elif resources.get("latex"):
        from extract_latex import extract_from_latex
        if not extract_from_latex(resources["latex"], base_dir):
            print("LaTeX failed. Trying PDF.")
            if resources.get("pdf"):
                from extract_pdf import extract_from_pdf
                extract_from_pdf(resources["pdf"], base_dir)
            else:
                print("No suitable source found.")
    elif resources.get("pdf"):
        from extract_pdf import extract_from_pdf
        extract_from_pdf(resources["pdf"], base_dir)
    else:
        print("No source found. Please check the arXiv ID.")

if __name__ == '__main__':
    main()
