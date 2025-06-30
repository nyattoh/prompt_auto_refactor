import pytest
from src.generator.code_generator import CodeGenerator, GenerationOptions


class TestCodeGenerator:
    def test_preserve_formatting_indentation(self):
        generator = CodeGenerator()
        original_code = """
def calculate():
    x = 1
    if x > 0:
        return x * 2
    else:
        return 0
"""
        refactored_code = """
def calculate():
    x = 1
    if x > 0:
        result = x * 2
        return result
    else:
        return 0
"""
        
        result = generator.preserve_formatting(original_code, refactored_code)
        lines = result.split('\n')
        assert '    x = 1' in result  # 4-space indentation preserved
        assert '        result = x * 2' in result  # 8-space indentation preserved
    
    def test_preserve_semantic_equivalence(self):
        generator = CodeGenerator()
        original_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        refactored_code = """
def fibonacci(number):
    if number <= 1:
        return number
    return fibonacci(number-1) + fibonacci(number-2)
"""
        
        assert generator.preserve_semantic_equivalence(original_code, refactored_code) == True
    
    def test_semantic_equivalence_violation(self):
        generator = CodeGenerator()
        original_code = """
def add(a, b):
    return a + b
"""
        refactored_code = """
def add(a, b):
    return a * b
"""
        
        assert generator.preserve_semantic_equivalence(original_code, refactored_code) == False
    
    def test_generate_clean_code(self):
        generator = CodeGenerator()
        messy_code = """
def   calculate( x,y ):
    z=x+y
    if(z>10):
        return   z*2
    else   :
        return z
"""
        
        result = generator.generate_clean_code(messy_code)
        
        assert 'def calculate(x, y):' in result
        assert 'z = x + y' in result
        assert 'if z > 10:' in result
        assert 'return z * 2' in result
    
    def test_support_python_language(self):
        generator = CodeGenerator()
        code = """
def test():
    return 42
"""
        options = GenerationOptions(language="python", preserve_comments=True)
        
        result = generator.generate_code(code, options)
        assert result is not None
        assert 'def test():' in result
    
    def test_support_javascript_language(self):
        generator = CodeGenerator()
        code = """
function test() {
    return 42;
}
"""
        options = GenerationOptions(language="javascript", preserve_comments=True)
        
        result = generator.generate_code(code, options)
        assert result is not None
        assert 'function test()' in result
    
    def test_preserve_comments(self):
        generator = CodeGenerator()
        code = """
# This is a helper function
def helper():
    # Calculate the result
    return 42
"""
        options = GenerationOptions(language="python", preserve_comments=True)
        
        result = generator.generate_code(code, options)
        assert '# This is a helper function' in result
        assert '# Calculate the result' in result
    
    def test_remove_comments(self):
        generator = CodeGenerator()
        code = """
# This is a helper function
def helper():
    # Calculate the result
    return 42
"""
        options = GenerationOptions(language="python", preserve_comments=False)
        
        result = generator.generate_code(code, options)
        assert '# This is a helper function' not in result
        assert '# Calculate the result' not in result
        assert 'def helper():' in result
    
    def test_format_with_black_style(self):
        generator = CodeGenerator()
        code = """
def calculate(x,y,z):
    result=x+y*z
    if result>100:
        return result/2
    return result
"""
        options = GenerationOptions(language="python", formatting_style="black")
        
        result = generator.generate_code(code, options)
        assert 'def calculate(x, y, z):' in result
        assert 'result = x + y * z' in result
        assert 'if result > 100:' in result
    
    def test_format_with_pep8_style(self):
        generator = CodeGenerator()
        code = """
def calculate(x,y,z):
    result=x+y*z
    return result
"""
        options = GenerationOptions(language="python", formatting_style="pep8")
        
        result = generator.generate_code(code, options)
        assert 'def calculate(x, y, z):' in result
        assert 'result = x + y * z' in result
    
    def test_validate_generated_code(self):
        generator = CodeGenerator()
        valid_code = """
def test():
    return 42
"""
        invalid_code = """
def test()
    return 42
"""
        
        assert generator.validate_code(valid_code, "python") == True
        assert generator.validate_code(invalid_code, "python") == False
    
    def test_optimize_imports(self):
        generator = CodeGenerator()
        code = """
import os
import sys
import json
import ast

def test():
    return ast.parse("x = 1")
"""
        options = GenerationOptions(language="python", optimize_imports=True)
        
        result = generator.generate_code(code, options)
        assert 'import ast' in result
        # Should remove unused imports
        assert 'import os' not in result or 'import sys' not in result or 'import json' not in result
    
    def test_add_type_hints(self):
        generator = CodeGenerator()
        code = """
def add(a, b):
    return a + b
"""
        options = GenerationOptions(language="python", add_type_hints=True)
        
        result = generator.generate_code(code, options)
        # Should add basic type hints
        assert '->' in result or ':' in result
    
    def test_unsupported_language(self):
        generator = CodeGenerator()
        code = "some code"
        options = GenerationOptions(language="cobol")
        
        with pytest.raises(NotImplementedError):
            generator.generate_code(code, options)
    
    def test_generation_with_multiple_options(self):
        generator = CodeGenerator()
        code = """
import os
import ast
# Helper function
def process(data):
    # Process the data
    result=ast.parse(data)
    return result
"""
        options = GenerationOptions(
            language="python",
            preserve_comments=True,
            formatting_style="black",
            optimize_imports=True
        )
        
        result = generator.generate_code(code, options)
        assert '# Helper function' in result
        assert 'def process(data):' in result
        assert 'result = ast.parse(data)' in result