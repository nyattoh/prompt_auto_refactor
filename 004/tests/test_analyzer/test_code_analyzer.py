import pytest
from src.analyzer.code_analyzer import CodeAnalyzer, CodeSmell


class TestCodeAnalyzer:
    def test_parse_python_file(self):
        analyzer = CodeAnalyzer()
        code = """
def calculate_sum(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
        result = analyzer.parse_code(code, "python")
        assert result is not None
        assert result.functions == ["calculate_sum"]
        assert result.classes == ["Calculator"]
        assert result.methods == {"Calculator": ["multiply"]}
    
    def test_identify_long_method(self):
        analyzer = CodeAnalyzer()
        code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            processed = item * 2
            if processed > 100:
                processed = processed / 2
                if processed % 2 == 0:
                    result.append(processed)
                else:
                    result.append(processed + 1)
            else:
                result.append(processed)
        else:
            result.append(0)
    
    final_result = []
    for r in result:
        if r > 50:
            final_result.append(r * 1.5)
        else:
            final_result.append(r)
    
    return final_result
"""
        smells = analyzer.identify_code_smells(code, "python")
        assert any(smell.type == "long_method" for smell in smells)
    
    def test_identify_duplicate_code(self):
        analyzer = CodeAnalyzer()
        code = """
def process_user_data(user):
    name = user.get('name', '')
    age = user.get('age', 0)
    email = user.get('email', '')
    
    if not name or not age or not email:
        return None
    
    return {'name': name.upper(), 'age': age, 'email': email.lower()}

def process_admin_data(admin):
    name = admin.get('name', '')
    age = admin.get('age', 0)
    email = admin.get('email', '')
    
    if not name or not age or not email:
        return None
    
    return {'name': name.upper(), 'age': age, 'email': email.lower()}
"""
        smells = analyzer.identify_code_smells(code, "python")
        assert any(smell.type == "duplicate_code" for smell in smells)
    
    def test_generate_refactoring_suggestions(self):
        analyzer = CodeAnalyzer()
        code = """
def calculate(x, y, operation):
    if operation == 'add':
        return x + y
    elif operation == 'subtract':
        return x - y
    elif operation == 'multiply':
        return x * y
    elif operation == 'divide':
        return x / y
"""
        suggestions = analyzer.generate_suggestions(code, "python")
        assert len(suggestions) > 0
        assert any("strategy pattern" in s.description.lower() or 
                  "dictionary" in s.description.lower() 
                  for s in suggestions)
    
    def test_extract_ast(self):
        analyzer = CodeAnalyzer()
        code = "x = 1 + 2"
        ast_tree = analyzer.extract_ast(code, "python")
        assert ast_tree is not None
        assert ast_tree.type == "Module"
    
    def test_invalid_code_handling(self):
        analyzer = CodeAnalyzer()
        code = "def invalid syntax here"
        with pytest.raises(SyntaxError):
            analyzer.parse_code(code, "python")
    
    def test_empty_code_handling(self):
        analyzer = CodeAnalyzer()
        result = analyzer.parse_code("", "python")
        assert result.functions == []
        assert result.classes == []
        assert result.methods == {}
    
    def test_nested_functions(self):
        analyzer = CodeAnalyzer()
        code = """
def outer_function():
    def inner_function():
        return 42
    return inner_function()
"""
        result = analyzer.parse_code(code, "python")
        assert "outer_function" in result.functions
        assert len(result.functions) >= 1