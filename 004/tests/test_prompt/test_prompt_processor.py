import pytest
from src.prompt.prompt_processor import PromptProcessor, RefactoringRequest
from src.refactor.refactoring_engine import RefactoringOperation


class TestPromptProcessor:
    def test_parse_extract_method_prompt(self):
        processor = PromptProcessor()
        prompt = "Extract the calculation logic from lines 5-10 into a new method called calculate_discount"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "extract_method"
        assert result.method_name == "calculate_discount"
        assert result.start_line == 5
        assert result.end_line == 10
    
    def test_parse_rename_function_prompt(self):
        processor = PromptProcessor()
        prompt = "Rename function 'calc' to 'calculate_sum'"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "rename_function"
        assert result.old_name == "calc"
        assert result.new_name == "calculate_sum"
    
    def test_parse_rename_variable_prompt(self):
        processor = PromptProcessor()
        prompt = "Rename variable 'x' to 'input_value'"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "rename_variable"
        assert result.old_name == "x"
        assert result.new_name == "input_value"
    
    def test_parse_inline_variable_prompt(self):
        processor = PromptProcessor()
        prompt = "Inline the variable 'temp'"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "inline_variable"
        assert result.variable_name == "temp"
    
    def test_parse_inline_function_prompt(self):
        processor = PromptProcessor()
        prompt = "Inline the function 'simple_add'"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "inline_function"
        assert result.function_name == "simple_add"
    
    def test_parse_move_method_prompt(self):
        processor = PromptProcessor()
        prompt = "Move method 'add' from Calculator class to MathUtils class"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "move_method"
        assert result.method_name == "add"
        assert result.source_class == "Calculator"
        assert result.target_class == "MathUtils"
    
    def test_parse_remove_dead_code_prompt(self):
        processor = PromptProcessor()
        prompt = "Remove unused functions: unused_function, old_helper"
        
        result = processor.parse_prompt(prompt)
        
        assert result.operation_type == "remove_dead_code"
        assert "unused_function" in result.dead_functions
        assert "old_helper" in result.dead_functions
    
    def test_validate_prompt_success(self):
        processor = PromptProcessor()
        prompt = "Rename function 'calc' to 'calculate_sum'"
        
        assert processor.validate_prompt(prompt) == True
    
    def test_validate_prompt_failure(self):
        processor = PromptProcessor()
        invalid_prompt = "Do something random with code"
        
        assert processor.validate_prompt(invalid_prompt) == False
    
    def test_convert_to_operation(self):
        processor = PromptProcessor()
        request = RefactoringRequest(
            operation_type="rename_function",
            old_name="calc",
            new_name="calculate_sum"
        )
        
        operation = processor.convert_to_operation(request)
        
        assert isinstance(operation, RefactoringOperation)
        assert operation.type == "rename_function"
        assert operation.old_name == "calc"
        assert operation.new_name == "calculate_sum"
    
    def test_extract_intent_from_prompt(self):
        processor = PromptProcessor()
        prompt = "This function is too long, please extract some methods"
        
        intent = processor.extract_intent(prompt)
        
        assert intent == "extract_method"
    
    def test_suggest_refactoring_from_prompt(self):
        processor = PromptProcessor()
        prompt = "This code has duplicate logic that should be removed"
        
        suggestions = processor.suggest_refactoring(prompt)
        
        assert len(suggestions) > 0
        assert any("extract" in s.lower() or "duplicate" in s.lower() for s in suggestions)
    
    def test_natural_language_understanding(self):
        processor = PromptProcessor()
        
        prompts = [
            "Please extract the validation logic",
            "Can you rename this function to something more descriptive?",
            "This variable name is unclear, let's change it",
            "Remove this unused method"
        ]
        
        for prompt in prompts:
            result = processor.parse_prompt(prompt)
            assert result is not None
            assert result.operation_type in ["extract_method", "rename_function", "rename_variable", "remove_dead_code"]
    
    def test_ambiguous_prompt_handling(self):
        processor = PromptProcessor()
        ambiguous_prompt = "Make this code better"
        
        with pytest.raises(ValueError, match="Ambiguous prompt"):
            processor.parse_prompt(ambiguous_prompt)
    
    def test_unsupported_operation_prompt(self):
        processor = PromptProcessor()
        unsupported_prompt = "Convert this to a different programming language"
        
        with pytest.raises(NotImplementedError):
            processor.parse_prompt(unsupported_prompt)