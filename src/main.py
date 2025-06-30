#!/usr/bin/env python3
"""
Prompt Auto Refactor Tool - Main Entry Point

A tool for automatic code refactoring based on natural language prompts.
"""

import click
import sys
from pathlib import Path
from typing import Optional

# Handle different execution contexts
try:
    # When run from the project root
    from src.analyzer.code_analyzer import CodeAnalyzer
    from src.refactor.refactoring_engine import RefactoringEngine
    from src.prompt.prompt_processor import PromptProcessor
    from src.generator.code_generator import CodeGenerator, GenerationOptions
except ImportError:
    # When run from the src directory
    sys.path.insert(0, str(Path(__file__).parent))
    from analyzer.code_analyzer import CodeAnalyzer
    from refactor.refactoring_engine import RefactoringEngine
    from prompt.prompt_processor import PromptProcessor
    from generator.code_generator import CodeGenerator, GenerationOptions


class PromptAutoRefactor:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.processor = PromptProcessor()
        self.engine = RefactoringEngine()
        self.generator = CodeGenerator()
    
    def refactor_code(self, code: str, prompt: str, language: str = "python", 
                     formatting_style: str = "black", 
                     preserve_comments: bool = True) -> str:
        """
        Main refactoring workflow
        """
        try:
            # 1. Parse the prompt
            request = self.processor.parse_prompt(prompt)
            
            # 2. Convert to refactoring operation
            operation = self.processor.convert_to_operation(request)
            
            # 3. Apply refactoring
            refactored_code = self.engine.apply_refactoring(code, operation)
            
            # 4. Generate clean output
            options = GenerationOptions(
                language=language,
                formatting_style=formatting_style,
                preserve_comments=preserve_comments
            )
            final_code = self.generator.generate_code(refactored_code, options)
            
            return final_code
            
        except Exception as e:
            raise RuntimeError(f"Refactoring failed: {str(e)}")
    
    def analyze_code(self, code: str, language: str = "python"):
        """
        Analyze code and suggest refactoring opportunities
        """
        try:
            # Parse code structure
            parse_result = self.analyzer.parse_code(code, language)
            
            # Identify code smells
            smells = self.analyzer.identify_code_smells(code, language)
            
            # Generate suggestions
            suggestions = self.analyzer.generate_suggestions(code, language)
            
            return {
                "structure": parse_result,
                "code_smells": smells,
                "suggestions": suggestions
            }
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {str(e)}")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Prompt Auto Refactor Tool - Automatic code refactoring based on natural language prompts."""
    pass


