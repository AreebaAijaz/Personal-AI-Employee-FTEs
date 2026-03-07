# AI Employee - Bronze Tier Implementation

> **Tagline**: Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is a **Bronze Tier** implementation of the Personal AI Employee FTE system. It provides the foundational layer for autonomous task processing using Qwen Code and Obsidian.

## ✅ Bronze Tier Deliverables

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System monitoring)
- [x] Qwen Code successfully reading from and writing to the vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] All AI functionality implemented as Agent Skills

## 📁 Project Structure

```
Personal-AI-Employee-FTEs/
├── AI_Employee_Vault/           # Obsidian vault
│   ├── Dashboard.md             # Real-time status dashboard
│   ├── Company_Handbook.md      # Rules of Engagement
│   ├── Inbox/                   # Drop folder for files
│   ├── Needs_Action/            # Pending action items
│   ├── Done/                    # Completed items
│   ├── Plans/                   # Action plans
│   ├── Pending_Approval/        # Awaiting human decision
│   ├── Approved/                # Ready for execution
│   ├── Rejected/                # Declined actions
│   ├── Accounting/              # Financial records
│   ├── Briefings/               # CEO briefings
│   ├── Logs/                    # System logs
│   └── Files/                   # Stored files
├── watchers/                    # Watcher scripts
│   ├── base_watcher.py          # Abstract base class
│   ├── filesystem_watcher.py    # File system monitor
│   └── requirements.txt         # Python dependencies
└── BRONZE-TIER-README.md        # This file
```

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.13+ | Watcher scripts |
| Qwen Code | Active subscription | Reasoning engine |
| Obsidian | v1.10.6+ (free) | Knowledge base |

### Step 1: Install Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

### Step 2: Verify Vault Structure

The vault should be created at `AI_Employee_Vault/` with all required folders.

### Step 3: Start the File System Watcher

**Option A: Polling Mode** (detects existing files)

```bash
cd watchers
python filesystem_watcher.py --vault ../AI_Employee_Vault --interval 30
```

**Option B: Observer Mode** (real-time, more efficient)

```bash
cd watchers
python filesystem_watcher.py --vault ../AI_Employee_Vault --observer
```

### Step 4: Test the System

1. **Drop a file** into `AI_Employee_Vault/Inbox/`
2. **Wait** for the watcher to detect it (within 30 seconds)
3. **Check** `AI_Employee_Vault/Needs_Action/` for a new action file
4. **Process** the action file using Qwen Code

### Step 5: Process with Qwen Code

Open Qwen Code pointed at your vault:

```bash
cd AI_Employee_Vault
qwen
```

Then prompt:

```
Check the /Needs_Action folder and process any pending items.
Create a plan in /Plans/ and move completed items to /Done.
Follow the rules in Company_Handbook.md.
```

## 📖 Usage Guide

### How the File System Watcher Works

1. **Monitors** the `Inbox/` folder for new files
2. **Copies** dropped files to `Files/` for safekeeping
3. **Creates** an action file in `Needs_Action/` with:
   - File metadata (size, timestamp, path)
   - Content preview (for text files)
   - Suggested actions checklist
4. **Logs** all activity to `Logs/YYYY-MM-DD.log`

### Action File Format

Each action file follows this schema:

```markdown
---
type: file_drop
original_name: document.pdf
size: 1024
priority: normal
status: pending
---

# File Dropped for Processing

## File Details
- **Original Name**: document.pdf
- **Size**: 1.0 KB
- **Dropped At**: 2026-03-07 12:00:00

## Suggested Actions
- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done when complete
```

### Workflow States

```
Inbox → Needs_Action → [Qwen Code processes] → Plans → [Human approves] → Done
```

## ⚙️ Configuration

### Watcher Options

| Flag | Description | Default |
|------|-------------|---------|
| `--vault, -v` | Path to Obsidian vault | `AI_Employee_Vault` |
| `--drop-folder, -d` | Folder to watch | `vault/Inbox` |
| `--interval, -i` | Poll interval (seconds) | `30` |
| `--observer, -o` | Use real-time Observer | `False` |

### Example Commands

```bash
# Run with custom interval (10 seconds)
python filesystem_watcher.py --vault ../AI_Employee_Vault --interval 10

# Run with custom drop folder
python filesystem_watcher.py --vault ../AI_Employee_Vault --drop-folder /path/to/drops

# Run in background (Linux/Mac)
nohup python filesystem_watcher.py --vault ../AI_Employee_Vault --observer &

# Run in background (Windows)
start /B python filesystem_watcher.py --vault ../AI_Employee_Vault --observer
```

## 🧪 Testing

### Test the Watcher

1. Start the watcher in one terminal:
   ```bash
   python filesystem_watcher.py --vault ../AI_Employee_Vault --interval 5
   ```

2. Drop a test file in another terminal:
   ```bash
   echo "Test content" > ../AI_Employee_Vault/Inbox/test.txt
   ```

3. Verify action file created:
   ```bash
   ls ../AI_Employee_Vault/Needs_Action/
   ```

Expected: `FILE_test_2026-03-07.md`

## 🔧 Troubleshooting

### Watcher Not Detecting Files

- **Check** the watcher is running: `ps aux | grep filesystem_watcher`
- **Verify** the Inbox folder path is correct
- **Check** logs in `Logs/YYYY-MM-DD.log`
- **Try** Observer mode for real-time detection

### Action File Not Created

- **Ensure** file is not hidden (doesn't start with `.`)
- **Check** file permissions allow reading
- **Review** logs for error messages

### Qwen Code Not Processing

- **Verify** Qwen Code is installed: `qwen --version`
- **Ensure** running from vault directory
- **Check** `Company_Handbook.md` exists for guidance

## 📝 Next Steps (Silver Tier)

To upgrade to Silver Tier, add:

1. **Second Watcher** (Gmail or WhatsApp)
2. **MCP Server** for external actions (email sending)
3. **Human-in-the-Loop** approval workflow
4. **Scheduled Operations** via cron/Task Scheduler
5. **Plan.md** creation by Qwen Code

## 🛡️ Security Notes

- **Never** commit `.env` files with credentials
- **Add** `Logs/` to `.gitignore` (may contain sensitive data)
- **Review** all actions before approving external operations
- **Rotate** credentials regularly

## 📚 Documentation

- **Main Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Company Handbook**: `AI_Employee_Vault/Company_Handbook.md`
- **Dashboard**: `AI_Employee_Vault/Dashboard.md`

## 🤝 Support

For issues or questions:
- Check the main hackathon document
- Review logs in `Logs/` folder
- Join Wednesday Research Meeting (see main doc for Zoom link)

---

*Bronze Tier v0.1.0 - Built for Personal AI Employee Hackathon 0*
