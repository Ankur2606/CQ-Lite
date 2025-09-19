import os
import ast
import time
from pathlib import Path
from typing import List, Dict, Any
import asyncio

from ..models.analysis_models import AnalysisResult, CodeIssue, FileMetrics
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer


class CodeAnalyzer:
    def __init__(self):
        self.python_analyzer = PythonAnalyzer()
        self.js_analyzer = JavaScriptAnalyzer()
        
    async def analyze_path(self, path: str, include_patterns: List[str] = None, generate_insights: bool = False) -> AnalysisResult:
        """Analyze code at the given path"""
        start_time = time.time()
        
        if include_patterns is None:
            include_patterns = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]
        
        files = self._collect_files(path, include_patterns)
        
        all_issues = []
        all_metrics = []
        total_lines = 0
        
        for file_path in files:
            try:
                file_issues, file_metrics = await self._analyze_file(file_path)
                all_issues.extend(file_issues)
                all_metrics.append(file_metrics)
                total_lines += file_metrics.lines_of_code
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue
        
    
        if generate_insights and all_issues:
            all_issues = await self._generate_ai_insights(all_issues)
        
    
        summary = self._generate_summary(all_issues, all_metrics)
        
        analysis_duration = time.time() - start_time
        
        return AnalysisResult(
            summary=summary,
            issues=all_issues,
            metrics=all_metrics,
            total_files=len(files),
            total_lines=total_lines,
            analysis_duration=analysis_duration
        )
    
    def _collect_files(self, path: str, patterns: List[str]) -> List[str]:
        """Collect files matching the patterns"""
        files = []
        path_obj = Path(path)
        
        if path_obj.is_file():
            return [str(path_obj)]
        
        for pattern in patterns:
            files.extend(path_obj.rglob(pattern))
        
        return [str(f) for f in files if f.is_file()]
    
    async def _analyze_file(self, file_path: str) -> tuple[List[CodeIssue], FileMetrics]:
        """Analyze a single file"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            return await self.python_analyzer.analyze(file_path)
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            return await self.js_analyzer.analyze(file_path)
        else:
        
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = len(content.splitlines())
            
            metrics = FileMetrics(
                file_path=file_path,
                language="unknown",
                lines_of_code=lines,
                complexity_score=0.0,
                duplication_percentage=0.0
            )
            return [], metrics
    
    def _generate_summary(self, issues: List[CodeIssue], metrics: List[FileMetrics]) -> Dict[str, Any]:
        """Generate analysis summary"""
        severity_counts = {}
        category_counts = {}
        
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        avg_complexity = sum(m.complexity_score for m in metrics) / len(metrics) if metrics else 0
        avg_duplication = sum(m.duplication_percentage for m in metrics) / len(metrics) if metrics else 0
        
        return {
            "total_issues": len(issues),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "average_complexity": round(avg_complexity, 2),
            "average_duplication": round(avg_duplication, 2),
            "languages_detected": list(set(m.language for m in metrics))
        }
    
    async def _generate_ai_insights(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Generate AI-powered resolution insights for issues"""
        try:
            from ..services.gemini_service import GeminiService
            gemini_service = GeminiService()
            
        
            batch_size = 5
            updated_issues = []
            
            for i in range(0, len(issues), batch_size):
                batch = issues[i:i + batch_size]
                
            
                issues_context = []
                for idx, issue in enumerate(batch):
                    issues_context.append(f"""
                    Issue {idx + 1}:
                    - Type: {issue.category} ({issue.severity})
                    - Title: {issue.title}
                    - Description: {issue.description}
                    - File: {issue.file_path}:{issue.line_number or 'N/A'}
                    - Current Suggestion: {issue.suggestion}
                    """)
                    
                prompt = f"""
                As a senior developer, provide CONCISE, actionable fixes for these code issues. Keep responses brief and practical.

                For each issue, provide:
                - Quick fix (1-2 sentences max)
                - Short code example (before/after)
                - Why it matters (1 sentence)

                Issues:
                {''.join(issues_context)}

                Respond in JSON:
                {{
                "insights": [
                    {{
                    "issue_index": 0,
                    "quick_fix": "Replace subprocess.run(['bandit', ...]) with subprocess.run(['/usr/bin/bandit', ...]) to use absolute path",
                    "code_before": "subprocess.run(['bandit', '-f', 'json', file_path])",
                    "code_after": "subprocess.run(['/usr/bin/bandit', '-f', 'json', file_path])",
                    "why_important": "Prevents PATH manipulation attacks"
                    }}
                ]
                }}
                """
                
                try:
                    response = await gemini_service.chat(prompt)
                    
                
                    import json
                    import re
                    
                
                    json_match = re.search(r'\{.*\}', response.message, re.DOTALL)
                    if json_match:
                        ai_insights = json.loads(json_match.group())
                        
                        for insight in ai_insights.get('insights', []):
                            issue_idx = insight.get('issue_index', 0)
                            if issue_idx < len(batch):
                                issue = batch[issue_idx]
                                
                            
                                enhanced_suggestion = self._format_ai_insight(insight)
                                issue.suggestion = enhanced_suggestion
                    
                except Exception as e:
                        print(f"Error generating AI insights for batch: {e}")
                    
                        pass
                
                updated_issues.extend(batch)
            
            return updated_issues
            
        except Exception as e:
            print(f"Error initializing AI insights: {e}")
            return issues  # Return original issues if AI service fails
    
    def _format_ai_insight(self, insight: Dict[str, Any]) -> str:
        """Format AI insight into a concise, readable suggestion"""
        formatted = []
        
    
        if 'quick_fix' in insight:
            formatted.append(f"🔧 Fix: {insight['quick_fix']}")
        
    
        if 'code_before' in insight and 'code_after' in insight:
            formatted.append(f"📝 Before: {insight['code_before']}")
            formatted.append(f"   After:  {insight['code_after']}")
        
    
        if 'why_important' in insight:
            formatted.append(f"⚠️  Why: {insight['why_important']}")
        
        return '\n'.join(formatted) if formatted else "AI insights not available"