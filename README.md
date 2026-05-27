# mathesar-cli

A local CLI and optional MCP server for Mathesar's JSON-RPC API.

The project provides three access layers:

- Friendly CLI groups for common database work: `db`, `schema`, `table`, `column`, and `record`.
- Universal CLI access for every exposed Mathesar RPC method: `api`, `call`, and `rpc`.
- Optional MCP tools for agent runtimes that support structured tool calls.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- A reachable Mathesar instance

## Development

Set up the project:

```sh
uv sync --extra dev --extra mcp
```

Run tests:

```sh
uv run pytest
```

Run the CLI locally:

```sh
uv run mathesar --help
```

Build distribution artifacts:

```sh
uv build
```

## Install

From a checkout:

```sh
uv tool install --from . mathesar-cli
```

With MCP support:

```sh
uv tool install --from '.[mcp]' mathesar-cli
```

During development, prefer:

```sh
uv run mathesar ...
uv run mathesar-mcp
```

## Log In

```sh
uv run mathesar --url http://localhost login --username USER
```

Omit `--password` for an interactive prompt. For non-interactive use:

```sh
uv run mathesar --url http://localhost login --username USER --password PASS
```

The CLI saves only the Mathesar URL and session cookies:

```text
~/.config/mathesar-cli/config.json
```

It does not save the username or password. Override the config location with `MATHESAR_CLI_CONFIG_DIR`.

## Discover Methods

```sh
uv run mathesar methods list
uv run mathesar methods help records.list
uv run mathesar methods signature records.list
```

## Friendly Commands

List configured databases:

```sh
uv run mathesar db list
uv run mathesar db get -d 1
```

Manage schemas:

```sh
uv run mathesar schema list -d 1
uv run mathesar schema create -d 1 reporting
uv run mathesar schema delete -d 1 17505
```

Manage tables:

```sh
uv run mathesar table list -d 1 -s 2200
uv run mathesar table get -d 1 -t 17500 --metadata
uv run mathesar table create -d 1 -s 2200 contacts --columns '[{"name":"name","type":"text"}]'
uv run mathesar table patch -d 1 -t 17500 --name contacts_archive --description "Archived contacts"
uv run mathesar table delete -d 1 -t 17507
```

Manage columns:

```sh
uv run mathesar column list -d 1 -t 17500
uv run mathesar column add -d 1 -t 17500 --columns '[{"name":"email","type":"text"}]'
uv run mathesar column patch -d 1 -t 17500 --columns '[{"id":2,"name":"full_name"}]'
uv run mathesar column delete -d 1 -t 17500 3
```

Manage records:

```sh
uv run mathesar record list -d 1 -t 17500 --limit 20
uv run mathesar record get -d 1 -t 17500 1
uv run mathesar record add -d 1 -t 17500 --data '{"2":"Alice"}'
uv run mathesar record patch -d 1 -t 17500 1 --data '{"2":"Bob"}'
uv run mathesar record delete -d 1 -t 17500 1
```

Mathesar records are keyed by column attnum, not column name. Use `mathesar column list -d DATABASE_ID -t TABLE_OID` to find attnums.

## Universal API Access

Use `api` for readable path-style access to every RPC method:

```sh
uv run mathesar api records list -p database_id=1 -p table_oid=22031 -p limit=20
uv run mathesar api databases configured list
uv run mathesar api schemas privileges list-direct -p database_id=1 -p schema_oid=2200
```

Hyphens in path segments become underscores, so `list-direct` calls `list_direct`.

Use `call` when you prefer method names:

```sh
uv run mathesar call records.list -p database_id=1 -p table_oid=22031
uv run mathesar call records list --params-json '{"database_id": 1, "table_oid": 22031}'
```

Use `rpc` for exact JSON-RPC terminology:

```sh
uv run mathesar rpc users.list
```

Values passed with `-p` are parsed as JSON when possible, so numbers, booleans, arrays, objects, and `null` work naturally.

## Environment Variables

```sh
export MATHESAR_URL=http://localhost
export MATHESAR_SESSIONID=...
export MATHESAR_CSRFTOKEN=...
```

## MCP Server

Install MCP support:

```sh
uv sync --extra mcp
```

Start the server over stdio:

```sh
uv run mathesar-mcp
```

Useful MCP tools include:

- `mathesar_login`
- `mathesar_list_methods`
- `mathesar_method_help`
- `mathesar_method_signature`
- `mathesar_call`
- `mathesar_list_databases`
- `mathesar_list_schemas`
- `mathesar_create_schema`
- `mathesar_delete_schemas`
- `mathesar_list_tables`
- `mathesar_create_table`
- `mathesar_patch_table`
- `mathesar_delete_table`
- `mathesar_list_columns`
- `mathesar_add_columns`
- `mathesar_patch_columns`
- `mathesar_delete_columns`
- `mathesar_list_records`
- `mathesar_add_record`
- `mathesar_patch_record`
- `mathesar_delete_records`

Use MCP tools when an agent runtime supports MCP. Use CLI commands for manual shell work, transcripts, and environments without MCP.

## Publishing

Build:

```sh
uv build
```

Validate the distribution metadata with Twine:

```sh
uv run --extra publish twine check dist/*
```

Publish to TestPyPI:

```sh
TWINE_USERNAME="__token__" TWINE_PASSWORD="$TEST_PYPI_TOKEN" \
  uv run --extra publish twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Publish to PyPI:

```sh
TWINE_USERNAME="__token__" TWINE_PASSWORD="$PYPI_TOKEN" \
  uv run --extra publish twine upload dist/*
```

Before publishing, confirm the package name is available and set final project URLs in `pyproject.toml`.

## License

GNU General Public License v3.0 or later. See [LICENSE](LICENSE).

## Method Coverage

Mathesar's upstream JSON-RPC API is not guaranteed to be stable yet, so method names, parameters, signatures, and response shapes may break between Mathesar releases. Run `mathesar methods list`, `mathesar methods help METHOD`, and `mathesar methods signature METHOD` against your target instance when building automation.

This client was tested against a local Mathesar instance on 2026-05-28 reporting:

- `last_confirmed_sql_version`: `0.10.1`
- `system.listMethods`: 106 exposed RPC methods

See [docs/METHODS.md](docs/METHODS.md) for the method list observed from that instance during development.
