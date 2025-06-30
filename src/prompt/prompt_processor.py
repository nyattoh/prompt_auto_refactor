import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
try:
    from src.refactor.refactoring_engine import RefactoringOperation
except ImportError:
    from refactor.refactoring_engine import RefactoringOperation


@dataclass
class RefactoringRequest:
    operation_type: str
    method_name: str = None
    start_line: int = None
    end_line: int = None
    old_name: str = None
    new_name: str = None
    variable_name: str = None
    function_name: str = None
    source_class: str = None
    target_class: str = None
    dead_functions: List[str] = None


class PromptProcessor:
    def __init__(self):
        self.operation_patterns = {
            'extract_method': [
                r'extract.*(?:from\s+)?lines?\s+(\d+)[-\s]*(?:to\s+)?(\d+).*(?:method|function)\s+(?:called\s+)?["\']?(\w+)["\']?',
                r'extract.*(?:method|function)\s+(?:called\s+)?["\']?(\w+)["\']?.*(?:from\s+)?lines?\s+(\d+)[-\s]*(?:to\s+)?(\d+)',
                r'extract.*validation\s+logic',
                r'extract.*calculation\s+logic'
            ],
            'rename_function': [
                r'rename\s+function\s+["\']?(\w+)["\']?\s+to\s+["\']?(\w+)["\']?',
                r'rename.*function.*["\']?(\w+)["\']?.*["\']?(\w+)["\']?',
                r'rename.*function.*more\s+descriptive'
            ],
            'rename_variable': [
                r'rename\s+variable\s+["\']?(\w+)["\']?\s+to\s+["\']?(\w+)["\']?',
                r'variable\s+name.*unclear.*change',
                r'rename.*variable'
            ],
            'inline_variable': [
                r'inline.*variable\s+["\']?(\w+)["\']?'
            ],
            'inline_function': [
                r'inline.*function\s+["\']?(\w+)["\']?'
            ],
            'move_method': [
                r'move\s+method\s+["\']?(\w+)["\']?\s+from\s+(\w+)\s+(?:class\s+)?to\s+(\w+)\s+(?:class)?'
            ],
            'remove_dead_code': [
                r'remove\s+unused\s+(?:functions?|methods?):\s*(.*)',
                r'remove.*unused\s+method'
            ]
        }
        
        self.intent_keywords = {
            'extract_method': ['extract', 'separate', 'split', 'factor out', 'pull out'],
            'rename_function': ['rename function', 'change function name', 'better name'],
            'rename_variable': ['rename variable', 'change variable', 'unclear', 'descriptive'],
            'inline_variable': ['inline variable', 'substitute'],
            'inline_function': ['inline function', 'expand'],
            'move_method': ['move method', 'relocate'],
            'remove_dead_code': ['remove unused', 'dead code', 'clean up']
        }
    
    def parse_prompt(self, prompt: str) -> RefactoringRequest:
        prompt_lower = prompt.lower()
        
        # Check for ambiguous prompts
        if any(phrase in prompt_lower for phrase in ['make', 'better', 'improve', 'optimize']) and not any(op in prompt_lower for op in ['extract', 'rename', 'inline', 'move', 'remove']):
            raise ValueError("Ambiguous prompt: Please specify the type of refactoring you want")
        
        # Check for unsupported operations
        if any(phrase in prompt_lower for phrase in ['convert', 'translate', 'different language']):
            raise NotImplementedError("Language conversion is not supported")
        
        for operation_type, patterns in self.operation_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    return self._create_request_from_match(operation_type, match, prompt_lower, prompt)
        
        # Fallback to intent extraction
        intent = self.extract_intent(prompt)
        if intent:
            return RefactoringRequest(operation_type=intent)
        
        raise ValueError("Could not parse the refactoring request from the prompt")
    
    def _create_request_from_match(self, operation_type: str, match, prompt_lower: str, original_prompt: str) -> RefactoringRequest:
        groups = match.groups()
        
        if operation_type == "extract_method":
            if len(groups) >= 3 and groups[2]:  # method name in third group
                return RefactoringRequest(
                    operation_type=operation_type,
                    method_name=groups[2],
                    start_line=int(groups[0]) if groups[0] else None,
                    end_line=int(groups[1]) if groups[1] else None
                )
            elif len(groups) >= 1 and groups[0]:  # method name in first group
                return RefactoringRequest(
                    operation_type=operation_type,
                    method_name=groups[0],
                    start_line=int(groups[1]) if len(groups) > 1 and groups[1] else None,
                    end_line=int(groups[2]) if len(groups) > 2 and groups[2] else None
                )
            else:
                # Default method name for validation/calculation logic
                method_name = "extracted_method"
                if "validation" in prompt_lower:
                    method_name = "validate"
                elif "calculation" in prompt_lower:
                    method_name = "calculate"
                return RefactoringRequest(operation_type=operation_type, method_name=method_name)
        
        elif operation_type == "rename_function":
            if len(groups) >= 2:
                return RefactoringRequest(
                    operation_type=operation_type,
                    old_name=groups[0],
                    new_name=groups[1]
                )
            else:
                return RefactoringRequest(operation_type=operation_type)
        
        elif operation_type == "rename_variable":
            if len(groups) >= 2:
                return RefactoringRequest(
                    operation_type=operation_type,
                    old_name=groups[0],
                    new_name=groups[1]
                )
            else:
                return RefactoringRequest(operation_type=operation_type)
        
        elif operation_type == "inline_variable":
            return RefactoringRequest(
                operation_type=operation_type,
                variable_name=groups[0] if groups else None
            )
        
        elif operation_type == "inline_function":
            return RefactoringRequest(
                operation_type=operation_type,
                function_name=groups[0] if groups else None
            )
        
        elif operation_type == "move_method":
            if len(groups) >= 3:
                # Extract original case from the original prompt
                source_match = re.search(r'from\s+(\w+)', original_prompt, re.IGNORECASE)
                target_match = re.search(r'to\s+(\w+)', original_prompt, re.IGNORECASE)
                
                source_class = source_match.group(1) if source_match else groups[1].title()
                target_class = target_match.group(1) if target_match else groups[2].title()
                
                return RefactoringRequest(
                    operation_type=operation_type,
                    method_name=groups[0],
                    source_class=source_class,
                    target_class=target_class
                )
        
        elif operation_type == "remove_dead_code":
            if groups and groups[0]:
                functions = [f.strip() for f in groups[0].split(',')]
                return RefactoringRequest(
                    operation_type=operation_type,
                    dead_functions=functions
                )
            else:
                return RefactoringRequest(operation_type=operation_type)
        
        return RefactoringRequest(operation_type=operation_type)
    
    def validate_prompt(self, prompt: str) -> bool:
        try:
            self.parse_prompt(prompt)
            return True
        except (ValueError, NotImplementedError):
            return False
    
    def convert_to_operation(self, request: RefactoringRequest) -> RefactoringOperation:
        operation_args = {
            'type': request.operation_type
        }
        
        if request.method_name:
            operation_args['new_method_name'] = request.method_name
        if request.start_line:
            operation_args['start_line'] = request.start_line
        if request.end_line:
            operation_args['end_line'] = request.end_line
        if request.old_name:
            operation_args['old_name'] = request.old_name
        if request.new_name:
            operation_args['new_name'] = request.new_name
        if request.variable_name:
            operation_args['variable_name'] = request.variable_name
        if request.function_name:
            operation_args['function_name'] = request.function_name
        if request.source_class:
            operation_args['source_class'] = request.source_class
        if request.target_class:
            operation_args['target_class'] = request.target_class
        if request.dead_functions:
            operation_args['dead_functions'] = request.dead_functions
        
        return RefactoringOperation(**operation_args)
    
    def extract_intent(self, prompt: str) -> Optional[str]:
        prompt_lower = prompt.lower()
        
        for operation_type, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return operation_type
        
        return None
    
    def suggest_refactoring(self, prompt: str) -> List[str]:
        suggestions = []
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['duplicate', 'repeated', 'similar']):
            suggestions.append("Extract common functionality into a shared method")
            suggestions.append("Remove duplicate code")
        
        if any(word in prompt_lower for word in ['long', 'complex', 'too many']):
            suggestions.append("Extract methods to reduce complexity")
            suggestions.append("Break down into smaller functions")
        
        if any(word in prompt_lower for word in ['unclear', 'confusing', 'hard to understand']):
            suggestions.append("Rename variables and functions for clarity")
            suggestions.append("Add descriptive method names")
        
        if any(word in prompt_lower for word in ['unused', 'dead', 'not used']):
            suggestions.append("Remove unused code")
        
        return suggestions if suggestions else ["Consider extracting methods or renaming for clarity"]