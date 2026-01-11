import typer
import json
from diffaid import __version__
from rich.console import Console
from diffaid.git import get_staged_diff
from diffaid.ai.gemini import GeminiEngine

app = typer.Typer(
    help="AI-assisted git diff review CLI",
    add_completion=False
)
console = Console()

def version_callback(value: bool):
    if value:
        console.print(f"diffaid version {__version__}")
        raise typer.Exit()

@app.command()
def check(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output raw JSON instead of formatted text"
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Treat warnings as errors (exit code 1)"
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Perform detailed line-by-line review with all suggestions"
    ),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """
    Review staged git changes with AI.
    
    Analyzes your staged diff and reports errors, warnings, and notes
    about potential issues before you commit.
    
    Example Usage:
    
      # Quick overview (default)
      $ diffaid

      # Analysis of all changes (with suggestions)
      $ diffaid --detailed

      # JSON output
      $ diffaid --json

      # Strict mode (warnings cause failures)
      $ diffaid --strict
    
    Exit Codes:
      0 - No errors found
      1 - Errors found, or warnings in strict mode
      2 - Tool error (git failure, API issues)
    """

    # Retrieve staged git changes
    try:
        diff = get_staged_diff()
    except RuntimeError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(2)

    if not diff:
        if json_output:
            print(json.dumps({"message": "No staged changes detected."}))
        else:
            console.print("[green]No staged changes detected.[/green]")
        raise typer.Exit(0)
    
    # Set engine and retrieve AI response
    try:
        engine = GeminiEngine()
        result = engine.review(diff, detailed=detailed)
    except RuntimeError as error:
        if json_output:
            print(json.dumps({"error": str(error)}))
        else:
            console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(2)
    
    has_errors = any(f.severity == "error" for f in result.findings)
    has_warnings = any(f.severity == "warning" for f in result.findings)
    should_fail = has_errors or (strict and has_warnings)
    
    # JSON output mode
    if json_output:
        # Convert Pydantic model to dict, then to JSON
        output = result.model_dump()
        
        # Strict mode condition
        if strict:
            output["strict_mode"] = True
            output["exit_code"] = 1 if should_fail else 0
        
        print(json.dumps(output, indent=2))
        raise typer.Exit(1 if should_fail else 0)

    # Diff summary
    console.print(f"\n[bold]Summary:[/bold] {result.summary}\n")
    console.print("\n---\n")

    # Finding contents
    if not result.findings:
        console.print("[green]No issues found![/green]\n")
    else:
        for f in result.findings:
            if f.severity == "error":
                has_errors = True
            elif f.severity == "warning":
                has_warnings = True

            color = {"error": "red", "warning": "yellow", "note": "cyan"}[f.severity]
            console.print(f"[{color}]{f.severity.upper()}[/]: {f.message}")
            if f.file:
                console.print(f"[bold]  → {f.file}[/bold]")
            console.print()

    # Count findings
    counts = {"error": 0, "warning": 0, "note": 0}
    for f in result.findings:
        counts[f.severity] += 1
    
    console.print("---\n")
    console.print(f"[bold]Found:[/bold] {counts['error']} error{'s' if counts['error'] != 1 else ''}, "
                  f"{counts['warning']} warning{'s' if counts['warning'] != 1 else ''}, "
                  f"{counts['note']} note{'s' if counts['note'] != 1 else ''}")
    
    if strict and has_warnings:
        console.print("\n[yellow]Strict Mode: Treating warnings as errors[/yellow]")

    if should_fail:
        raise typer.Exit(1)
    raise typer.Exit(0)
