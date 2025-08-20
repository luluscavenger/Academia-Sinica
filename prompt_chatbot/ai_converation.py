#!/usr/bin/env python3
# ai_converation.py - AI Self-Evaluation System
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
import re
from typing import Dict, Any
from datetime import datetime

# 檢查並導入 OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: OpenAI package not installed")
    print("Please run: pip install openai")
    sys.exit(1)

# ====== Global Variables ======
client = None
current_prompt = ""
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "prompt_config.json")

def extract_arxiv_id_from_path(file_path: str) -> str:
    """Extract arxiv ID from file path
    
    Examples:
    /home/user/AI_literature_agent-3/2110.01975/text.md -> 2110.01975
    /path/to/2507.15389/source.html -> 2507.15389
    """
    # 正規化路徑
    normalized_path = os.path.normpath(file_path)
    path_parts = normalized_path.split(os.sep)
    
    # 從路徑部分中尋找 arxiv ID 模式
    arxiv_pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    
    for part in path_parts:
        if re.match(arxiv_pattern, part):
            # 移除版本號（如果有的話）
            arxiv_id = re.sub(r'v\d+$', '', part)
            return arxiv_id
    
    # 如果找不到，返回空字串
    return ""

def generate_summary_file_path(input_file_path: str) -> str:
    """Generate summary file path based on input file path"""
    arxiv_id = extract_arxiv_id_from_path(input_file_path)
    
    if not arxiv_id:
        # 如果無法提取 arxiv ID，使用檔名
        base_dir = os.path.dirname(input_file_path)
        filename = os.path.splitext(os.path.basename(input_file_path))[0]
        return os.path.join(base_dir, f"{filename}_summary_keyword.md")
    
    # 使用 arxiv ID 生成檔案路徑
    # 在同一目錄層級創建檔案
    input_dir = os.path.dirname(input_file_path)
    arxiv_dir = os.path.dirname(input_dir) if arxiv_id in input_dir else input_dir
    return os.path.join(arxiv_dir, f"{arxiv_id}sum&keyword.md")

def save_summary_and_keywords(output: Dict[str, Any], file_path: str, score: float = None):
    """Save summary and keywords to file"""
    summary_file = generate_summary_file_path(file_path)
    
    try:
        # 準備內容
        content_lines = []
        content_lines.append(f"# Summary & Keywords Report")
        content_lines.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_lines.append(f"**Source File:** {file_path}")
        if score is not None:
            content_lines.append(f"**Evaluation Score:** {score}/20.0")
        content_lines.append("")
        
        # Abstract
        if "abstract" in output:
            content_lines.append("## Abstract")
            content_lines.append(output["abstract"])
            content_lines.append("")
        
        # Summary bullets
        if "summary_bullets" in output:
            content_lines.append("## Key Findings")
            for i, bullet in enumerate(output["summary_bullets"], 1):
                content_lines.append(f"{i}. {bullet}")
            content_lines.append("")
        
        # Keywords
        if "keywords" in output:
            content_lines.append("## Keywords")
            content_lines.append(f"**Total:** {len(output['keywords'])} keywords")
            content_lines.append("")
            for keyword in output["keywords"]:
                content_lines.append(f"- {keyword}")
            content_lines.append("")
        
        # 保存到檔案
        os.makedirs(os.path.dirname(summary_file), exist_ok=True)
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        print(f"✅ Summary & keywords saved to: {summary_file}")
        return summary_file
        
    except Exception as e:
        print(f"❌ Failed to save summary file: {e}")
        return None

class AIEvaluationSystem:
    """AI Self-Evaluation System: Generator + Reviewer dual-role optimization loop"""
    
    def __init__(self, api_key: str):
        """Initialize the system"""
        self.client = OpenAI(api_key=api_key)
        self.current_prompt = self.load_prompt()
        print("✅ AI evaluation system initialized successfully")
    
    def load_prompt(self) -> str:
        """Load prompt from JSON file"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            prompt = config.get("prompt", "")
            print(f"✅ Prompt loaded successfully, length: {len(prompt)} characters")
            return prompt
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {CONFIG_FILE}")
            print("📝 Creating default configuration file...")
            # Ensure directory exists
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            # Provide default prompt
            default_prompt = """You are a domain expert assistant for physics papers. Read the following Markdown and produce:
