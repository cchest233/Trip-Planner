"""
Logging utilities for the road trip planner.

Provides consistent logging across all LangGraph nodes.
"""

from datetime import datetime
from typing import Any


class NodeLogger:
    """Logger for LangGraph nodes with colored output."""
    
    # ANSI color codes
    COLORS = {
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'reset': '\033[0m',
        'bold': '\033[1m',
    }
    
    @classmethod
    def _colorize(cls, text: str, color: str) -> str:
        """Add color to text."""
        return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['reset']}"
    
    @classmethod
    def _get_timestamp(cls) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime("%H:%M:%S")
    
    @classmethod
    def node_start(cls, node_name: str) -> None:
        """Log the start of a node."""
        print()
        print("=" * 80)
        print(cls._colorize(f"🔵 [{cls._get_timestamp()}] Starting: {node_name}", 'blue'))
        print("=" * 80)
    
    @classmethod
    def node_complete(cls, node_name: str, details: str = "") -> None:
        """Log the completion of a node."""
        print(cls._colorize(f"✅ [{cls._get_timestamp()}] Completed: {node_name}", 'green'))
        if details:
            print(cls._colorize(f"   {details}", 'green'))
        print("=" * 80)
    
    @classmethod
    def node_error(cls, node_name: str, error: Exception) -> None:
        """Log an error in a node."""
        print(cls._colorize(f"❌ [{cls._get_timestamp()}] Error in {node_name}: {error}", 'red'))
        print("=" * 80)
    
    @classmethod
    def info(cls, message: str) -> None:
        """Log an info message."""
        print(cls._colorize(f"ℹ️  {message}", 'cyan'))
    
    @classmethod
    def step(cls, step_name: str, value: Any = None) -> None:
        """Log a step within a node."""
        if value is not None:
            print(cls._colorize(f"   • {step_name}: {value}", 'yellow'))
        else:
            print(cls._colorize(f"   • {step_name}", 'yellow'))
    
    @classmethod
    def output(cls, label: str, content: str, max_length: int = 200) -> None:
        """Log output content (truncated if too long)."""
        if len(content) > max_length:
            content = content[:max_length] + "..."
        print(cls._colorize(f"   📤 {label}:", 'magenta'))
        print(f"      {content}")
    
    @classmethod
    def section(cls, title: str) -> None:
        """Log a section header."""
        print()
        print(cls._colorize(f"─── {title} ───", 'bold'))


# Create a global logger instance
logger = NodeLogger()
