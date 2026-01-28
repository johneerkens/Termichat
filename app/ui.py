from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

console = Console()

def print_header():
    console.print(
        Panel.fit(
            "[bold cyan]🤖 TermiChat[/bold cyan]\n[dim]Linux Terminal AI[/dim]",
            border_style="cyan"
        )
    )

def user_input():
    return Prompt.ask("[bold green]You[/bold green]")

def ai_response(text: str):
    md = Markdown(text)
    console.print(
        Panel(
            md,
            title="[bold magenta]AI[/bold magenta]",
            border_style="magenta"
        )
    )

def info(message: str):
    console.print(f"[dim]{message}[/dim]")

def error(message: str):
    console.print(f"[bold red]❌ {message}[/bold red]")

from rich.panel import Panel

def show_help():
    help_text = (
        "[bold]/help[/bold]  Show this help message\n"
        "[bold]/clear[/bold] Clear the conversation history\n"
        "[bold]exit[/bold]   Exit Termichat\n"
    )

    console.print(
        Panel(
            help_text,
            title="[bold cyan]Available Commands[/bold cyan]",
            border_style="cyan"
        )
    )