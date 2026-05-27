---
name: mathesar-cli
description: Use this skill when an agent needs to operate a Mathesar instance through this repository's CLI or optional MCP server.
---

# Mathesar CLI

The installable skill lives at `skills/mathesar-cli/SKILL.md`. Keep this root file as a short pointer for agents browsing the repository.

Use uv:

```sh
uv sync --extra dev --extra mcp
uv run mathesar --help
uv run mathesar-mcp
```

Prefer MCP tools for structured agent calls. Use CLI commands for human-facing shell workflows.
