import ast
from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class ParseResult:
    functions: List[str]
    classes: List[str]
    methods: Dict[str, List[str]]


@dataclass
class CodeSmell:
    type: str
    line: int
    description: str


@dataclass
class RefactoringSuggestion:
    type: str
    description: str
    priority: str


@dataclass
class ASTNode:
    type: str
    children: List['ASTNode'] = None


class CodeAnalyzer:
    def __init__(self):
        self.max_method_lines = 20
        self.similarity_threshold = 0.8
    
    def parse_code(self, code: str, language: str) -> ParseResult:
        if language != "python":
            raise NotImplementedError(f"Language {language} not supported yet")
        
        if not code.strip():
            return ParseResult(functions=[], classes=[], methods={})
        
        tree = ast.parse(code)
        
        functions = []
        classes = []
        methods = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                parent = self._get_parent_class(tree, node)
                if parent:
                    if parent not in methods:
                        methods[parent] = []
                    methods[parent].append(node.name)
                else:
                    functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return ParseResult(functions=functions, classes=classes, methods=methods)
    
    def identify_code_smells(self, code: str, language: str) -> List[CodeSmell]:
        if language != "python":
            raise NotImplementedError(f"Language {language} not supported yet")
        
        smells = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = code.split('\n')[node.lineno - 1:node.end_lineno]
                method_length = len([l for l in lines if l.strip()])
                
                if method_length > self.max_method_lines:
                    smells.append(CodeSmell(
                        type="long_method",
                        line=node.lineno,
                        description=f"Method '{node.name}' is too long ({method_length} lines)"
                    ))
        
        duplicates = self._find_duplicate_code(tree)
        smells.extend(duplicates)
        
        return smells
    
    def generate_suggestions(self, code: str, language: str) -> List[RefactoringSuggestion]:
        if language != "python":
            raise NotImplementedError(f"Language {language} not supported yet")
        
        suggestions = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._has_many_conditionals(node):
                    suggestions.append(RefactoringSuggestion(
                        type="replace_conditionals",
                        description="Consider using strategy pattern or dictionary dispatch instead of multiple if/elif statements",
                        priority="medium"
                    ))
        
        return suggestions
    
    def extract_ast(self, code: str, language: str) -> ASTNode:
        if language != "python":
            raise NotImplementedError(f"Language {language} not supported yet")
        
        tree = ast.parse(code)
        return self._convert_ast_to_node(tree)
    
    def _get_parent_class(self, tree: ast.AST, func_node: ast.FunctionDef) -> Optional[str]:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if child == func_node:
                        return node.name
        return None
    
    def _find_duplicate_code(self, tree: ast.AST) -> List[CodeSmell]:
        smells = []
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                if self._are_similar(func1, func2):
                    smells.append(CodeSmell(
                        type="duplicate_code",
                        line=func1.lineno,
                        description=f"Functions '{func1.name}' and '{func2.name}' have similar code"
                    ))
                    break
        
        return smells
    
    def _are_similar(self, node1: ast.AST, node2: ast.AST) -> bool:
        lines1 = [line.strip() for line in ast.unparse(node1).split('\n') if line.strip()]
        lines2 = [line.strip() for line in ast.unparse(node2).split('\n') if line.strip()]
        
        lines1_normalized = [line.replace(node1.name, 'FUNC') for line in lines1]
        lines2_normalized = [line.replace(node2.name, 'FUNC') for line in lines2]
        
        param1 = node1.args.args[0].arg if node1.args.args else 'param'
        param2 = node2.args.args[0].arg if node2.args.args else 'param'
        
        lines1_normalized = [line.replace(param1, 'PARAM') for line in lines1_normalized]
        lines2_normalized = [line.replace(param2, 'PARAM') for line in lines2_normalized]
        
        return lines1_normalized == lines2_normalized
    
    def _has_many_conditionals(self, node: ast.FunctionDef) -> bool:
        conditionals = 0
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                conditionals += 1
        return conditionals >= 4
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        if str1 == str2:
            return 1.0
        
        len1, len2 = len(str1), len(str2)
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        
        common_chars = sum(1 for c1, c2 in zip(str1, str2) if c1 == c2)
        return common_chars / max_len
    
    def _convert_ast_to_node(self, ast_node: ast.AST) -> ASTNode:
        node_type = ast_node.__class__.__name__
        return ASTNode(type=node_type)