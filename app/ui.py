from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from contextlib import contextmanager
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

console = Console()

# ✅ ADD THIS LINE (or make sure it exists)
SCROLL_THRESHOLD = 20 # number of lines before pager is used

def print_header():
    console.print(
        Panel.fit(
            "[bold cyan]🤖 TermiChat[/bold cyan]\n[dim]Linux Terminal AI[/dim]",
            border_style="cyan"
        )
    )

# Prompt session with history & arrow-key support
_session = PromptSession(
    history=InMemoryHistory(),
)

def user_input():
    return _session.prompt(
        "You: ",
        multiline=False
    )

def ai_response(text: str):
    md = Markdown(text)
    lines = text.count("\n") + 1

    if lines >= SCROLL_THRESHOLD:
        # use pager for long output
        with console.pager():
            console.print(md)

    else:
        # normal panel for short output
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

@contextmanager
def thinking():
    with console.status(
        "[bold magenta]AI is thinking…[/bold magenta]",
        spinner="dots"
    ):
        yield