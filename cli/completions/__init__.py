"""
LastAgent Shell Completions Package

Shell completion generation for bash, zsh, and fish.
"""

from cli.completions.generate import (
    generate_completion_script,
    install_completion,
    get_completion_path,
)

__all__ = [
    "generate_completion_script",
    "install_completion", 
    "get_completion_path",
]
