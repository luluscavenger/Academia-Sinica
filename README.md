This repository is Lulu Hung recording her work as a summer intern at the Academia Sinica, Institute of Physics from 2025/07/01 to 2025/08/31 
We aim to build an AI-enhanced particle and High-Energy Physics Search System to search more accurately for High-Energy Physics
Here are the usages of the files:
1.arxiv 
The arXiv file includes the code and its examples; clear instructions are in the README file.
Its usage is to extract HTML, LaTeX, and PDF files into md and png files, to provide accurate texts for the next step summary and keyword extraction.
The examples are below files:
HTML : 2507.21856
LaTeX : 2110.01975
PDF : 2507.15389
2.pdf_estract_test
The pdf_estract_test file is established to test word, images and formulas extraction from PDF type papers.
It contains two files, including testing_docling and testing _pymu files, they both contain README files for instruction
There are three papers as pdf documents(paper1.pdf, paper2.pdf, paper3.pdf) as examples
3.prompt_chatbot
The prompt_chatbot file is used to generate better prompts for summarization and keyword extraction. 
It lets AI act in two roles: 
A generator(uses the prompt to generate a summary and keywords, and the prompt will be regenerated according to the suggestions)
A reviewer(scores and gives suggestions according to the summary and keywords).
Markdown files with arXiv numbers are examples, and the README file instructs the files' usage.
