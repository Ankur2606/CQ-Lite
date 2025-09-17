import json
import subprocess
from typing import List, Tuple
from pathlib import Path

from ..models.analysis_models import CodeIssue, FileMetrics, IssueSeverity, IssueCategory

class JavaScriptAnalyzer:
    def __init__(self):
        self.complexity_threshold = 10
        
    async def analyze(self, file_path: str, github_files=None) -> Tuple[List[CodeIssue], FileMetrics]:
        """
        Analyze a JavaScript/TypeScript file, either local or from GitHub
        
        Args:
            file_path: Path to the file
            github_files: Optional list of GitHub file dictionaries
            
        Returns:
            Tuple of (issues, metrics)
        """
        issues = []
        
        # Check if we have GitHub files
        if github_files:
            from backend.analyzers.github_helpers import find_github_file_by_path
            github_file = find_github_file_by_path(github_files, file_path)
            if github_file:
                content = github_file.get("content", "")
            else:
                # Fall back to local file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        else:
            # Read local file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Basic syntax and structure analysis
        syntax_issues = self._analyze_syntax(content, file_path)
        issues.extend(syntax_issues)
        
        # Performance analysis
        performance_issues = self._analyze_performance(content, file_path)
        issues.extend(performance_issues)
        
        # Security analysis
        security_issues = self._analyze_security(content, file_path)
        issues.extend(security_issues)
        
        # Code quality analysis
        quality_issues = self._analyze_code_quality(content, file_path)
        issues.extend(quality_issues)
        
        # Hardcoded secrets detection
        secrets_issues = self._analyze_hardcoded_secrets(content, file_path)
        issues.extend(secrets_issues)
        
        # Calculate metrics
        metrics = self._calculate_metrics(content, file_path)
        
        return issues, metrics
    
    def _analyze_syntax(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze syntax and basic structure"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for console.log statements
            if 'console.log' in line and not line.startswith('//'):
                issues.append(CodeIssue(
                    id=f"console_{file_path}_{i}",
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.LOW,
                    title="Console statement found",
                    description="Console.log statement should be removed in production",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line,
                    suggestion="Remove console.log or use proper logging",
                    impact_score=2.0
                ))
            
            # Check for var usage
            if line.startswith('var '):
                issues.append(CodeIssue(
                    id=f"var_{file_path}_{i}",
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.LOW,
                    title="Use of 'var' keyword",
                    description="'var' has function scope, consider using 'let' or 'const'",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line,
                    suggestion="Replace 'var' with 'let' or 'const'",
                    impact_score=3.0
                ))
        
        return issues  
  
    def _analyze_performance(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze performance issues"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for inefficient DOM queries
            if 'document.getElementById' in line or 'document.querySelector' in line:
                # Look for repeated queries in loops
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                context = '\n'.join(lines[context_start:context_end])
                
                if 'for' in context or 'while' in context:
                    issues.append(CodeIssue(
                        id=f"dom_query_{file_path}_{i}",
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.MEDIUM,
                        title="DOM query in loop",
                        description="DOM queries inside loops can impact performance",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line,
                        suggestion="Cache DOM elements outside the loop",
                        impact_score=6.0
                    ))
        
        return issues
    
    def _analyze_security(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze security issues"""
        issues = []
        lines = content.splitlines()
        
        security_patterns = [
            ('eval(', 'Use of eval() function', 'Avoid eval() as it can execute arbitrary code'),
            ('innerHTML', 'Use of innerHTML', 'Consider using textContent or proper sanitization'),
            ('document.write', 'Use of document.write', 'Use modern DOM manipulation methods'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, title, suggestion in security_patterns:
                if pattern in line and not line.strip().startswith('//'):
                    issues.append(CodeIssue(
                        id=f"security_{pattern.replace('(', '')}_{file_path}_{i}",
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.HIGH if pattern == 'eval(' else IssueSeverity.MEDIUM,
                        title=title,
                        description=f"Potentially unsafe use of {pattern}",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion=suggestion,
                        impact_score=8.0 if pattern == 'eval(' else 5.0
                    ))
        
        return issues
    
    def _analyze_code_quality(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze code quality issues"""
        issues = []
        lines = content.splitlines()
        
        # Check for long functions (simple heuristic)
        in_function = False
        function_start = 0
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'function' in stripped or '=>' in stripped:
                in_function = True
                function_start = i
                brace_count = 0
            
            if in_function:
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count == 0 and i > function_start:
                    function_length = i - function_start
                    if function_length > 50:  # Long function threshold
                        issues.append(CodeIssue(
                            id=f"long_function_{file_path}_{function_start}",
                            category=IssueCategory.COMPLEXITY,
                            severity=IssueSeverity.MEDIUM,
                            title="Long function detected",
                            description=f"Function is {function_length} lines long",
                            file_path=file_path,
                            line_number=function_start,
                            code_snippet="",
                            suggestion="Consider breaking this function into smaller functions",
                            impact_score=4.0
                        ))
                    in_function = False
        
        return issues
    
    def _calculate_metrics(self, content: str, file_path: str) -> FileMetrics:
        """Calculate file metrics"""
        lines = content.splitlines()
        lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        # Simple complexity estimation based on control structures
        complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch']
        complexity_score = sum(content.count(keyword) for keyword in complexity_keywords)
        
        file_ext = Path(file_path).suffix.lower()
        language = {
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx'
        }.get(file_ext, 'javascript')
        
        return FileMetrics(
            file_path=file_path,
            language=language,
            lines_of_code=lines_of_code,
            complexity_score=complexity_score,
            duplication_percentage=0.0  # Simplified for now
        )
        
    def _analyze_hardcoded_secrets(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze for hardcoded secrets and API keys in JavaScript"""
        issues = []
        lines = content.splitlines()
        
        # Patterns for detecting hardcoded secrets in JavaScript
        secret_patterns = [
            # API Keys
            (r'["\']?API_?KEY["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', 'API Key', 'critical'),
            (r'["\']?GOOGLE_API_KEY["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', 'Google API Key', 'critical'),
            (r'["\']?OPENAI_API_KEY["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', 'OpenAI API Key', 'critical'),
            
            # Environment variables being set (bad practice)
            (r'process\.env\.[A-Z_]+\s*=\s*["\'][^"\']{16,}["\']', 'Environment Variable Assignment', 'high'),
            
            # Common secret formats
            (r'["\']sk-[A-Za-z0-9]{32,}["\']', 'OpenAI Secret Key Format', 'critical'),
            (r'["\']AIza[A-Za-z0-9_-]{35}["\']', 'Google API Key Format', 'critical'),
            (r'["\']AKIA[A-Z0-9]{16}["\']', 'AWS Access Key Format', 'critical'),
            
            # Generic long strings that might be secrets
            (r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']', 'Potential Base64 Secret', 'medium'),
        ]
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments and empty lines
            if line_stripped.startswith('//') or line_stripped.startswith('/*') or not line_stripped:
                continue
            
            for pattern, secret_type, severity in secret_patterns:
                import re
                if re.search(pattern, line, re.IGNORECASE):
                    # Additional validation to reduce false positives
                    if self._is_likely_secret_js(line, secret_type):
                        severity_enum = {
                            'critical': IssueSeverity.CRITICAL,
                            'high': IssueSeverity.HIGH,
                            'medium': IssueSeverity.MEDIUM
                        }.get(severity, IssueSeverity.HIGH)
                        
                        issues.append(CodeIssue(
                            id=f"hardcoded_secret_{file_path}_{i}",
                            category=IssueCategory.SECURITY,
                            severity=severity_enum,
                            title=f"Hardcoded {secret_type} Detected",
                            description=f"Found hardcoded {secret_type.lower()} in JavaScript code",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line_stripped,
                            suggestion=f"Move {secret_type.lower()} to environment variables or secure configuration",
                            impact_score=9.0 if severity == 'critical' else 7.0
                        ))
                        break  # Only report one issue per line
        
        return issues
        
    def _is_likely_secret_js(self, line: str, secret_type: str) -> bool:
        """Additional validation to reduce false positives for JavaScript"""
        line_lower = line.lower()
        
        # Skip obvious test/example values
        test_indicators = [
            'test', 'example', 'dummy', 'fake', 'mock', 'sample',
            'your_key_here', 'replace_me', 'todo', 'fixme',
            '123456', 'abcdef', 'xxxxxx'
        ]
        
        for indicator in test_indicators:
            if indicator in line_lower:
                return False
        
        # Skip if it's reading from environment variables
        if 'process.env' in line and '=' not in line.split('process.env')[0]:
            return False
        
        # Skip if it's in a comment
        if line.strip().startswith('//'):
            return False
        
        return True