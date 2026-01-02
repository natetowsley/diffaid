import typer
from rich.console import Console
from diffaid.git import get_staged_diff
from diffaid.ai.gemini import GeminiEngine

app = typer.Typer()
console = Console()

@app.command()
def check():
    diff = get_staged_diff()

    if not diff:
        console.print("[green]No staged changes detected.[/green]")
        raise typer.Exit()
    
    try:
        engine = GeminiEngine()
        result = engine.review(diff)
    except RuntimeError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]Summary:[/bold] {result.summary}\n\n---\n")

    for f in result.findings:
        color = {"error": "red", "warning": "yellow", "note": "cyan"}[f.severity]
        console.print(f"[{color}]{f.severity.upper()}[/]: {f.message}")
        if f.file:
            console.print(f"[bold]  → {f.file} {f.lines or ''}[/bold]")
        console.print()