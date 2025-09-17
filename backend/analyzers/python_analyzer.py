import ast
import os
from typing import List, Tuple, Dict, Any
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import subprocess
import json

from ..models.analysis_models import CodeIssue, FileMetrics, IssueSeverity, IssueCategory

class PythonAnalyzer:
    def __init__(self):
        self.duplicate_threshold = 0.8
        
    async def analyze(self, file_path: str, github_files: List[Dict] = None) -> Tuple[List[CodeIssue], FileMetrics]:
        """
        Analyze a Python file, either from local path or GitHub repository.
        
        Args:
            file_path: Path to the file to analyze
            github_files: Optional list of GitHub file dictionaries
            
        Returns:
            Tuple of (issues, metrics)
        """
        issues = []
        temp_file_path = None
        
        # Handle GitHub repository files
        if github_files:
            from .github_helpers import find_github_file_by_path, create_temp_file_from_github_data
            
            github_file = find_github_file_by_path(github_files, file_path)
            if github_file:
                content = github_file.get("content", "")
                temp_file_path = create_temp_file_from_github_data(content, file_path)
                analysis_file_path = temp_file_path
            else:
                return [], FileMetrics(
                    file_path=file_path,
                    language="python",
                    lines_of_code=0,
                    complexity_score=0.0,
                    duplication_percentage=0.0
                )
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            analysis_file_path = file_path
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            issues.append(CodeIssue(
                id=f"syntax_{file_path}",
                category=IssueCategory.STYLE,
                severity=IssueSeverity.HIGH,
                title="Syntax Error",
                description=f"Syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno,
                code_snippet="",
                suggestion="Fix the syntax error to enable proper analysis",
                impact_score=8.0
            ))
            
            metrics = FileMetrics(
                file_path=file_path,
                language="python",
                lines_of_code=len(content.splitlines()),
                complexity_score=0.0,
                duplication_percentage=0.0
            )
            
            if temp_file_path:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
            return issues, metrics
        
        complexity_issues = self._analyze_complexity(tree, content, file_path)
        issues.extend(complexity_issues)
        
        security_issues = await self._analyze_security(file_path)
        issues.extend(security_issues)
        
        secrets_issues = self._analyze_hardcoded_secrets(content, file_path)
        issues.extend(secrets_issues)
        
        duplication_issues = self._analyze_duplication(tree, file_path)
        issues.extend(duplication_issues)
        
        performance_issues = self._analyze_performance(tree, file_path)
        issues.extend(performance_issues)
        
        metrics = self._calculate_metrics(content, tree, file_path)
        
        return issues, metrics   
 
    def _generate_issue_id(self, file_path: str, line_number: int, title: str) -> str:
        """Generate a consistent, predictable ID for an issue."""
        normalized_title = ''.join(e for e in title if e.isalnum()).lower()
        return f"{os.path.basename(file_path)}-{line_number}-{normalized_title}"

    def _analyze_complexity(self, tree: ast.AST, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze code complexity"""
        issues = []
        
        try:
            complexity_results = cc_visit(content)
            
            for result in complexity_results:
                if result.complexity > 10: 
                    severity = IssueSeverity.HIGH if result.complexity > 15 else IssueSeverity.MEDIUM
                    title = f"High Complexity in {result.name}"
                    
                    issues.append(CodeIssue(
                        id=self._generate_issue_id(file_path, result.lineno, title),
                        category=IssueCategory.COMPLEXITY,
                        severity=severity,
                        title=title,
                        description=f"Function/method has cyclomatic complexity of {result.complexity}",
                        file_path=file_path,
                        line_number=result.lineno,
                        code_snippet="",
                        suggestion="Consider breaking this function into smaller, more focused functions",
                        impact_score=min(result.complexity / 2, 10.0)
                    ))
        except Exception as e:
            print(f"Complexity analysis failed for {file_path}: {e}")
        
        return issues
    
    async def _analyze_security(self, file_path: str) -> List[CodeIssue]:
        """Analyze security issues using bandit"""
        issues = []
        
        try:
            # here Running bandit on the file
            result = subprocess.run(
                ['bandit', '-f', 'json', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                bandit_data = json.loads(result.stdout)
                
                for finding in bandit_data.get('results', []):
                    severity_map = {
                        'LOW': IssueSeverity.LOW,
                        'MEDIUM': IssueSeverity.MEDIUM,
                        'HIGH': IssueSeverity.HIGH
                    }
                    
                    issues.append(CodeIssue(
                        id=self._generate_issue_id(file_path, finding['line_number'], finding['test_name']),
                        category=IssueCategory.SECURITY,
                        severity=severity_map.get(finding['issue_severity'], IssueSeverity.MEDIUM),
                        title=finding['test_name'],
                        description=finding['issue_text'],
                        file_path=file_path,
                        line_number=finding['line_number'],
                        code_snippet=finding.get('code', ''),
                        suggestion="Review and fix the security vulnerability",
                        impact_score=float(finding.get('confidence', 5))
                    ))
        except Exception as e:
            print(f"Security analysis failed for {file_path}: {e}")
        
        return issues    

    def _analyze_duplication(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Analyze code duplication"""
        issues = []
        
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'lineno': node.lineno,
                    'body_hash': hash(ast.dump(node.body[0]) if node.body else "")
                }
                functions.append(func_info)
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                if func1['body_hash'] == func2['body_hash'] and func1['name'] != func2['name']:
                    title = "Duplicate code detected"
                    issues.append(CodeIssue(
                        id=self._generate_issue_id(file_path, func1['lineno'], title),
                        category=IssueCategory.DUPLICATION,
                        severity=IssueSeverity.MEDIUM,
                        title=title,
                        description=f"Functions '{func1['name']}' and '{func2['name']}' have similar implementations",
                        file_path=file_path,
                        line_number=func1['lineno'],
                        code_snippet="",
                        suggestion="Consider extracting common functionality into a shared function",
                        impact_score=6.0
                    ))
        
        return issues
    
    def _analyze_performance(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Analyze performance issues"""
        issues = []
        
            # here Checking for inefficient loops and nested loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.For) and child != node:
                        title = "Nested loops detected"
                        issues.append(CodeIssue(
                            id=self._generate_issue_id(file_path, node.lineno, title),
                            category=IssueCategory.PERFORMANCE,
                            severity=IssueSeverity.MEDIUM,
                            title=title,
                            description="Nested loops can impact performance",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet="",
                            suggestion="Consider optimizing the algorithm or using more efficient data structures",
                            impact_score=5.0
                        ))
                        break
        
        return issues
    
    def _calculate_metrics(self, content: str, tree: ast.AST, file_path: str) -> FileMetrics:
        """Calculate file metrics"""
        lines_of_code = len([line for line in content.splitlines() if line.strip()])
        
        # Calculate average complexity
        try:
            complexity_results = cc_visit(content)
            avg_complexity = sum(r.complexity for r in complexity_results) / len(complexity_results) if complexity_results else 0
        except:
            avg_complexity = 0
        
        return FileMetrics(
            file_path=file_path,
            language="python",
            lines_of_code=lines_of_code,
            complexity_score=avg_complexity,
            duplication_percentage=0.0 
        )    

    def _analyze_hardcoded_secrets(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze for hardcoded secrets and API keys"""
        issues = []
        lines = content.splitlines()
        
        secret_patterns = [
            # API Keys
            (r'["\']?API_?KEY["\']?\s*=\s*["\'][^"\']{20,}["\']', 'API Key', 'critical'),
            (r'["\']?GOOGLE_API_KEY["\']?\s*=\s*["\'][^"\']{20,}["\']', 'Google API Key', 'critical'),
            (r'["\']?OPENAI_API_KEY["\']?\s*=\s*["\'][^"\']{20,}["\']', 'OpenAI API Key', 'critical'),
            (r'["\']?AWS_ACCESS_KEY["\']?\s*=\s*["\'][^"\']{16,}["\']', 'AWS Access Key', 'critical'),
            
            # Database credentials
            (r'["\']?PASSWORD["\']?\s*=\s*["\'][^"\']{6,}["\']', 'Hardcoded Password', 'high'),
            (r'["\']?DB_PASSWORD["\']?\s*=\s*["\'][^"\']{6,}["\']', 'Database Password', 'high'),
            
            # Tokens
            (r'["\']?TOKEN["\']?\s*=\s*["\'][^"\']{20,}["\']', 'Access Token', 'high'),
            (r'["\']?SECRET["\']?\s*=\s*["\'][^"\']{16,}["\']', 'Secret Key', 'high'),
            
            # Common secret formats
            (r'["\'][A-Za-z0-9]{32,}["\']', 'Potential Secret (32+ chars)', 'medium'),
            (r'sk-[A-Za-z0-9]{32,}', 'OpenAI Secret Key Format', 'critical'),
            (r'AIza[A-Za-z0-9_-]{35}', 'Google API Key Format', 'critical'),
            (r'AKIA[A-Z0-9]{16}', 'AWS Access Key Format', 'critical'),
        ]
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            
            if line_stripped.startswith('#') or not line_stripped:
                continue
            
            for pattern, secret_type, severity in secret_patterns:
                import re
                if re.search(pattern, line, re.IGNORECASE):
                  
                    if self._is_likely_secret(line, secret_type):
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
                            description=f"Found hardcoded {secret_type.lower()} in source code",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line_stripped,
                            suggestion=f"Move {secret_type.lower()} to environment variables or secure configuration",
                            impact_score=9.0 if severity == 'critical' else 7.0
                        ))
                        break  # Only report one issue per line
        
        return issues
    
    def _is_likely_secret(self, line: str, secret_type: str) -> bool:
        """Additional validation to reduce false positives"""
        line_lower = line.lower()
        
        test_indicators = [
            'test', 'example', 'dummy', 'fake', 'mock', 'sample',
            'your_key_here', 'replace_me', 'todo', 'fixme',
            '123456', 'abcdef', 'xxxxxx'
        ]
        
        for indicator in test_indicators:
            if indicator in line_lower:
                return False
        
        if 'os.getenv' in line or 'environ' in line:
            return False
        
        if line.strip().startswith('#'):
            return False
        
        return True