1) 5 bullet-point key findings with numbers, units, and uncertainties if available.
2) A 1-paragraph abstract (120–180 words) faithful to the text.
3) 15–25 domain keywords (prefer PHYS_TERM/METHOD/MATERIAL).
- Preserve inline equations as `$...$` and do not invent results.
Output ONLY valid JSON format:
{
  "summary_bullets": ["...", "..."],
  "abstract": "...",
  "keywords": ["...", "..."]
}

Paper content:
{CONTENT}"""
            self.save_prompt(default_prompt)
            return default_prompt
        except Exception as e:
            print(f"❌ 載入 prompt 失敗: {e}")
            return self._get_fallback_prompt()
    
    
    def _get_fallback_prompt(self) -> str:
        """回退的預設 prompt"""
        return """You are a physics paper analysis expert. Extract from the following content:
1) "summary_bullets": 5 key findings with specific numbers/units
2) "abstract": 120-180 word summary 
3) "keywords": 15-25 physics-related terms

Return ONLY valid JSON:
{"summary_bullets": ["..."], "abstract": "...", "keywords": ["..."]}

Content: {CONTENT}"""
    
    def save_prompt(self, prompt: str):
        """儲存 prompt 到 JSON 檔案"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            config = {"prompt": prompt}
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ Prompt 已保存到 {CONFIG_FILE}")
        except Exception as e:
            print(f"❌ 保存 prompt 失敗: {e}")
    
    def call_openai(self, prompt: str, role: str = "generator") -> str:
        """呼叫 OpenAI API"""
        try:
            print(f"🤖 {role.upper()} 正在處理...")
            if not self.client:
                print("❌ OpenAI 客戶端未初始化")
                return ""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7 if role == "generator" else 0.1,
                max_tokens=4000
            )
            result = response.choices[0].message.content.strip()
            print(f"✅ {role.upper()} response completed, length: {len(result)} characters")
            return result
        except Exception as e:
            print(f"❌ {role.upper()} API call failed: {e}")
            print(f"Please check:")
            print("1. API Key is correct")
            print("2. Network connection is stable")
            print("3. OpenAI service is available")
            return ""
    
    def generator_extract(self, content: str) -> Dict[str, Any]:
        """Generator role: Generate summary and keywords using current prompt"""
        print("\n🔧 GENERATOR starting work...")
        
        full_prompt = self.current_prompt.replace("{CONTENT}", content)
        raw_output = self.call_openai(full_prompt, "generator")
        
        if not raw_output:
            return {}
        
        # Try to parse JSON output
        return self._parse_json_output(raw_output)
    
    def _parse_json_output(self, raw_output: str) -> Dict[str, Any]:
        """Parse JSON output using multiple methods"""
        # Method 1: Direct parsing
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass
        
        # Method 2: Extract from markdown code block
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.search(json_pattern, raw_output, re.DOTALL)
        if matches:
            try:
                return json.loads(matches.group(1))
            except json.JSONDecodeError:
                pass
        
        # Method 3: Find JSON structure
        json_patterns = [
            r'\{.*?"summary_bullets".*?"abstract".*?"keywords".*?\}',
            r'\{.*?"summary".*?"keywords".*?\}',
        ]
        
        for pattern in json_patterns:
            matches = re.search(pattern, raw_output, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches.group(0))
                except json.JSONDecodeError:
                    continue
        
        print("⚠️  無法解析 JSON，返回原始文本")
        return {"raw_output": raw_output}
    
    def reviewer_evaluate(self, content: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Reviewer 角色：評估 Generator 的輸出並提供改進建議"""
        print("\n🔍 REVIEWER 開始評估...")
        
        if not output or "raw_output" in output:
            return {
                "total_score": 2.0,
                "detailed_scores": {
                    "summary_quality": 0.5,
                    "keyword_relevance": 0.5,
                    "format_compliance": 0.5,
                    "physics_terminology": 0.5
                },
                "suggestions": [
                    "Output format is completely incorrect, unable to parse JSON",
                    "Need to explicitly specify JSON format output",
                    "Ensure output contains summary_bullets, abstract, keywords fields"
                ]
            }
        
        critique_prompt = f"""
You are a professional academic paper analysis evaluation expert. Please evaluate the quality of the following physics paper summary extraction results.

Original document length: {len(content)} characters

AI extraction results:
{json.dumps(output, ensure_ascii=False, indent=2)}

Please rate from the following four perspectives, with 0.5 increments (0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0), maximum 5 points each (total 20 points):

1. Summary Quality: Is the content complete and accurately reflects the paper's key points?
   - 5.0: Completely accurate, covers all key information
   - 4.5: Almost perfect with very minor omissions
   - 4.0: Mostly accurate with slight omissions
   - 3.5: Generally accurate but missing some important details
   - 3.0: Basically accurate but with obvious omissions
   - 2.5: Partially accurate, some important information missing
   - 2.0: Partially accurate, important information missing
   - 1.5: Limited accuracy, significant information gaps
   - 1.0: Inaccurate or severely incomplete
   - 0.5: Very poor quality
   - 0.0: Completely wrong or missing

2. Keyword Relevance: Are keywords precise and relevant to physics content?
   - 5.0: All keywords highly relevant and professional
   - 4.5: Almost all keywords relevant with excellent specificity
   - 4.0: Most keywords relevant and appropriate
   - 3.5: Generally good keyword selection with minor issues
   - 3.0: About half of keywords relevant
   - 2.5: Some keywords relevant but lacking precision
   - 2.0: Few keywords relevant
   - 1.5: Limited relevance in keyword selection
   - 1.0: Keywords irrelevant or incorrect
   - 0.5: Poor keyword quality
   - 0.0: No relevant keywords

3. Format Compliance: Does it strictly follow the required JSON format?
   - 5.0: Perfect format compliance
   - 4.5: Almost perfect with very minor formatting issues
   - 4.0: Generally compliant with small problems
   - 3.5: Mostly compliant but some formatting concerns
   - 3.0: Partially compliant format
   - 2.5: Some format issues affecting usability
   - 2.0: Obvious format problems
   - 1.5: Significant format violations
   - 1.0: Format completely incorrect
   - 0.5: Severe format errors
   - 0.0: No proper format

4. Physics Terminology: Is physics terminology usage correct and appropriate?
   - 5.0: Terminology usage completely correct and professional
   - 4.5: Excellent terminology with very minor imprecisions
   - 4.0: Terminology usage basically correct
   - 3.5: Generally good terminology with some issues
   - 3.0: Terminology usage acceptable
   - 2.5: Some terminology errors or inappropriate usage
   - 2.0: Terminology usage incorrect or inappropriate
   - 1.5: Significant terminology problems
   - 1.0: Serious terminology errors
   - 0.5: Very poor terminology usage
   - 0.0: Completely wrong terminology

Please respond in the following JSON format (ensure valid JSON with 0.5 increments):
{{
  "total_score": [sum of four scores, max 20.0],
  "detailed_scores": {{
    "summary_quality": [0-5.0 in 0.5 increments],
    "keyword_relevance": [0-5.0 in 0.5 increments],
    "format_compliance": [0-5.0 in 0.5 increments],
    "physics_terminology": [0-5.0 in 0.5 increments]
  }},
  "suggestions": [
    "Specific suggestion 1",
    "Specific suggestion 2", 
    "Specific suggestion 3"
  ]
}}
"""
        
        raw_critique = self.call_openai(critique_prompt, "reviewer")
        
        # Try multiple methods to parse JSON
        critique_result = self._parse_critique_json(raw_critique)
        
        if critique_result:
            # Validate score ranges (0-5 in 0.5 increments)
            scores = critique_result.get("detailed_scores", {})
            total = 0
            valid_scores = [i * 0.5 for i in range(11)]  # [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
            
            for key, value in scores.items():
                if isinstance(value, (int, float)) and value in valid_scores:
                    total += value
                else:
                    print(f"⚠️  Invalid score {key}: {value}, setting to 0.5")
                    scores[key] = 0.5
                    total += 0.5
            
            critique_result["total_score"] = total
            return critique_result
        else:
            print("⚠️  Reviewer score parsing failed, using fallback values")
            return {
                "total_score": 4.0,
                "detailed_scores": {
                    "summary_quality": 1.0,
                    "keyword_relevance": 1.0,
                    "format_compliance": 1.0,
                    "physics_terminology": 1.0
                },
                "suggestions": [
                    "Evaluation system not functioning properly, manual review needed",
                    "Please verify API connection is stable",
                    "Recommend re-running evaluation"
                ]
            }
    
    def _parse_critique_json(self, raw_critique: str) -> Dict[str, Any]:
        """Parse reviewer's JSON output"""
        if not raw_critique:
            return None
        
        # Method 1: Direct parsing
        try:
            result = json.loads(raw_critique)
            if "total_score" in result and "detailed_scores" in result:
                return result
        except json.JSONDecodeError:
            pass
        
        # Method 2: Extract from markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.search(json_pattern, raw_critique, re.DOTALL)
        if matches:
            try:
                result = json.loads(matches.group(1))
                if "total_score" in result and "detailed_scores" in result:
                    return result
            except json.JSONDecodeError:
                pass
        
        # Method 3: Find JSON structure containing scores
        json_patterns = [
            r'\{.*?"total_score".*?"detailed_scores".*?\}',
            r'\{.*?"detailed_scores".*?"suggestions".*?\}',
        ]
        
        for pattern in json_patterns:
            matches = re.search(pattern, raw_critique, re.DOTALL)
            if matches:
                try:
                    result = json.loads(matches.group(0))
                    return result
                except json.JSONDecodeError:
                    continue
        
        print("❌ Unable to parse reviewer scores, raw response:")
        print(raw_critique[:500] + "..." if len(raw_critique) > 500 else raw_critique)
        return None
    
    def generator_improve_prompt(self, current_prompt: str, critique: Dict[str, Any]) -> str:
        """Generator role: Improve prompt based on reviewer suggestions"""
        print("\n🔧 GENERATOR starting prompt optimization...")
        
        improve_prompt = f"""
You are a professional prompt engineer. Please improve the existing physics paper analysis prompt based on the following evaluation results.

Current Prompt:
{current_prompt}

Evaluation Results:
Total Score: {critique.get('total_score', 4.0)}/20.0
Detailed Scores: {json.dumps(critique.get('detailed_scores', {}), ensure_ascii=False)}

Improvement Suggestions:
{json.dumps(critique.get('suggestions', []), ensure_ascii=False)}

Please redesign a better prompt based on the above suggestions, with requirements:
1. Improve the accuracy and completeness of summary extraction
2. Enhance the relevance and professionalism of keywords
3. Ensure output format stability
4. Keep the {{CONTENT}} placeholder

Please output the improved complete prompt directly, without additional explanatory text.
"""
        
        improved_prompt = self.call_openai(improve_prompt, "generator")
        
        if improved_prompt and len(improved_prompt) > 100:
            print(f"✅ Prompt optimized, new length: {len(improved_prompt)} characters")
            return improved_prompt
        else:
            print("⚠️  Prompt optimization failed, keeping original version")
            return current_prompt
    
    def run_evaluation_cycle(self, content: str, file_path: str = "", max_iterations: int = 3, auto_threshold: float = 15.0):
        """Execute complete evaluation cycle"""
        print(f"\n🚀 Starting AI self-evaluation cycle")
        print(f"📋 Auto-run condition: score < {auto_threshold}/20.0")
        print(f"📋 Maximum iterations: {max_iterations}")
        print("=" * 80)
        
        iteration = 1
        while iteration <= max_iterations:
            print(f"\n📍 Round {iteration} Evaluation")
            print("-" * 40)
            
            # Generator generates summary
            output = self.generator_extract(content)
            if not output:
                print("❌ Generator failed, terminating cycle")
                break
            
            # Display generated results
            self._display_results(output)
            
            # Save summary and keywords to file
            if file_path:
                save_summary_and_keywords(output, file_path)
            
            # Reviewer evaluation
            critique = self.reviewer_evaluate(content, output)
            current_score = critique.get("total_score", 0)
            
            print(f"\n📊 REVIEWER Evaluation Results:")
            print(f"Total Score: {current_score}/20.0 points")
            
            if "detailed_scores" in critique:
                print("Detailed Scores:")
                score_names = {
                    "summary_quality": "Summary Quality",
                    "keyword_relevance": "Keyword Relevance", 
                    "format_compliance": "Format Compliance",
                    "physics_terminology": "Physics Terminology"
                }
                for key, value in critique["detailed_scores"].items():
                    name = score_names.get(key, key)
                    print(f"  • {name}: {value}/5.0")
            
            print(f"\n💡 Improvement Suggestions:")
            for i, suggestion in enumerate(critique.get("suggestions", []), 1):
                print(f"  {i}. {suggestion}")
            
            # Determine whether to continue running
            if current_score < auto_threshold:
                # Score below threshold, automatically run next round
                if iteration < max_iterations:
                    print(f"\n🔄 Score ({current_score}/20.0) below auto-run threshold ({auto_threshold}/20.0)")
                    print("⚡ Automatically proceeding to next optimization round...")
                    
                    # Generator improves prompt
                    improved_prompt = self.generator_improve_prompt(self.current_prompt, critique)
                    
                    if improved_prompt != self.current_prompt:
                        self.current_prompt = improved_prompt
                        self.save_prompt(improved_prompt)
                        print("✅ Prompt updated and saved")
                    else:
                        print("⚠️  Prompt unchanged")
                    
                    iteration += 1
                    continue
                else:
                    print(f"\n⏹️  Maximum iterations ({max_iterations}) reached, evaluation cycle ended")
                    break
            else:
                # Score reaches good level, ask whether to continue
                print(f"\n🎯 Score ({current_score}/20.0) reaches good level!")
                
                if iteration < max_iterations:
                    user_choice = input("❓ Continue with next optimization round? (y/N): ").strip().lower()
                    
                    if user_choice in ['y', 'yes', '1', 'continue']:
                        print("🔄 Continuing with next optimization round...")
                        
                        # Generator improves prompt
                        improved_prompt = self.generator_improve_prompt(self.current_prompt, critique)
                        
                        if improved_prompt != self.current_prompt:
                            self.current_prompt = improved_prompt
                            self.save_prompt(improved_prompt)
                            print("✅ Prompt updated and saved")
                        else:
                            print("⚠️  Prompt unchanged")
                        
                        iteration += 1
                        continue
                    else:
                        print("✅ User chose to stop, evaluation cycle ended")
                        break
                else:
                    print(f"\n🎉 Maximum iterations reached, final score: {current_score}/20.0")
                    break
        
        print(f"\n🏁 Evaluation cycle completed")
        print(f"📊 Final evaluation result: {current_score}/20.0 points")
        
        # Final save with evaluation score
        if file_path:
            save_summary_and_keywords(output, file_path, current_score)
            print(f"💾 Final results saved with evaluation score")
        
        return output, critique
    
    def _display_results(self, output: Dict[str, Any]):
        """Display analysis results"""
        print(f"\n📋 GENERATOR Results:")
        print("-" * 30)
        
        if "summary_bullets" in output:
            print("🔹 Key Findings:")
            for i, bullet in enumerate(output["summary_bullets"], 1):
                print(f"  {i}. {bullet}")
        
        if "abstract" in output:
            print(f"\n📄 Abstract:")
            print(f"  {output['abstract']}")
        
        if "keywords" in output:
            print(f"\n🏷️  Keywords ({len(output['keywords'])} items):")
            for keyword in output["keywords"]:
                print(f"  • {keyword}")
        
        if "raw_output" in output:
            print(f"\n⚠️  Raw Output (unparsed):")
            print(f"  {output['raw_output'][:200]}...")

def read_file_content(file_path: str) -> str:
    """Read file content with multiple encoding support"""
    file_path = os.path.expanduser(file_path)
    file_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    # Support multiple encoding formats
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'gbk', 'big5']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✅ File read successfully (encoding: {encoding}), length: {len(content)} characters")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"⚠️  Failed to read with encoding {encoding}: {e}")
            continue
    
    raise ValueError("❌ Unable to read file with any encoding, please check file format")

