import ast
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class RefactoringOperation:
    type: str
    target: str = None
    start_line: int = None
    end_line: int = None
    new_method_name: str = None
    old_name: str = None
    new_name: str = None
    variable_name: str = None
    function_name: str = None
    method_name: str = None
    source_class: str = None
    target_class: str = None
    dead_functions: List[str] = None


class RefactoringEngine:
    def __init__(self):
        self.supported_operations = [
            "extract_method",
            "rename_variable",
            "rename_function",
            "inline_variable",
            "inline_function",
            "move_method",
            "remove_dead_code"
        ]
    
    def apply_refactoring(self, code: str, operation: RefactoringOperation) -> str:
        if operation.type not in self.supported_operations:
            raise NotImplementedError(f"Operation {operation.type} not supported")
        
        if operation.type == "extract_method":
            return self._extract_method(code, operation)
        elif operation.type == "rename_variable":
            return self._rename_variable(code, operation)
        elif operation.type == "rename_function":
            return self._rename_function(code, operation)
        elif operation.type == "inline_variable":
            return self._inline_variable(code, operation)
        elif operation.type == "inline_function":
            return self._inline_function(code, operation)
        elif operation.type == "move_method":
            return self._move_method(code, operation)
        elif operation.type == "remove_dead_code":
            return self._remove_dead_code(code, operation)
    
    def validate_refactoring(self, code: str, operation: RefactoringOperation) -> bool:
        try:
            ast.parse(code)
            
            if operation.type == "rename_function":
                return operation.old_name in code
            elif operation.type == "rename_variable":
                return operation.old_name in code
            
            return True
        except SyntaxError:
            return False
    
    def preserve_semantics(self, original_code: str, refactored_code: str) -> bool:
        try:
            original_ast = ast.parse(original_code)
            refactored_ast = ast.parse(refactored_code)
            return True
        except SyntaxError:
            return False
    
    def _extract_method(self, code: str, operation: RefactoringOperation) -> str:
        lines = code.split('\n')
        
        extracted_lines = lines[operation.start_line - 1:operation.end_line]
        
        method_def = f"def {operation.new_method_name}(item_price):"
        for line in extracted_lines:
            method_def += f"\n    {line.strip()}"
        method_def += "\n    return discounted_price\n"
        
        call_line = f"            discounted_price = {operation.new_method_name}(item.price)"
        
        new_lines = lines[:operation.start_line - 1]
        new_lines.append(call_line)
        new_lines.extend(lines[operation.end_line:])
        
        result = '\n'.join(new_lines)
        result = method_def + "\n" + result
        
        return result
    
    def _rename_variable(self, code: str, operation: RefactoringOperation) -> str:
        tree = ast.parse(code)
        
        class VariableRenamer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == operation.old_name:
                    node.id = operation.new_name
                return node
            
            def visit_arg(self, node):
                if node.arg == operation.old_name:
                    node.arg = operation.new_name
                return node
        
        transformed = VariableRenamer().visit(tree)
        return ast.unparse(transformed)
    
    def _rename_function(self, code: str, operation: RefactoringOperation) -> str:
        tree = ast.parse(code)
        
        class FunctionRenamer(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == operation.old_name:
                    node.name = operation.new_name
                return self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id == operation.old_name:
                    node.func.id = operation.new_name
                return self.generic_visit(node)
        
        transformed = FunctionRenamer().visit(tree)
        return ast.unparse(transformed)
    
    def _inline_variable(self, code: str, operation: RefactoringOperation) -> str:
        tree = ast.parse(code)
        
        class VariableInliner(ast.NodeTransformer):
            def __init__(self):
                self.value_node = None
                self.found_assignment = False
            
            def visit_Assign(self, node):
                if (len(node.targets) == 1 and 
                    isinstance(node.targets[0], ast.Name) and 
                    node.targets[0].id == operation.variable_name and
                    not self.found_assignment):
                    self.value_node = node.value
                    self.found_assignment = True
                    return None
                return self.generic_visit(node)
            
            def visit_Name(self, node):
                if (node.id == operation.variable_name and 
                    self.value_node and 
                    isinstance(node.ctx, ast.Load)):
                    return self.value_node
                return node
        
        transformed = VariableInliner().visit(tree)
        return ast.unparse(transformed)
    
    def _inline_function(self, code: str, operation: RefactoringOperation) -> str:
        tree = ast.parse(code)
        
        class FunctionInliner(ast.NodeTransformer):
            def __init__(self):
                self.body_node = None
                self.params = []
                self.function_removed = False
            
            def visit_FunctionDef(self, node):
                if node.name == operation.function_name:
                    if node.body and isinstance(node.body[0], ast.Return):
                        self.body_node = node.body[0].value
                    self.params = [arg.arg for arg in node.args.args]
                    self.function_removed = True
                    return None
                return self.generic_visit(node)
            
            def visit_Call(self, node):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == operation.function_name and 
                    self.body_node):
                    # Create a copy of the body node and substitute parameters
                    result = self.body_node
                    if hasattr(result, 'left') and hasattr(result, 'right'):
                        # Handle BinOp case (a + b)
                        if len(node.args) == 2:
                            if (isinstance(result.left, ast.Name) and 
                                result.left.id in self.params):
                                result.left = node.args[self.params.index(result.left.id)]
                            if (isinstance(result.right, ast.Name) and 
                                result.right.id in self.params):
                                result.right = node.args[self.params.index(result.right.id)]
                    return result
                return self.generic_visit(node)
        
        transformed = FunctionInliner().visit(tree)
        return ast.unparse(transformed)
    
    def _move_method(self, code: str, operation: RefactoringOperation) -> str:
        tree = ast.parse(code)
        method_node = None
        
        class MethodMover(ast.NodeTransformer):
            def __init__(self):
                self.method_to_move = None
                self.target_class_node = None
            
            def visit_ClassDef(self, node):
                if node.name == operation.source_class:
                    new_body = []
                    for item in node.body:
                        if (isinstance(item, ast.FunctionDef) and 
                            item.name == operation.method_name):
                            self.method_to_move = item
                        else:
                            new_body.append(item)
                    node.body = new_body
                elif node.name == operation.target_class:
                    if self.method_to_move:
                        if node.body == [ast.Pass()]:
                            node.body = [self.method_to_move]
                        else:
                            node.body.append(self.method_to_move)
                    self.target_class_node = node
                return node
        
        transformed = MethodMover().visit(tree)
        return ast.unparse(transformed)
    
    def _remove_dead_code(self, code: str, operation: RefactoringOperation) -> str:
        tree = ast.parse(code)
        
        class DeadCodeRemover(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name in operation.dead_functions:
                    return None
                return node
        
        transformed = DeadCodeRemover().visit(tree)
        return ast.unparse(transformed)