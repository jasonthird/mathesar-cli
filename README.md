# mathesar-cli

## Install

Run without installing with `uvx`:

```sh
uvx mathesar-cli --help
```

Install as an isolated CLI with `uv tool`:

```sh
uv tool install mathesar-cli
```

Or with `pipx`:

```sh
pipx install mathesar-cli
```

Then log in and start using it:

```sh
mathesar-cli --url http://localhost login --username USER
mathesar-cli db list
```

For the optional MCP server, install the MCP extra from a checkout or package source that supports extras:

```sh
uv tool install 'mathesar-cli[mcp]'
mathesar-mcp
```

## What It Is

`mathesar-cli` is a local CLI and optional MCP server for Mathesar's JSON-RPC API.

It provides three access layers:

- Friendly CLI groups for common database work: `db`, `schema`, `table`, `column`, and `record`.
- Universal CLI access for every exposed Mathesar RPC method: `api`, `call`, and `rpc`.
- Optional MCP tools for agent runtimes that support structured tool calls.

## Requirements

- Python 3.10+
- A reachable Mathesar instance
- `uv`, `pipx`, or `pip` for installation

## Development

Set up the project from a checkout:

```sh
uv sync --extra dev --extra mcp --extra publish
```

Run tests:

```sh
uv run --extra dev pytest
```

Run the CLI locally:

```sh
uv run mathesar-cli --help
```

Build distribution artifacts:

```sh
uv build
```

## Log In

```sh
mathesar-cli --url http://localhost login --username USER
```

Omit `--password` for an interactive prompt. For non-interactive use:

```sh
mathesar-cli --url http://localhost login --username USER --password PASS
```

The CLI saves only the Mathesar URL and session cookies:

```text
~/.config/mathesar-cli/config.json
```

It does not save the username or password. Override the config location with `MATHESAR_CLI_CONFIG_DIR`.

## Discover Methods

```sh
mathesar-cli methods list
mathesar-cli methods help records.list
mathesar-cli methods signature records.list
```

## Friendly Commands

List configured databases:

```sh
mathesar-cli db list
mathesar-cli db get -d 1
```

Manage schemas:

```sh
mathesar-cli schema list -d 1
mathesar-cli schema create -d 1 reporting
mathesar-cli schema delete -d 1 17505
```

Manage tables:

```sh
mathesar-cli table list -d 1 -s 2200
mathesar-cli table get -d 1 -t 17500 --metadata
mathesar-cli table create -d 1 -s 2200 contacts --columns '[{"name":"name","type":"text"}]'
mathesar-cli table patch -d 1 -t 17500 --name contacts_archive --description "Archived contacts"
mathesar-cli table delete -d 1 -t 17507
```

Manage columns:

```sh
mathesar-cli column list -d 1 -t 17500
mathesar-cli column add -d 1 -t 17500 --columns '[{"name":"email","type":"text"}]'
mathesar-cli column patch -d 1 -t 17500 --columns '[{"id":2,"name":"full_name"}]'
mathesar-cli column delete -d 1 -t 17500 3
```

Manage records:

```sh
mathesar-cli record list -d 1 -t 17500 --limit 20
mathesar-cli record get -d 1 -t 17500 1
mathesar-cli record add -d 1 -t 17500 --data '{"2":"Alice"}'
mathesar-cli record patch -d 1 -t 17500 1 --data '{"2":"Bob"}'
mathesar-cli record delete -d 1 -t 17500 1
```

Mathesar records are keyed by column attnum, not column name. Use `mathesar-cli column list -d DATABASE_ID -t TABLE_OID` to find attnums.

## Universal API Access

Use `api` for readable path-style access to every RPC method:

```sh
mathesar-cli api records list -p database_id=1 -p table_oid=22031 -p limit=20
mathesar-cli api databases configured list
mathesar-cli api schemas privileges list-direct -p database_id=1 -p schema_oid=2200
```

Hyphens in path segments become underscores, so `list-direct` calls `list_direct`.

Use `call` when you prefer method names:

```sh
mathesar-cli call records.list -p database_id=1 -p table_oid=22031
mathesar-cli call records list --params-json '{"database_id": 1, "table_oid": 22031}'
```

Use `rpc` for exact JSON-RPC terminology:

```sh
mathesar-cli rpc users.list
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
mathesar-mcp
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

Mathesar's upstream JSON-RPC API is not guaranteed to be stable yet, so method names, parameters, signatures, and response shapes may break between Mathesar releases. Run `mathesar-cli methods list`, `mathesar-cli methods help METHOD`, and `mathesar-cli methods signature METHOD` against your target instance when building automation.

This client was tested against a local Mathesar instance on 2026-05-28 reporting:

- `last_confirmed_sql_version`: `0.10.1`
- `system.listMethods`: 106 exposed RPC methods

See [docs/METHODS.md](docs/METHODS.md) for the method list observed from that instance during development.