def validate_api_key(api_key: str) -> bool:
    """Validate API Key format"""
    if not api_key:
        return False
    # Basic format check
    if not api_key.startswith(('sk-', 'sk-proj-')):
        print("⚠️  API Key format may be incorrect, but will attempt to use")
    return True

def get_user_input_with_validation():
    """Get and validate user input"""
    print("\n" + "="*50)
    print("🚀 AI Physics Paper Analysis System")
    print("="*50)
    
    # Get API Key
    while True:
        api_key = input("Enter OpenAI API Key: ").strip()
        if validate_api_key(api_key):
            break
        print("❌ API Key cannot be empty, please re-enter")
    
    # Get file path
    while True:
        file_path = input("Enter file path to analyze: ").strip()
        if file_path:
            # Try to read file for validation
            try:
                content = read_file_content(file_path)
                if len(content) < 100:
                    confirm = input(f"⚠️  File content is short ({len(content)} chars), continue? (y/N): ")
                    if confirm.lower() not in ['y', 'yes']:
                        continue
                return api_key, file_path, content
            except Exception as e:
                print(f"❌ {e}")
                print("Please check if file path is correct")
        else:
            print("❌ File path cannot be empty, please re-enter")

def main():
    """Main program - supports command line arguments and interactive mode"""
    parser = argparse.ArgumentParser(
        description="AI Physics Paper Analysis System - Automated Evaluation & Optimization",
        epilog="Example: python3 ai_converation.py -i 3 -t 15.0"
    )
    parser.add_argument("--max-iterations", "-i", type=int, default=3, 
                       help="Maximum iterations (default: 3)")
    parser.add_argument("--auto-threshold", "-t", type=float, default=15.0, 
                       help="Auto-run threshold score, max 20.0 (default: 15.0)")
    parser.add_argument("--api-key", "-k", 
                       help="OpenAI API Key (optional, will prompt if not provided)")
    parser.add_argument("--file-path", "-f", 
                       help="File path to analyze (optional, will prompt if not provided)")
    parser.add_argument("--version", "-v", action="version", version="AI Analysis System v2.0")
    
    args = parser.parse_args()
    
    try:
        # Display system information
        print("🚀 AI Self-Evaluation System Startup")
        print("=" * 50)
        print("Features:")
        print("• JSON file manages Prompt configuration")
        print("• Smart API Key and file path input")
        print("• Generator: Generate summaries and keywords")
        print("• Reviewer: 4 scoring criteria, max 5.0 points each (total 20.0 points)")
        print("• Scoring increments: 0.5 (0.0, 0.5, 1.0, 1.5, ... 5.0)")
        print(f"• Auto-run condition: score < {args.auto_threshold}/20.0")
        print("• Automatic Prompt optimization for improvement")
        print("=" * 50)
        
        # Get input parameters
        if args.api_key and args.file_path:
            # Command line mode
            api_key = args.api_key
            file_path = args.file_path
            content = read_file_content(file_path)
        else:
            # Interactive mode
            api_key, file_path, content = get_user_input_with_validation()
        
        # Initialize AI system
        print("\n🔧 Initializing AI system...")
        ai_system = AIEvaluationSystem(api_key)
        
        # Execute evaluation cycle
        print(f"\n📊 Starting analysis ({len(content)} characters)")
        final_output, final_critique = ai_system.run_evaluation_cycle(
            content, 
            file_path=file_path,
            max_iterations=args.max_iterations,
            auto_threshold=args.auto_threshold
        )
        
        # Display final results
        print(f"\n🎯 Analysis completed!")
        print("=" * 50)
        print(f"Final Score: {final_critique.get('total_score', 0)}/20.0")
        print(f"File Path: {file_path}")
        print(f"Config File: {CONFIG_FILE}")
        print("=" * 50)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted program")
        return 1
    except Exception as e:
        print(f"\n❌ System error: {e}")
        import traceback
        print("Detailed error information:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Set Python path to ensure correct module loading
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Execute main program
    exit_code = main()
    sys.exit(exit_code)
