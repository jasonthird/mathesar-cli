---
name: mathesar-cli
description: Use this skill when an agent needs to operate a Mathesar instance through the mathesar CLI or optional MCP server, including login, method discovery, database/schema/table/column/record management, and arbitrary JSON-RPC calls.
---

# Mathesar CLI

Prefer MCP tools for structured agent work when available. Use CLI commands when MCP is unavailable, when a shell transcript is useful, or when a user asks for command-line usage.

## Setup

From the repository root:

```sh
uv sync --extra dev --extra mcp
```

Run CLI commands with:

```sh
uv run mathesar ...
```

Start the MCP server with:

```sh
uv run mathesar-mcp
```

## Login

Log in once before API work:

```sh
uv run mathesar --url http://localhost login --username USERNAME
```

Use `--password` only for non-interactive automation. The saved config contains URL, `sessionid`, and `csrftoken`, not the username or password.

## Discovery

Treat the target instance as authoritative:

```sh
uv run mathesar methods list
uv run mathesar methods help records.list
uv run mathesar methods signature records.list
```

## Friendly CLI Workflows

```sh
uv run mathesar db list
uv run mathesar schema list -d 1
uv run mathesar table list -d 1 -s 2200
uv run mathesar table patch -d 1 -t 17500 --name new_table_name
uv run mathesar column list -d 1 -t 17500
uv run mathesar record list -d 1 -t 17500 --limit 20
uv run mathesar record add -d 1 -t 17500 --data '{"2":"Alice"}'
```

Records are keyed by column attnum. Always call `mathesar column list` before writing records unless attnums are already known.

## Full API Coverage

Use `api` for friendly access to any RPC method:

```sh
uv run mathesar api databases configured list
uv run mathesar api schemas privileges list-direct -p database_id=1 -p schema_oid=2200
```

Hyphens become underscores. `list-direct` maps to `list_direct`.

Use raw method calls when clearer:

```sh
uv run mathesar call records.list -p database_id=1 -p table_oid=22031
uv run mathesar call records list --params-json '{"database_id": 1, "table_oid": 22031}'
```

## MCP Tools

Common tools:

```text
mathesar_login
mathesar_list_methods
mathesar_method_help
mathesar_method_signature
mathesar_call
mathesar_list_databases
mathesar_list_schemas
mathesar_list_tables
mathesar_patch_table
mathesar_list_columns
mathesar_list_records
mathesar_add_record
mathesar_patch_record
mathesar_delete_records
```

Use `mathesar_call` for exposed RPC methods without a dedicated typed tool.
