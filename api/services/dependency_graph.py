"""
Dependency graph generation service
"""

from typing import Dict, List, Any, Set, Tuple
from fastapi import Depends
import os
import ast
import re
import json
from pathlib import Path

from api.models.api_models import DependencyGraph, GraphNode, GraphLink

class DependencyGraphService:
    """Service for generating dependency graphs from code"""
    
    def __init__(self):
        """Initialize the dependency graph service"""
        pass
    
    async def generate_graph(self, path: str) -> DependencyGraph:
        """
        Generate a dependency graph for code at the given path
        
        Args:
            path: Path to the code to analyze
            
        Returns:
            Dependency graph data structure
        """
        try:
            print(f"Generating dependency graph for path: {path}")
            
            # Find all relevant files
            py_files = self._find_files(path, [".py"])
            js_files = self._find_files(path, [".js", ".jsx", ".ts", ".tsx"])
            docker_files = self._find_files(path, ["Dockerfile"])
            
            print(f"Found {len(py_files)} Python files, {len(js_files)} JavaScript files, and {len(docker_files)} Docker files")
            
            # Extract dependencies
            py_dependencies = self._extract_python_dependencies(py_files)
            js_dependencies = self._extract_js_dependencies(js_files)
            docker_dependencies = self._extract_docker_dependencies(docker_files)
            
            # Combine all dependencies
            dependencies = {**py_dependencies, **js_dependencies, **docker_dependencies}
            
            # Create graph nodes and links
            nodes, links = self._create_graph_structure(dependencies)
            
            # Return the graph
            return DependencyGraph(nodes=nodes, links=links)
        except Exception as e:
            import traceback
            print(f"Error generating dependency graph: {str(e)}")
            print(traceback.format_exc())
            # Return an empty graph as fallback
            return DependencyGraph(nodes=[], links=[])
    
    def _find_files(self, path: str, extensions: List[str]) -> List[str]:
        """Find all files with the given extensions in the path"""
        files = []
        
        # Make sure path exists
        if not os.path.exists(path):
            print(f"Warning: Path does not exist: {path}")
            return []
        
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions) or any(filename == ext for ext in extensions):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, path)
                    # Store full path instead of relative path
                    files.append(full_path)
        
        return files
    
    def _extract_python_dependencies(self, files: List[str]) -> Dict[str, List[str]]:
        """Extract import dependencies from Python files"""
        dependencies = {}
        
        for file_path in files:
            try:
                # Get the absolute path if it's not already absolute
                abs_path = file_path if os.path.isabs(file_path) else os.path.abspath(file_path)
                
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    # Handle direct imports
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(name.name)
                    
                    # Handle from imports
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                # Store the dependencies
                dependencies[file_path] = imports
                
            except Exception as e:
                print(f"Error parsing {file_path}: {str(e)}")
                dependencies[file_path] = []
        
        return dependencies
    
    def _extract_js_dependencies(self, files: List[str]) -> Dict[str, List[str]]:
        """Extract import dependencies from JavaScript/TypeScript files"""
        dependencies = {}
        
        # Regular expressions for JS imports
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"](.+?)[\'"]',  # ES6 imports
            r'require\(\s*[\'"](.+?)[\'"]\s*\)',       # CommonJS requires
        ]
        
        for file_path in files:
            try:
                # Get the absolute path if it's not already absolute
                abs_path = file_path if os.path.isabs(file_path) else os.path.abspath(file_path)
                
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = []
                
                # Find all imports using regex patterns
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    imports.extend(matches)
                
                # Store the dependencies
                dependencies[file_path] = imports
                
            except Exception as e:
                print(f"Error parsing {file_path}: {str(e)}")
                dependencies[file_path] = []
        
        return dependencies
    
    def _extract_docker_dependencies(self, files: List[str]) -> Dict[str, List[str]]:
        """Extract dependencies from Dockerfile"""
        dependencies = {}
        
        # Regular expressions for Dockerfile references
        from_pattern = r'FROM\s+(.+?)(?:\s+AS\s+(.+?))?(?:\s|$)'
        copy_from_pattern = r'COPY\s+--from=(.+?)\s+'
        
        for file_path in files:
            try:
                # Get the absolute path if it's not already absolute
                abs_path = file_path if os.path.isabs(file_path) else os.path.abspath(file_path)
                
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = []
                
                # Find all FROM statements
                from_matches = re.findall(from_pattern, content, re.IGNORECASE)
                for match in from_matches:
                    base_image = match[0].strip()
                    imports.append(f"docker:{base_image}")
                
                # Find all COPY --from statements
                copy_matches = re.findall(copy_from_pattern, content, re.IGNORECASE)
                imports.extend(copy_matches)
                
                # Store the dependencies
                dependencies[file_path] = imports
                
            except Exception as e:
                print(f"Error parsing {file_path}: {str(e)}")
                dependencies[file_path] = []
        
        return dependencies
    
    def _create_graph_structure(self, dependencies: Dict[str, List[str]]) -> Tuple[List[GraphNode], List[GraphLink]]:
        """Create graph nodes and links from dependencies"""
        nodes = []
        links = []
        
        # Set to track unique nodes
        unique_nodes = set()
        
        # Helper function to determine file type and group
        def get_file_type_and_group(file_path: str) -> Tuple[str, int]:
            if file_path.endswith('.py'):
                return 'python', 1
            elif file_path.endswith(('.js', '.jsx')):
                return 'javascript', 2
            elif file_path.endswith(('.ts', '.tsx')):
                return 'typescript', 3
            elif file_path.endswith('Dockerfile') or 'Dockerfile' in file_path:
                return 'docker', 4
            else:
                return 'other', 5
        
        # Add all source files as nodes
        for file_path in dependencies.keys():
            if file_path not in unique_nodes:
                file_type, group = get_file_type_and_group(file_path)
                
                # Get display path (filename only or relative path for better readability)
                try:
                    display_name = os.path.basename(file_path)
                except:
                    display_name = file_path
                
                # Size is roughly proportional to the number of dependencies
                size = 100 + 20 * len(dependencies.get(file_path, []))
                
                nodes.append(GraphNode(
                    id=file_path,
                    name=display_name,  # Add display name for better visualization
                    group=group,
                    type=file_type,
                    size=size
                ))
                unique_nodes.add(file_path)
        
        # Add links between files
        for source, imports in dependencies.items():
            for target_import in imports:
                # For standard libraries and external packages, we skip creating links
                if not target_import.startswith(('/', '.')) and not any(target_import.endswith(ext) for ext in ['.py', '.js', '.jsx', '.ts', '.tsx']):
                    continue
                
                # Find target files that match the import
                for potential_target in dependencies.keys():
                    target_basename = os.path.basename(potential_target)
                    import_basename = os.path.basename(target_import) if '/' in target_import or '\\' in target_import else target_import
                    
                    # Check various ways the import might match the target
                    if (potential_target == target_import or
                        potential_target.endswith(f"/{target_import}") or 
                        potential_target.endswith(f"\\{target_import}") or
                        potential_target.endswith(f"/{target_import}.py") or
                        potential_target.endswith(f"\\{target_import}.py") or
                        target_basename == import_basename or
                        target_basename == f"{import_basename}.py"):
                        
                        links.append(GraphLink(
                            source=source,
                            target=potential_target,
                            value=1
                        ))
                        break
        
        return nodes, links


# Dependency injection for the graph service
def get_graph_service() -> DependencyGraphService:
    """Dependency for the graph service"""
    return DependencyGraphService()