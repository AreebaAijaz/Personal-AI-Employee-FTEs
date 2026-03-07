# Personal AI Employee FTEs - Project Context

## Project Overview

This project provides a comprehensive blueprint for building **Autonomous AI Employees** (Digital FTEs - Full-Time Equivalents) that operate 24/7 to manage personal and business affairs. The architecture is **local-first**, **agent-driven**, and implements **human-in-the-loop** controls.

### Core Concept

A Digital FTE is an AI agent powered by **Qwen Code** (reasoning engine) and **Obsidian** (knowledge base/dashboard) that proactively manages tasks across multiple domains:
- **Personal Affairs**: Gmail, WhatsApp, Bank transactions
- **Business Operations**: Social Media, Payments, Project Tasks, Accounting

### Key Differentiators

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000-$8,000+ | $500-$2,000 |
| Consistency | 85-95% accuracy | 99%+ consistency |
| Scaling | Linear | Exponential |

## Architecture

### The Stack

| Component | Role | Technology |
|-----------|------|------------|
| **The Brain** | Reasoning engine | Qwen Code |
| **The Memory/GUI** | Dashboard & long-term memory | Obsidian (local Markdown) |
| **The Senses** | Watchers monitoring inputs | Python scripts |
| **The Hands** | External system interaction | MCP Servers |

### Perception → Reasoning → Action Loop

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PERCEPTION    │────▶│   REASONING     │────▶│     ACTION      │
│   (Watchers)    │     │  (Qwen Code)    │     │   (MCP Servers) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
- Gmail Watcher          - Read /Needs_Action    - WhatsApp/Social MCP
- WhatsApp Watcher       - Think & Plan          - Browser/Payment MCP
- File System Watcher    - Create Plan.md        - Human-in-the-Loop
- Finance Watcher        - Ralph Wiggum Loop     - Approval workflows
```

## Directory Structure

```
Personal-AI-Employee-FTEs/
├── QWEN.md                          # This context file
├── skills-lock.json                 # Skill dependencies registry
├── Personal AI Employee Hackathon 0_*.md  # Main documentation (1200+ lines)
├── .qwen/
│   └── skills/
│       └── browsing-with-playwright/    # Browser automation skill
│           ├── SKILL.md                 # Skill documentation
│           ├── references/
│           │   └── playwright-tools.md  # MCP tool reference (22 tools)
│           └── scripts/
│               ├── mcp-client.py        # Universal MCP client (HTTP + stdio)
│               ├── start-server.sh      # Start Playwright MCP server
│               ├── stop-server.sh       # Stop server gracefully
│               └── verify.py            # Server health check
└── .git/
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Qwen Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Sentinel scripts & orchestration |
| Node.js | v24+ LTS | MCP servers & automation |
| GitHub Desktop | Latest | Version control |

### Hardware Requirements

- **Minimum**: 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended**: 16GB RAM, 8-core CPU, SSD storage
- **For always-on**: Dedicated mini-PC or cloud VM

### Quick Start

#### 1. Setup Obsidian Vault

```bash
# Create vault structure
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done,Plans,Pending_Approval,Accounting,Briefings}
```

#### 2. Start Playwright MCP Server (for browser automation)

```bash
# Start server (default port 8808)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

#### 3. Use MCP Client

```bash
# List available tools
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py list \
  -u http://localhost:8808

# Call a tool (navigate to URL)
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take a screenshot
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'
```

#### 4. Configure Qwen Code MCP Servers

Create `~/.config/qwen-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

## Development Conventions

### Watcher Pattern

All Watcher scripts follow the `BaseWatcher` abstract class pattern:

```python
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Action File Schema

All action files use YAML frontmatter:

```markdown
---
type: email
from: sender@example.com
subject: Urgent: Invoice Payment
received: 2026-01-07T10:30:00Z
priority: high
status: pending
---

## Email Content
{message body}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
```

### Human-in-the-Loop Pattern

For sensitive actions, create approval request files:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A

## To Approve
Move this file to /Approved folder.
```

### Ralph Wiggum Loop (Persistence Pattern)

Use the Ralph Wiggum pattern to keep Qwen Code working autonomously:

```bash
# Start a Ralph loop
qwen "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

The Stop hook intercepts Qwen Code's exit and re-injects the prompt until:
1. Task file is moved to `/Done`, OR
2. Maximum iterations reached

## Key Features

### Monday Morning CEO Briefing

Scheduled weekly audit that generates:
- **Revenue Summary**: Total earned this week
- **Bottlenecks**: Tasks that took too long
- **Proactive Suggestions**: Cost optimization opportunities

### Watcher Types

| Watcher | Monitors | Trigger Keywords |
|---------|----------|------------------|
| Gmail | Unread important emails | N/A |
| WhatsApp | Urgent messages | "urgent", "asap", "invoice", "payment" |
| File System | Drop folder | N/A |
| Finance | Bank transactions | N/A |

### MCP Servers Available

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in vault access |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling |
| `slack-mcp` | Send messages, read channels | Team communication |

## Testing Practices

1. **Verify MCP Server**: Always run `verify.py` before browser automation tasks
2. **Graceful Shutdown**: Use `stop-server.sh` to close browser before killing process
3. **Shared Context**: Use `--shared-browser-context` flag to maintain state across calls
4. **Error Recovery**: If verification fails, restart: `stop-server.sh && start-server.sh`

## Contribution Guidelines

- All AI functionality should be implemented as **Agent Skills**
- Keep data local and accessible via Markdown files
- Implement human-in-the-loop for sensitive actions
- Use the Watcher pattern for continuous monitoring
- Document architecture decisions in the vault

## Related Documentation

- **Main Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md` (1201 lines)
- **Playwright Tools**: `.qwen/skills/browsing-with-playwright/references/playwright-tools.md` (22 tools)
- **Skill Documentation**: `.qwen/skills/browsing-with-playwright/SKILL.md`

## External Resources

- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Agent Skills Reference](https://github.com/QwenLM/Qwen-Agent)
- [MCP Server Specification](https://github.com/AlanOgic/mcp-odoo-adv)
- [Ralph Wiggum Pattern](https://github.com/QwenLM/Qwen-Code) (Qwen Code equivalent)
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/) (for cloud deployment)
