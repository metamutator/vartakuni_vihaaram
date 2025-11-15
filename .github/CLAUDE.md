# Claude Instructions (Single Source Reference)

This project maintains ONE authoritative instruction set for AI coding agents to avoid duplication.

## Canonical Instruction File
Primary source of truth: `.github/copilot-instructions.md`
- Contains architecture, workflows, conventions, data model, and tasks.
- Used by GitHub Copilot and should be updated first.

## Claude (Cline) Runtime Rules
Claude Code (Cline) auto-loads: `.clinerules`
- This file mirrors the canonical content for convenience.
- Do NOT edit `.clinerules` directly unless syncing from the canonical file.

## Update Workflow
1. Edit `.github/copilot-instructions.md`
2. Sync changes into `.clinerules` (manual copy or script)
3. (Optional) Adjust any Claude-specific additions in `.clinerules`

## Why This Structure?
- Prevents divergence between multiple instruction files
- Reduces maintenance overhead
- Keeps Claude and Copilot aligned on project context

## Regeneration Suggestion (Optional Script)
You may create a future script (not yet implemented) like:
```bash
python scripts/sync_instructions.py  # Copies canonical file → .clinerules
```

## If Adding New Guidance
Always place new global guidance in `.github/copilot-instructions.md` first.

## Do Not Duplicate
Avoid creating additional files like `AI_GUIDE.md`, `AGENTS.md`, or `DEVELOPER_AI_RULES.md` unless there is a clear new audience.

## Quick References
- Canonical: `.github/copilot-instructions.md`
- Claude runtime: `.clinerules`
- Data sources: `data/raw/*_SOURCE.md`
- Architecture decisions: `PROJECT_SPEC.md` Section 3.4

---
If you update this file, verify the canonical file remains the richer source.