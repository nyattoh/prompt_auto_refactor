# Prompt Auto Refactor Tool

**👉 日本語版 README は[こちら](README_ja.md)です。**

A tool for automatic code refactoring based on natural language prompts, implemented using Test-Driven Development (TDD).

## Features

- **Code Analysis**: Parse code structure and identify refactoring opportunities
- **Refactoring Engine**: Apply various refactoring operations
- **Prompt Processing**: Process natural language prompts for refactoring
- **Code Generation**: Generate clean, readable code with proper formatting

## Supported Refactoring Operations

- Extract method/function
- Rename variables/functions
- Inline variable/function
- Move method/class
- Remove dead code

## Supported Languages

- Python (primary)
- JavaScript (basic support)
- TypeScript (basic support)

## Installation

```bash
# Clone the repository
cd 004

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

#### Refactor code with a prompt:
```bash
# From file
refactor -f mycode.py -p "Rename function 'calc' to 'calculate'"

# From stdin
echo "def calc(x, y): return x + y" | refactor -p "Rename function 'calc' to 'calculate'"

# Interactive mode
refactor -i -p "Extract the validation logic"
```

#### Analyze code:
```bash
# Analyze file
refactor analyze -f mycode.py

# Analyze from stdin
cat mycode.py | refactor analyze
```

#### Interactive session:
```bash
refactor interactive
```

### Python API

```python
from src.main import PromptAutoRefactor

tool = PromptAutoRefactor()

# Refactor code
code = """
def calc(x, y):
    return x + y
"""

result = tool.refactor_code(code, "Rename function 'calc' to 'calculate'")
print(result)

# Analyze code
analysis = tool.analyze_code(code)
print(f"Functions: {analysis['structure'].functions}")
print(f"Suggestions: {[s.description for s in analysis['suggestions']]}")
```

## Example Prompts

- "Rename function 'calc' to 'calculate_sum'"
- "Extract the validation logic from lines 5-10 into a new method called validate_data"
- "Inline the variable 'temp'"
- "Move method 'add' from Calculator class to MathUtils class"
- "Remove unused functions: helper1, helper2"

## Project Structure

```
004/
├── src/
│   ├── analyzer/          # Code analysis module
│   ├── refactor/          # Refactoring engine
│   ├── prompt/            # Prompt processing
│   ├── generator/         # Code generation
│   └── main.py           # CLI interface
├── tests/
│   ├── test_analyzer/
│   ├── test_refactor/
│   ├── test_prompt/
│   ├── test_generator/
│   └── test_integration.py
├── requirements.txt
├── pytest.ini
├── setup.py
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test module
pytest tests/test_analyzer/

# Run integration tests
pytest tests/test_integration.py
```

### Test Coverage

The project maintains high test coverage (>90%) across all modules:

- Code Analyzer: 90%+ coverage
- Refactoring Engine: 94%+ coverage  
- Prompt Processor: 85%+ coverage
- Code Generator: 85%+ coverage
- Integration tests: Complete workflow testing

### TDD Implementation

This project was implemented using Test-Driven Development:

1. **Red**: Write failing tests first
2. **Green**: Implement minimal code to pass tests
3. **Refactor**: Improve code while keeping tests green

Each module follows this pattern:
1. Write comprehensive test cases
2. Implement functionality to pass tests
3. Refactor and optimize implementation

## Architecture

The tool follows a modular architecture:

1. **Analyzer**: Parses code and identifies refactoring opportunities
2. **Prompt Processor**: Interprets natural language prompts
3. **Refactoring Engine**: Applies transformations to code
4. **Generator**: Produces clean, formatted output

## Contributing

1. Follow TDD principles - write tests first
2. Maintain test coverage above 90%
3. Use clear, descriptive commit messages
4. Add documentation for new features

## License

MIT License - see LICENSE file for details.