@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Input file to refactor')
@click.option('--prompt', '-p', required=True, help='Refactoring prompt')
@click.option('--output', '-o', type=click.Path(), help='Output file (default: stdout)')
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--style', '-s', default='black', help='Formatting style')
@click.option('--no-comments', is_flag=True, help='Remove comments from output')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def refactor(file: Optional[str], prompt: str, output: Optional[str], 
            language: str, style: str, no_comments: bool, interactive: bool):
    """Refactor code based on a natural language prompt."""
    
    tool = PromptAutoRefactor()
    
    try:
        # Read input
        if file:
            with open(file, 'r') as f:
                code = f.read()
        else:
            if interactive:
                click.echo("Enter your code (end with Ctrl+D on Unix or Ctrl+Z on Windows):")
            code = sys.stdin.read()
        
        if not code.strip():
            click.echo("Error: No code provided", err=True)
            sys.exit(1)
        
        # Show original code analysis in interactive mode
        if interactive:
            click.echo("\n" + "="*50)
            click.echo("ORIGINAL CODE ANALYSIS")
            click.echo("="*50)
            
            analysis = tool.analyze_code(code, language)
            
            click.echo(f"Functions: {analysis['structure'].functions}")
            click.echo(f"Classes: {analysis['structure'].classes}")
            click.echo(f"Methods: {analysis['structure'].methods}")
            
            if analysis['code_smells']:
                click.echo("\nCode Smells Found:")
                for smell in analysis['code_smells']:
                    click.echo(f"  - Line {smell.line}: {smell.description}")
            
            if analysis['suggestions']:
                click.echo("\nRefactoring Suggestions:")
                for suggestion in analysis['suggestions']:
                    click.echo(f"  - {suggestion.description}")
            
            click.echo("\n" + "="*50)
            click.echo("APPLYING REFACTORING")
            click.echo("="*50)
        
        # Apply refactoring
        result = tool.refactor_code(
            code, 
            prompt, 
            language=language,
            formatting_style=style,
            preserve_comments=not no_comments
        )
        
        # Output result
        if output:
            with open(output, 'w') as f:
                f.write(result)
            click.echo(f"Refactored code written to {output}")
        else:
            if interactive:
                click.echo("\nREFACTORED CODE:")
                click.echo("-" * 30)
            click.echo(result)
        
        if interactive:
            click.echo("\n" + "="*50)
            click.echo("REFACTORING COMPLETED SUCCESSFULLY")
            click.echo("="*50)
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='File to analyze')
@click.option('--language', '-l', default='python', help='Programming language')
def analyze(file: Optional[str], language: str):
    """Analyze code and suggest refactoring opportunities."""
    
    tool = PromptAutoRefactor()
    
    try:
        # Read input
        if file:
            with open(file, 'r') as f:
                code = f.read()
        else:
            code = sys.stdin.read()
        
        if not code.strip():
            click.echo("Error: No code provided", err=True)
            sys.exit(1)
        
        # Analyze code
        analysis = tool.analyze_code(code, language)
        
        # Display results
        click.echo("CODE STRUCTURE:")
        click.echo(f"  Functions: {', '.join(analysis['structure'].functions) if analysis['structure'].functions else 'None'}")
        click.echo(f"  Classes: {', '.join(analysis['structure'].classes) if analysis['structure'].classes else 'None'}")
        if analysis['structure'].methods:
            click.echo("  Methods:")
            for class_name, methods in analysis['structure'].methods.items():
                click.echo(f"    {class_name}: {', '.join(methods)}")
        
        if analysis['code_smells']:
            click.echo("\nCODE SMELLS:")
            for smell in analysis['code_smells']:
                click.echo(f"  Line {smell.line}: {smell.type} - {smell.description}")
        else:
            click.echo("\nCODE SMELLS: None detected")
        
        if analysis['suggestions']:
            click.echo("\nREFACTORING SUGGESTIONS:")
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                click.echo(f"  {i}. {suggestion.description} (Priority: {suggestion.priority})")
        else:
            click.echo("\nREFACTORING SUGGESTIONS: No suggestions")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def interactive():
    """Start interactive refactoring session."""
    
    tool = PromptAutoRefactor()
    
    click.echo("Welcome to Prompt Auto Refactor Tool!")
    click.echo("Enter 'help' for available commands, 'quit' to exit.")
    
    while True:
        try:
            command = click.prompt("\nrefactor> ", type=str).strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                click.echo("Goodbye!")
                break
            elif command.lower() == 'help':
                click.echo("""
Available commands:
  analyze <language>  - Analyze code from stdin
  refactor <prompt>   - Refactor code with prompt
  help               - Show this help
  quit               - Exit the tool
                """)
            elif command.startswith('analyze'):
                parts = command.split(maxsplit=1)
                language = parts[1] if len(parts) > 1 else 'python'
                
                click.echo("Enter your code (end with Ctrl+D):")
                code = sys.stdin.read()
                
                analysis = tool.analyze_code(code, language)
                
                click.echo("ANALYSIS RESULTS:")
                click.echo(f"Functions: {analysis['structure'].functions}")
                click.echo(f"Classes: {analysis['structure'].classes}")
                if analysis['code_smells']:
                    click.echo("Code smells found:")
                    for smell in analysis['code_smells']:
                        click.echo(f"  - {smell.description}")
                        
            elif command.startswith('refactor'):
                prompt = command[8:].strip()  # Remove 'refactor '
                if not prompt:
                    click.echo("Please provide a refactoring prompt")
                    continue
                
                click.echo("Enter your code (end with Ctrl+D):")
                code = sys.stdin.read()
                
                result = tool.refactor_code(code, prompt)
                click.echo("REFACTORED CODE:")
                click.echo(result)
            else:
                click.echo("Unknown command. Type 'help' for available commands.")
                
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break
        except Exception as e:
            click.echo(f"Error: {str(e)}")


if __name__ == '__main__':
    cli()