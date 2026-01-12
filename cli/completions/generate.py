"""
Shell Completion Generation

Generate and install shell completions for bash, zsh, and fish.
Uses Typer's built-in completion functionality.
"""

import os
import subprocess
from pathlib import Path
from typing import Literal, Optional

ShellType = Literal["bash", "zsh", "fish"]


def detect_shell() -> Optional[ShellType]:
    """Detect the current shell type."""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    elif "fish" in shell:
        return "fish"
    return None


def get_completion_path(shell: ShellType) -> Path:
    """Get the path where completions should be installed."""
    home = Path.home()
    
    if shell == "zsh":
        # Check for oh-my-zsh first
        omz_completions = home / ".oh-my-zsh" / "completions"
        if omz_completions.parent.exists():
            omz_completions.mkdir(exist_ok=True)
            return omz_completions / "_lastagent"
        
        # Fallback to .zsh/completions
        zsh_completions = home / ".zsh" / "completions"
        zsh_completions.mkdir(parents=True, exist_ok=True)
        return zsh_completions / "_lastagent"
    
    elif shell == "bash":
        # Use bash-completion.d if available
        bash_completions = Path("/etc/bash_completion.d")
        if bash_completions.exists() and os.access(bash_completions, os.W_OK):
            return bash_completions / "lastagent"
        
        # Fallback to user directory
        user_completions = home / ".local" / "share" / "bash-completion" / "completions"
        user_completions.mkdir(parents=True, exist_ok=True)
        return user_completions / "lastagent"
    
    elif shell == "fish":
        fish_completions = home / ".config" / "fish" / "completions"
        fish_completions.mkdir(parents=True, exist_ok=True)
        return fish_completions / "lastagent.fish"
    
    raise ValueError(f"Unsupported shell: {shell}")


def generate_completion_script(shell: ShellType) -> str:
    """
    Generate the completion script for the given shell.
    
    Uses Typer's internal completion generation.
    """
    # Use Typer's internal completion generation
    env = os.environ.copy()
    env["_LASTAGENT_COMPLETE"] = f"{shell}_source"
    
    try:
        result = subprocess.run(
            ["lastagent"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except Exception:
        # Fallback: generate a basic completion script
        return _generate_basic_completion(shell)


def _generate_basic_completion(shell: ShellType) -> str:
    """Generate a basic completion script as fallback."""
    commands = ["chat", "agents", "server", "workflow", "mcp", "config", "init"]
    options = ["--help", "--version", "--no-color", "--yolo", "--interactive"]
    
    if shell == "zsh":
        return f'''#compdef lastagent

_lastagent() {{
    local -a commands options
    commands=({" ".join(commands)})
    options=({" ".join(options)})
    
    _arguments \\
        '1: :->command' \\
        '*: :->args'
    
    case $state in
        command)
            _describe 'command' commands
            ;;
        args)
            _describe 'option' options
            ;;
    esac
}}

_lastagent "$@"
'''
    
    elif shell == "bash":
        return f'''# bash completion for lastagent

_lastagent() {{
    local cur prev commands options
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    commands="{" ".join(commands)}"
    options="{" ".join(options)}"
    
    if [[ ${{COMP_CWORD}} == 1 ]]; then
        COMPREPLY=( $(compgen -W "$commands $options" -- $cur) )
    else
        COMPREPLY=( $(compgen -W "$options" -- $cur) )
    fi
}}

complete -F _lastagent lastagent
'''
    
    elif shell == "fish":
        cmds = "\n".join([f"complete -c lastagent -n '__fish_use_subcommand' -a {c}" for c in commands])
        return f'''# fish completion for lastagent

{cmds}
complete -c lastagent -l help -d 'Show help'
complete -c lastagent -l version -s v -d 'Show version'
complete -c lastagent -l no-color -d 'Disable color'
complete -c lastagent -l yolo -s y -d 'YOLO mode'
'''
    
    return ""


def install_completion(shell: Optional[ShellType] = None) -> tuple[bool, str]:
    """
    Install shell completion for the given or detected shell.
    
    Returns (success, message) tuple.
    """
    if shell is None:
        shell = detect_shell()
        if shell is None:
            return False, "Could not detect shell. Please specify: bash, zsh, or fish"
    
    try:
        script = generate_completion_script(shell)
        if not script:
            return False, f"Failed to generate completion script for {shell}"
        
        path = get_completion_path(shell)
        path.write_text(script)
        
        # Shell-specific instructions
        if shell == "zsh":
            return True, f"""Completion installed to {path}

Add this to your ~/.zshrc if not using oh-my-zsh:
    fpath=({path.parent} $fpath)
    autoload -Uz compinit && compinit

Then reload your shell: source ~/.zshrc"""
        
        elif shell == "bash":
            return True, f"""Completion installed to {path}

Add this to your ~/.bashrc:
    source {path}

Then reload your shell: source ~/.bashrc"""
        
        elif shell == "fish":
            return True, f"""Completion installed to {path}

Fish will automatically load completions from this directory.
Reload with: source ~/.config/fish/config.fish"""
        
        return True, f"Completion installed to {path}"
    
    except Exception as e:
        return False, f"Failed to install completion: {e}"


if __name__ == "__main__":
    # Test completion generation
    for shell in ["bash", "zsh", "fish"]:
        print(f"=== {shell} ===")
        print(generate_completion_script(shell)[:200])
        print()
