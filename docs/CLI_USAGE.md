# LastAgent CLI Usage Guide

A comprehensive guide to using the LastAgent command-line interface.

## Quick Start

```bash
# Run a task (Gemini-style positional prompt)
lastagent "Write a Python function to calculate fibonacci"

# Enter interactive mode
lastagent

# List available agents
lastagent agents

# Start API server
lastagent server
```

## Installation

```bash
# Install from PyPI
pip install lastagent

# Run setup wizard
lastagent init

# Install shell completions
lastagent --install-completion
```

---

## Commands

### `lastagent [PROMPT]`

Execute a task with positional prompt (like gemini CLI):

```bash
# Basic usage
lastagent "Explain this code"

# With YOLO mode (auto-accept)
lastagent -y "Refactor this function"

# Interactive mode after execution
lastagent -i "Write tests for this file"
```

**Options:**
| Option | Description |
|--------|-------------|
| `-y, --yolo` | Auto-accept all actions |
| `-i, --interactive` | Enter REPL after execution |
| `--no-color` | Disable colored output |

---

### `lastagent chat PROMPT`

Submit a task with explicit command (more options):

```bash
# Basic usage
lastagent chat "Write a hello world in Python"

# With working directory
lastagent chat "Refactor this file" -d ./src

# Force specific agent
lastagent chat "Explain this code" -a claude

# With system prompt
lastagent chat "Review this code" -s "Be thorough and critical"
```

**Options:**
| Option | Description |
|--------|-------------|
| `-s, --system TEXT` | System prompt to prepend |
| `-d, --dir PATH` | Working directory |
| `-a, --agent TEXT` | Force specific agent |
| `--no-markdown` | Disable markdown rendering |
| `--no-stream` | Disable streaming output |

---

### `lastagent agents`

List available agents:

```bash
# Show all agents
lastagent agents

# Filter by capability
lastagent agents -c coding

# Output as JSON
lastagent agents --json
```

**Output:**
```
                     Available Agents
┏━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Agent  ┃ Type ┃ Best For                       ┃ Status ┃
┡━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ claude │ cli  │ Complex reasoning and analysis │   ●    │
│ gemini │ cli  │ 1M+ token context window       │   ●    │
│ aider  │ cli  │ Git-aware code editing         │   ●    │
│ codex  │ cli  │ Sandboxed code execution       │   ●    │
│ goose  │ cli  │ Complex multi-step workflows   │   ●    │
└────────┴──────┴────────────────────────────────┴────────┘
```

---

### `lastagent server`

Start the REST API server:

```bash
# Default (localhost:8000)
lastagent server

# Custom port
lastagent server -p 8080

# Production mode (no reload)
lastagent server --no-reload
```

**API Endpoints:**
- `POST /v1/chat/completions` - OpenAI-compatible chat
- `GET /health` - Health check
- `GET /agents` - List agents

---

### `lastagent workflow PHASE`

Run Agile TDD workflow phases:

```bash
# Check status
lastagent workflow status

# Run planning phase
lastagent workflow plan

# Run all phases
lastagent workflow all -p ./project
```

**Phases:** `status`, `plan`, `implement`, `integrate`, `merge`, `deploy`, `present`, `inputs`, `all`

---

### `lastagent mcp`

Start as MCP server for agent-to-agent communication:

```bash
lastagent mcp
```

**MCP Tools Exposed:**
| Tool | Description |
|------|-------------|
| `lastagent_prompt` | Submit task for routing |
| `lastagent_in_directory` | Execute with working dir |
| `lastagent_with_agent` | Force specific agent |
| `lastagent_agents` | List available agents |
| `get_lastagent_capabilities` | Get agent card |
| `get_lastagent_version` | Get version |

---

### `lastagent init`

Run the installation wizard:

```bash
lastagent init
```

**What it does:**
1. Checks which agent CLIs are installed
2. Verifies API key configuration
3. Sets default preferences
4. Creates `~/.lastagent/config.yml`

---

## Interactive Mode (REPL)

Running `lastagent` without arguments enters interactive mode:

```
🤖 lastagent> /help
🤖 lastagent> Write a hello world function
🤖 lastagent> /agents
🤖 lastagent> /agent claude
🤖 lastagent [claude]> Explain quantum computing
🤖 lastagent> /exit
```

**Slash Commands:**
| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/agents` | List available agents |
| `/agent NAME` | Switch default agent |
| `/clear` | Clear the screen |
| `/history` | Show command history |
| `/config` | Show current config |
| `/exit` | Exit interactive mode |

---

## Configuration

Configuration is stored in `~/.lastagent/config.yml`:

```yaml
version: "1.0"
default_agent: auto
available_agents:
  - claude
  - gemini
  - aider
yolo_mode: false
save_history: true
```

**Environment Variables:**
| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key |
| `GEMINI_API_KEY` | Gemini API key |
| `OPENAI_API_KEY` | For Aider/Codex |
| `NO_COLOR` | Disable colored output |

---

## Shell Completions

Install tab completions for your shell:

```bash
# Auto-detect and install
lastagent --install-completion

# Show completion script
lastagent --show-completion
```

**Supported Shells:** bash, zsh, fish

---

## Examples

### Quick Tasks
```bash
lastagent "What is 2+2?"
lastagent "Explain the difference between HTTP and HTTPS"
```

### Coding Tasks
```bash
lastagent chat "Write a REST API endpoint" -d ./backend
lastagent chat "Add unit tests for this module" -a claude
lastagent chat "Refactor for better performance" -s "Prioritize readability"
```

### Agent-to-Agent (MCP)
```bash
# In Claude Desktop mcp_servers config:
{
  "lastagent": {
    "command": "lastagent",
    "args": ["mcp"]
  }
}
```

---

## Troubleshooting

### Agent CLI not found
```bash
# Check which CLIs are installed
lastagent agents

# Install missing agents
pip install aider-chat           # Aider
npm install -g @google/gemini-cli # Gemini
```

### API key issues
```bash
# Run setup wizard to check configuration
lastagent init

# Set environment variables
export ANTHROPIC_API_KEY="sk-..."
export GEMINI_API_KEY="AI..."
```

### Completions not working
```bash
# Reinstall completions
lastagent --install-completion

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

---

## Version

```bash
lastagent --version
# LastAgent version 0.1.0
```
