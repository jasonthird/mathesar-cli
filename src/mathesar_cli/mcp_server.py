from __future__ import annotations

import html
import re
from typing import Any

from .client import MathesarClient
from .config import build_client_config, save_config
from .operations import (
    add_columns,
    add_record,
    create_schema,
    create_table,
    delete_columns,
    delete_records,
    delete_schemas,
    delete_table,
    get_database,
    get_record,
    get_schema,
    get_table,
    list_columns,
    list_databases,
    list_records,
    list_schemas,
    list_tables,
    patch_columns,
    patch_record,
    patch_table,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as error:  # pragma: no cover - exercised only without optional extra
    raise SystemExit("Install MCP support with: python3 -m pip install 'mathesar-cli[mcp]'") from error


mcp = FastMCP("mathesar")


def client(timeout: float = 30.0) -> MathesarClient:
    return MathesarClient(
        build_client_config(
            url=None,
            sessionid=None,
            csrftoken=None,
            timeout=timeout,
        )
    )


def html_to_text(value: str) -> str:
    text = re.sub(r"</p>\s*<p>", "\n\n", value)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


@mcp.tool()
def mathesar_login(url: str, username: str, password: str, timeout: float = 30.0) -> dict[str, Any]:
    """Log in to Mathesar and save the session for CLI and MCP tools."""
    login_client = MathesarClient(
        build_client_config(
            url=url,
            sessionid=None,
            csrftoken=None,
            timeout=timeout,
            require_auth=False,
        )
    )
    config = login_client.login(username, password)
    path = save_config(
        {
            "url": config.base_url,
            "sessionid": config.sessionid,
            "csrftoken": config.csrftoken,
        }
    )
    return {"url": config.base_url, "config_path": str(path), "authenticated": True}


@mcp.tool()
def mathesar_list_methods(timeout: float = 30.0) -> list[str]:
    """List every JSON-RPC method exposed by the configured Mathesar instance."""
    return client(timeout).list_methods()


@mcp.tool()
def mathesar_method_help(method_name: str, raw_html: bool = False, timeout: float = 30.0) -> str:
    """Show Mathesar's help text for one JSON-RPC method."""
    help_text = client(timeout).method_help(method_name)
    return help_text if raw_html else html_to_text(help_text)


@mcp.tool()
def mathesar_method_signature(method_name: str, timeout: float = 30.0) -> Any:
    """Show Mathesar's JSON-RPC signature metadata for one method."""
    return client(timeout).method_signature(method_name)


@mcp.tool()
def mathesar_call(method: str, params: dict[str, Any] | None = None, timeout: float = 30.0) -> Any:
    """Call any Mathesar JSON-RPC method."""
    return client(timeout).rpc(method, params or {})


@mcp.tool()
def mathesar_list_databases(server_id: int | None = None, timeout: float = 30.0) -> Any:
    """List configured Mathesar databases."""
    return list_databases(client(timeout), server_id)


@mcp.tool()
def mathesar_get_database(database_id: int, timeout: float = 30.0) -> Any:
    """Get one Mathesar database by id."""
    return get_database(client(timeout), database_id)


@mcp.tool()
def mathesar_list_schemas(database_id: int, timeout: float = 30.0) -> Any:
    """List schemas in a database."""
    return list_schemas(client(timeout), database_id)


@mcp.tool()
def mathesar_get_schema(database_id: int, schema_oid: int, timeout: float = 30.0) -> Any:
    """Get one schema."""
    return get_schema(client(timeout), database_id, schema_oid)


@mcp.tool()
def mathesar_create_schema(
    database_id: int,
    name: str,
    owner_oid: int | None = None,
    description: str | None = None,
    timeout: float = 30.0,
) -> Any:
    """Create a schema."""
    return create_schema(client(timeout), database_id, name, owner_oid, description)


@mcp.tool()
def mathesar_delete_schemas(database_id: int, schema_oids: list[int], timeout: float = 30.0) -> Any:
    """Delete one or more schemas by OID."""
    return delete_schemas(client(timeout), database_id, schema_oids)


@mcp.tool()
def mathesar_list_tables(database_id: int, schema_oid: int, timeout: float = 30.0) -> Any:
    """List tables in a schema."""
    return list_tables(client(timeout), database_id, schema_oid)


@mcp.tool()
def mathesar_get_table(database_id: int, table_oid: int, metadata: bool = False, timeout: float = 30.0) -> Any:
    """Get one table."""
    return get_table(client(timeout), database_id, table_oid, metadata)


@mcp.tool()
def mathesar_create_table(
    database_id: int,
    schema_oid: int,
    name: str,
    columns: list[Any] | None = None,
    primary_key: dict[str, Any] | None = None,
    constraints: list[Any] | None = None,
    owner_oid: int | None = None,
    comment: str | None = None,
    timeout: float = 30.0,
) -> Any:
    """Create a table. Column types may use simple strings like {'name': 'email', 'type': 'text'}."""
    return create_table(client(timeout), database_id, schema_oid, name, columns, primary_key, constraints, owner_oid, comment)


@mcp.tool()
def mathesar_delete_table(database_id: int, table_oid: int, cascade: bool = False, timeout: float = 30.0) -> Any:
    """Delete a table."""
    return delete_table(client(timeout), database_id, table_oid, cascade)


@mcp.tool()
def mathesar_patch_table(
    database_id: int,
    table_oid: int,
    name: str | None = None,
    description: str | None = None,
    columns: list[Any] | None = None,
    timeout: float = 30.0,
) -> Any:
    """Rename a table, edit its description, or alter columns."""
    return patch_table(client(timeout), database_id, table_oid, name, description, columns)


@mcp.tool()
def mathesar_list_columns(database_id: int, table_oid: int, metadata: bool = False, timeout: float = 30.0) -> Any:
    """List columns in a table. Use this before writing records; records are keyed by column attnum."""
    return list_columns(client(timeout), database_id, table_oid, metadata)


@mcp.tool()
def mathesar_add_columns(database_id: int, table_oid: int, columns: list[Any], timeout: float = 30.0) -> Any:
    """Add columns to a table."""
    return add_columns(client(timeout), database_id, table_oid, columns)


@mcp.tool()
def mathesar_patch_columns(database_id: int, table_oid: int, columns: list[Any], timeout: float = 30.0) -> Any:
    """Patch column metadata or settings."""
    return patch_columns(client(timeout), database_id, table_oid, columns)


@mcp.tool()
def mathesar_delete_columns(database_id: int, table_oid: int, attnums: list[int], timeout: float = 30.0) -> Any:
    """Delete columns by attnum."""
    return delete_columns(client(timeout), database_id, table_oid, attnums)


@mcp.tool()
def mathesar_list_records(
    database_id: int,
    table_oid: int,
    limit: int | None = None,
    offset: int | None = None,
    order: list[Any] | None = None,
    filter: dict[str, Any] | None = None,
    grouping: dict[str, Any] | None = None,
    joined_columns: list[Any] | None = None,
    summaries: bool = False,
    timeout: float = 30.0,
) -> Any:
    """List records from a table."""
    return list_records(
        client(timeout),
        database_id,
        table_oid,
        limit,
        offset,
        order,
        filter,
        grouping,
        joined_columns,
        summaries,
    )


@mcp.tool()
def mathesar_get_record(
    database_id: int,
    table_oid: int,
    record_id: Any,
    summaries: bool = False,
    timeout: float = 30.0,
) -> Any:
    """Get one record by primary key."""
    return get_record(client(timeout), database_id, table_oid, record_id, summaries)


@mcp.tool()
def mathesar_add_record(
    database_id: int,
    table_oid: int,
    data: dict[str, Any],
    summaries: bool = False,
    timeout: float = 30.0,
) -> Any:
    """Add one record. Data must be keyed by column attnum as strings."""
    return add_record(client(timeout), database_id, table_oid, data, summaries)


@mcp.tool()
def mathesar_patch_record(
    database_id: int,
    table_oid: int,
    record_id: Any,
    data: dict[str, Any],
    summaries: bool = False,
    timeout: float = 30.0,
) -> Any:
    """Patch one record by primary key. Data must be keyed by column attnum as strings."""
    return patch_record(client(timeout), database_id, table_oid, record_id, data, summaries)


@mcp.tool()
def mathesar_delete_records(database_id: int, table_oid: int, record_ids: list[Any], timeout: float = 30.0) -> Any:
    """Delete records by primary key."""
    return delete_records(client(timeout), database_id, table_oid, record_ids)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
