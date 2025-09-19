"""
Docker file analyzer to detect common issues and best practices in Dockerfile.
"""
import os
import re
from typing import List, Tuple, Dict, Any
from ..models.analysis_models import CodeIssue, FileMetrics, IssueSeverity, IssueCategory

class DockerAnalyzer:
    """Analyzer for Docker files to identify common issues and best practices."""
    
    def __init__(self):
        self.base_image_patterns = {
            r'FROM\s+ubuntu(?::latest)?\s': 'Consider using a more specific tag than latest for reproducibility.',
            r'FROM\s+debian(?::latest)?\s': 'Consider using a more specific tag than latest for reproducibility.',
            r'FROM\s+alpine(?::latest)?\s': 'Consider using a more specific tag than latest for reproducibility.',
            r'FROM\s+node(?::latest)?\s': 'Consider using a more specific tag than latest for reproducibility.',
            r'FROM\s+python(?::latest)?\s': 'Consider using a more specific tag than latest for reproducibility.',
        }
        
        self.security_patterns = {
            r'apt-get\s+install\s+.*--no-install-recommends': 'Good practice: Using --no-install-recommends reduces image size.',
            r'apt-get\s+install(?!.*--no-install-recommends)': 'Consider adding --no-install-recommends to reduce image size.',
            r'apt-get\s+(?!clean).*(?<!&&\s+apt-get clean)': 'Missing apt-get clean after apt-get commands increases image size.',
            r'USER\s+root': 'Running as root in containers is a security risk. Consider using a non-root user.',
            r'COPY\s+.*\.env\s+': 'Copying .env files into Docker images may expose sensitive data.',
            r'ENV\s+.*PASSWORD': 'Hardcoded passwords or secrets in ENV variables are a security risk.',
            r'ENV\s+.*SECRET': 'Hardcoded secrets in ENV variables are a security risk.',
            r'ENV\s+.*TOKEN': 'Hardcoded tokens in ENV variables are a security risk.',
            r'ENV\s+.*KEY': 'Hardcoded keys in ENV variables are a security risk.',
        }
        
        self.best_practice_patterns = {
            r'ADD\s+': 'COPY is preferred over ADD for simple file copying, as ADD has some surprising behaviors.',
            r'RUN\s+.*(?<!\s&&)\s*apt-get\s+update(?!\s+&&)': 'apt-get update should be in the same layer as apt-get install.',
            r'RUN\s+.*(?<!\s&&)\s*pip\s+install(?!\s+&&)': 'Consider using pip install with a requirements.txt file for better caching.',
            r'RUN\s+.*(?<!\s&&)\s*npm\s+install(?!\s+&&)': 'Consider using npm ci with a package-lock.json for better reproducibility.',
            r'WORKDIR\s+\/(?!home|app|usr|opt|src)': 'Consider using a standard directory like /app, /home/app, or /usr/src/app.',
        }
        
    
        self.best_practices_checklist = [
            'MULTI_STAGE_BUILD',  # Check for multi-stage builds
            'LAYER_REDUCTION',
            'DOCKERIGNORE',   
            'SPECIFIC_TAG',   
            'NON_ROOT_USER',  
            'HEALTH_CHECK',   
            'EXPOSE_PORT',    
            'ENTRYPOINT_OR_CMD',  # Check for ENTRYPOINT or CMD
        ]
    
    async def analyze(self, file_path: str, github_files=None) -> Tuple[List[CodeIssue], FileMetrics]:
        """
        Analyze a Docker file for issues and best practices.
        
        Args:
            file_path: Path to the Dockerfile
            github_files: Optional list of GitHub file dictionaries
            
        Returns:
            Tuple of (issues, metrics)
        """
        issues = []
        
    
        if github_files:
            from backend.analyzers.github_helpers import find_github_file_by_path
            github_file = find_github_file_by_path(github_files, file_path)
            if github_file:
                content = github_file.get("content", "")
            else:
            
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
        else:
        
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        lines = content.splitlines()
        
    
        num_lines = len(lines)
        num_instructions = len(re.findall(r'^\s*(FROM|RUN|CMD|LABEL|EXPOSE|ENV|ADD|COPY|ENTRYPOINT|VOLUME|USER|WORKDIR|ARG|ONBUILD|HEALTHCHECK|SHELL)\s+', content, re.MULTILINE))
        
    
        has_multi_stage_build = len(re.findall(r'^\s*FROM\s+', content, re.MULTILINE)) > 1
        
    
        security_issues = self._analyze_security(content, file_path, lines)
        issues.extend(security_issues)
        
    
        best_practice_issues = self._analyze_best_practices(content, file_path, lines)
        issues.extend(best_practice_issues)
        
    
        base_image_issues = self._analyze_base_image(content, file_path, lines)
        issues.extend(base_image_issues)
        
    
        metrics = FileMetrics(
            file_path=file_path,
            language="docker",
            lines_of_code=num_lines,
            complexity_score=num_instructions / 5 if num_instructions else 1.0,  # Simple complexity heuristic
            duplication_percentage=0.0  # Not implemented for Docker files
        )
        
        return issues, metrics
    
    def _analyze_security(self, content: str, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze Dockerfile for security issues."""
        issues = []
        
    
        if not re.search(r'^\s*USER\s+', content, re.MULTILINE):
            issues.append(
                CodeIssue(
                    id=f"docker_security_root_user_{file_path}",
                    category=IssueCategory.SECURITY,
                    severity=IssueSeverity.MEDIUM,
                    title="Container runs as root user",
                    description="Running containers as root is a security risk. Consider adding a USER directive with a non-root user.",
                    file_path=file_path,
                    line_number=1,  # First line as no USER directive is found
                    code_snippet="# No USER directive found (container will run as root)",
                    suggestion="Add a USER directive with a non-root user.",
                    impact_score=7.0
                )
            )
        
    
        for i, line in enumerate(lines, 1):
            for pattern, message in self.security_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    severity = IssueSeverity.MEDIUM
                    impact = 5.0
                    
                
                    if "security risk" in message:
                        severity = IssueSeverity.HIGH
                        impact = 8.0
                    elif "good practice" in message.lower():
                    
                        continue
                    
                    issues.append(
                        CodeIssue(
                            id=f"docker_security_{i}_{file_path}",
                            category=IssueCategory.SECURITY,
                            severity=severity,
                            title="Docker security issue",
                            description=message,
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion=message,
                            impact_score=impact
                        )
                    )
        
        return issues
    
    def _analyze_best_practices(self, content: str, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze Dockerfile for best practice violations."""
        issues = []
        
    
        run_commands = re.findall(r'^\s*RUN\s+(.+)$', content, re.MULTILINE)
        if len(run_commands) > 3:  # More than 3 RUN commands might indicate too many layers
            run_with_multiple_commands = sum(1 for cmd in run_commands if "&&" in cmd)
            if run_with_multiple_commands / len(run_commands) < 0.5:  # Less than 50% use &&
                issues.append(
                    CodeIssue(
                        id=f"docker_best_practice_layers_{file_path}",
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.LOW,
                        title="Too many Docker layers",
                        description="Having too many RUN instructions creates unnecessary layers. Consider combining commands with && to reduce layers.",
                        file_path=file_path,
                        line_number=next((i for i, line in enumerate(lines, 1) if line.strip().startswith("RUN")), 1),
                        code_snippet="Multiple RUN instructions detected",
                        suggestion="Combine related RUN instructions with && to reduce layers.",
                        impact_score=4.0
                    )
                )
        
    
        if not re.search(r'^\s*(ENTRYPOINT|CMD)\s+', content, re.MULTILINE):
            issues.append(
                CodeIssue(
                    id=f"docker_best_practice_entrypoint_cmd_{file_path}",
                    category=IssueCategory.CORRECTNESS,
                    severity=IssueSeverity.MEDIUM,
                    title="Missing ENTRYPOINT or CMD",
                    description="A Dockerfile should have either an ENTRYPOINT or CMD instruction to specify what runs when the container starts.",
                    file_path=file_path,
                    line_number=len(lines),  # Last line as this is a general issue
                    code_snippet="# No ENTRYPOINT or CMD found",
                    suggestion="Add an ENTRYPOINT or CMD instruction to specify what should run when the container starts.",
                    impact_score=6.0
                )
            )
        
    
        for i, line in enumerate(lines, 1):
            for pattern, message in self.best_practice_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        CodeIssue(
                            id=f"docker_best_practice_{i}_{file_path}",
                            category=IssueCategory.STYLE,
                            severity=IssueSeverity.LOW,
                            title="Docker best practice issue",
                            description=message,
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion=message,
                            impact_score=3.5
                        )
                    )
        
        return issues
    
    def _analyze_base_image(self, content: str, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze Dockerfile base images for issues."""
        issues = []
        
    
        from_lines = [(i, line) for i, line in enumerate(lines, 1) if line.strip().startswith("FROM")]
        
        if not from_lines:
            issues.append(
                CodeIssue(
                    id=f"docker_base_missing_from_{file_path}",
                    category=IssueCategory.CORRECTNESS,
                    severity=IssueSeverity.HIGH,
                    title="Missing FROM instruction",
                    description="A valid Dockerfile must have a FROM instruction to specify the base image.",
                    file_path=file_path,
                    line_number=1,
                    code_snippet="# No FROM instruction found",
                    suggestion="Add a FROM instruction to specify the base image.",
                    impact_score=8.0
                )
            )
            return issues
        
    
        for i, line in from_lines:
        
            if ":latest" in line or not ":" in line:
                issues.append(
                    CodeIssue(
                        id=f"docker_base_latest_tag_{i}_{file_path}",
                        category=IssueCategory.MAINTAINABILITY,
                        severity=IssueSeverity.MEDIUM,
                        title="Using latest tag",
                        description="Using the 'latest' tag or no tag (which defaults to 'latest') makes builds non-reproducible.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Specify a fixed version tag for the base image.",
                        impact_score=6.0
                    )
                )
            
        
            if "ubuntu:16.04" in line or "ubuntu:14.04" in line or "debian:jessie" in line or "debian:stretch" in line:
                issues.append(
                    CodeIssue(
                        id=f"docker_base_outdated_{i}_{file_path}",
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.HIGH,
                        title="Outdated base image",
                        description="Using an outdated base image can introduce security vulnerabilities.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Update to a more recent base image version.",
                        impact_score=7.5
                    )
                )
            
        
            for pattern, message in self.base_image_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        CodeIssue(
                            id=f"docker_base_{i}_{file_path}",
                            category=IssueCategory.MAINTAINABILITY,
                            severity=IssueSeverity.LOW,
                            title="Base image issue",
                            description=message,
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion=message,
                            impact_score=4.0
                        )
                    )
        
        return issues