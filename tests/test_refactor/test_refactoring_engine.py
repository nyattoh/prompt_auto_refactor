import pytest
from src.refactor.refactoring_engine import RefactoringEngine, RefactoringOperation


class TestRefactoringEngine:
    def test_extract_method(self):
        engine = RefactoringEngine()
        code = """
def calculate_total(items):
    total = 0
    for item in items:
        if item.price > 0:
            discount = item.price * 0.1
            discounted_price = item.price - discount
            total += discounted_price
        else:
            total += 0
    
    tax = total * 0.08
    final_total = total + tax
    return final_total
"""
        operation = RefactoringOperation(
            type="extract_method",
            target="calculate_discount",
            start_line=5,
            end_line=7,
            new_method_name="calculate_discounted_price"
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "def calculate_discounted_price" in result
        assert "discounted_price = calculate_discounted_price(item.price)" in result
    
    def test_rename_variable(self):
        engine = RefactoringEngine()
        code = """
def process_data(x):
    y = x * 2
    z = y + 1
    return z
"""
        operation = RefactoringOperation(
            type="rename_variable",
            old_name="x",
            new_name="input_value"
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "def process_data(input_value):" in result
        assert "y = input_value * 2" in result
        assert "x" not in result.replace("input_value", "")
    
    def test_rename_function(self):
        engine = RefactoringEngine()
        code = """
def calc(a, b):
    return a + b

def main():
    result = calc(5, 3)
    return result
"""
        operation = RefactoringOperation(
            type="rename_function",
            old_name="calc",
            new_name="calculate_sum"
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "def calculate_sum(a, b):" in result
        assert "result = calculate_sum(5, 3)" in result
    
    def test_inline_variable(self):
        engine = RefactoringEngine()
        code = """
def calculate():
    temp = 5 * 3
    result = temp + 10
    return result
"""
        operation = RefactoringOperation(
            type="inline_variable",
            variable_name="temp"
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "result = 5 * 3 + 10" in result
        assert "temp = 5 * 3" not in result
    
    def test_inline_function(self):
        engine = RefactoringEngine()
        code = """
def simple_add(a, b):
    return a + b

def calculate():
    x = simple_add(5, 3)
    return x * 2
"""
        operation = RefactoringOperation(
            type="inline_function",
            function_name="simple_add"
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "x = 5 + 3" in result
        assert "def simple_add" not in result
    
    def test_move_method(self):
        engine = RefactoringEngine()
        code = """
class Calculator:
    def add(self, a, b):
        return a + b

class MathUtils:
    pass
"""
        operation = RefactoringOperation(
            type="move_method",
            method_name="add",
            source_class="Calculator",
            target_class="MathUtils"
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "class MathUtils:" in result
        assert "    def add(self, a, b):" in result
        lines = result.split('\n')
        math_utils_start = next(i for i, line in enumerate(lines) if "class MathUtils:" in line)
        calculator_start = next(i for i, line in enumerate(lines) if "class Calculator:" in line)
        assert any("def add" in line for line in lines[math_utils_start:])
    
    def test_remove_dead_code(self):
        engine = RefactoringEngine()
        code = """
def active_function():
    return "active"

def unused_function():
    return "unused"

def main():
    return active_function()
"""
        operation = RefactoringOperation(
            type="remove_dead_code",
            dead_functions=["unused_function"]
        )
        
        result = engine.apply_refactoring(code, operation)
        assert "def unused_function" not in result
        assert "def active_function" in result
        assert "def main" in result
    
    def test_validate_refactoring(self):
        engine = RefactoringEngine()
        code = "def test(): return 42"
        
        valid_operation = RefactoringOperation(
            type="rename_function",
            old_name="test",
            new_name="test_function"
        )
        
        invalid_operation = RefactoringOperation(
            type="rename_function",
            old_name="nonexistent",
            new_name="new_name"
        )
        
        assert engine.validate_refactoring(code, valid_operation) == True
        assert engine.validate_refactoring(code, invalid_operation) == False
    
    def test_preserve_semantics(self):
        engine = RefactoringEngine()
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        operation = RefactoringOperation(
            type="rename_variable",
            old_name="n",
            new_name="number"
        )
        
        result = engine.apply_refactoring(code, operation)
        
        assert engine.preserve_semantics(code, result) == True
    
    def test_unsupported_operation(self):
        engine = RefactoringEngine()
        code = "def test(): pass"
        
        operation = RefactoringOperation(
            type="unsupported_operation"
        )
        
        with pytest.raises(NotImplementedError):
            engine.apply_refactoring(code, operation)