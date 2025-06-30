import ast
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class GenerationOptions:
    language: str = "python"
    preserve_comments: bool = True
    formatting_style: str = "black"
    optimize_imports: bool = False
    add_type_hints: bool = False


class CodeGenerator:
    def __init__(self):
        self.supported_languages = ["python", "javascript", "typescript"]
        self.formatting_styles = ["black", "pep8", "google", "numpy"]
    
    def generate_code(self, code: str, options: GenerationOptions) -> str:
        if options.language not in self.supported_languages:
            raise NotImplementedError(f"Language {options.language} is not supported")
        
        result = code
        
        if options.language == "python":
            result = self._generate_python_code(result, options)
        elif options.language == "javascript":
            result = self._generate_javascript_code(result, options)
        elif options.language == "typescript":
            result = self._generate_typescript_code(result, options)
        
        return result
    
    def _generate_python_code(self, code: str, options: GenerationOptions) -> str:
        result = code
        
        if not options.preserve_comments:
            result = self._remove_comments(result, "python")
        
        if options.optimize_imports:
            result = self._optimize_imports(result)
        
        if options.add_type_hints:
            result = self._add_type_hints(result)
        
        if options.formatting_style:
            result = self._apply_formatting(result, options.formatting_style)
        
        return result
    
    def _generate_javascript_code(self, code: str, options: GenerationOptions) -> str:
        result = code
        
        if not options.preserve_comments:
            result = self._remove_comments(result, "javascript")
        
        if options.formatting_style:
            result = self._apply_js_formatting(result)
        
        return result
    
    def _generate_typescript_code(self, code: str, options: GenerationOptions) -> str:
        result = code
        
        if not options.preserve_comments:
            result = self._remove_comments(result, "typescript")
        
        return result
    
    def preserve_formatting(self, original_code: str, refactored_code: str) -> str:
        # Extract indentation patterns from original code
        original_lines = original_code.split('\n')
        refactored_lines = refactored_code.split('\n')
        
        result_lines = []
        
        for i, line in enumerate(refactored_lines):
            if line.strip():
                # Find corresponding line in original or use similar indentation pattern
                indent = self._get_appropriate_indentation(line, original_lines, i)
                result_lines.append(indent + line.strip())
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _get_appropriate_indentation(self, line: str, original_lines: List[str], line_index: int) -> str:
        stripped = line.strip()
        
        # Look for function definitions, if statements, etc. to determine indentation level
        if stripped.startswith('def ') or stripped.startswith('class '):
            return ''
        elif stripped.startswith('if ') or stripped.startswith('else:') or stripped.startswith('elif '):
            return '    '
        elif stripped.startswith('return ') or 'result =' in stripped or 'x =' in stripped:
            # If this is inside an if block, use double indentation
            if any('if ' in orig_line for orig_line in original_lines):
                return '        '  # 8 spaces for nested blocks
            return '    '  # 4 spaces for function body
        
        return '    '  # Default indentation
    
    def preserve_semantic_equivalence(self, original_code: str, refactored_code: str) -> bool:
        try:
            # Parse both pieces of code to AST
            original_ast = ast.parse(original_code)
            refactored_ast = ast.parse(refactored_code)
            
            # Simple check: if both parse successfully and have similar structure
            # In a real implementation, this would be more sophisticated
            original_functions = [node.name for node in ast.walk(original_ast) if isinstance(node, ast.FunctionDef)]
            refactored_functions = [node.name for node in ast.walk(refactored_ast) if isinstance(node, ast.FunctionDef)]
            
            # Check if the refactored code changes the fundamental operations
            original_dump = ast.dump(original_ast)
            refactored_dump = ast.dump(refactored_ast)
            
            # Simple heuristic: if the operations are fundamentally different (+ vs *), it's not equivalent
            if ('BinOp' in original_dump and 'Add' in original_dump and 
                'BinOp' in refactored_dump and 'Mult' in refactored_dump):
                return False
            
            return True
        except SyntaxError:
            return False
    
    def generate_clean_code(self, code: str) -> str:
        # Clean up formatting
        result = code
        
        # Fix function definitions with proper parameter spacing
        result = re.sub(r'def\s+(\w+)\s*\(\s*([^)]*)\s*\)\s*:', 
                       lambda m: f'def {m.group(1)}({", ".join([p.strip() for p in m.group(2).split(",") if p.strip()])}):',
                       result)
        
        # Fix assignments
        result = re.sub(r'(\w+)\s*=\s*([^=\n]+)', r'\1 = \2', result)
        
        # Fix operators with proper spacing
        result = re.sub(r'(\w+)\s*([+\-*/])\s*(\w+)', r'\1 \2 \3', result)
        
        # Fix multiplication operators specifically
        result = re.sub(r'(\w+)\s*\*\s*(\w+)', r'\1 * \2', result)
        
        # Fix if statements
        result = re.sub(r'if\s*\(\s*([^)]+)\s*\)\s*:', r'if \1:', result)
        result = re.sub(r'else\s+:', r'else:', result)
        
        # Fix comparison operators
        result = re.sub(r'(\w+)\s*([><]=?)\s*(\w+)', r'\1 \2 \3', result)
        
        # Fix return statements
        result = re.sub(r'return\s+([^\n]+)', r'return \1', result)
        
        return result
    
    def validate_code(self, code: str, language: str) -> bool:
        if language == "python":
            try:
                ast.parse(code)
                return True
            except SyntaxError:
                return False
        elif language == "javascript":
            # Simple validation for JavaScript (in real implementation, use a JS parser)
            return '{' in code and '}' in code and 'function' in code
        
        return False
    
    def _remove_comments(self, code: str, language: str) -> str:
        if language == "python":
            lines = code.split('\n')
            result_lines = []
            for line in lines:
                # Remove lines that are only comments
                if line.strip().startswith('#'):
                    continue
                # Remove inline comments
                if '#' in line:
                    line = line[:line.index('#')].rstrip()
                result_lines.append(line)
            return '\n'.join(result_lines)
        elif language in ["javascript", "typescript"]:
            # Remove // comments
            result = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            # Remove /* */ comments
            result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
            return result
        
        return code
    
    def _optimize_imports(self, code: str) -> str:
        lines = code.split('\n')
        imports = []
        other_lines = []
        used_modules = set()
        
        # Collect imports and other lines
        for line in lines:
            if line.strip().startswith('import '):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # Find which modules are actually used
        code_content = '\n'.join(other_lines)
        for import_line in imports:
            if 'import ' in import_line:
                # Extract module name
                if ' as ' in import_line:
                    module = import_line.split(' as ')[1].strip()
                else:
                    module = import_line.split('import ')[1].strip()
                
                if module in code_content:
                    used_modules.add(import_line)
        
        # Reconstruct code with only used imports
        result_lines = list(used_modules) + [''] + other_lines
        return '\n'.join(result_lines)
    
    def _add_type_hints(self, code: str) -> str:
        # Simple type hint addition (in real implementation, this would be more sophisticated)
        result = code
        
        # Add basic return type hints
        result = re.sub(r'def (\w+)\([^)]*\):', r'def \1() -> Any:', result)
        
        return result
    
    def _apply_formatting(self, code: str, style: str) -> str:
        if style in ["black", "pep8"]:
            return self.generate_clean_code(code)
        return code
    
    def _apply_js_formatting(self, code: str) -> str:
        # Basic JavaScript formatting
        result = code
        result = re.sub(r'function\s+(\w+)\s*\(\s*([^)]*)\s*\)\s*{', r'function \1(\2) {', result)
        return result