from __future__ import annotations

from typing import Any

from .client import MathesarClient


def compact_params(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def normalize_table_columns(columns: list[Any]) -> list[Any]:
    normalized = []
    for column in columns:
        if not isinstance(column, dict):
            normalized.append(column)
            continue
        next_column = dict(column)
        column_type = next_column.get("type")
        if isinstance(column_type, str):
            next_column["type"] = {
                "name": column_type,
                "options": next_column.pop("type_options", {}),
            }
        if "nullable" in next_column and "not_null" not in next_column:
            next_column["not_null"] = not bool(next_column.pop("nullable"))
        default = next_column.get("default")
        if isinstance(default, dict) and "value" in default:
            next_column["default"] = default["value"]
        normalized.append(next_column)
    return normalized


def list_databases(client: MathesarClient, server_id: int | None = None) -> Any:
    return client.rpc("databases.configured.list", compact_params({"server_id": server_id}))


def get_database(client: MathesarClient, database_id: int) -> Any:
    return client.rpc("databases.get", {"database_id": database_id})


def list_schemas(client: MathesarClient, database_id: int) -> Any:
    return client.rpc("schemas.list", {"database_id": database_id})


def get_schema(client: MathesarClient, database_id: int, schema_oid: int) -> Any:
    return client.rpc("schemas.get", {"database_id": database_id, "schema_oid": schema_oid})


def create_schema(
    client: MathesarClient,
    database_id: int,
    name: str,
    owner_oid: int | None = None,
    description: str | None = None,
) -> Any:
    return client.rpc(
        "schemas.add",
        compact_params(
            {
                "database_id": database_id,
                "name": name,
                "owner_oid": owner_oid,
                "description": description,
            }
        ),
    )


def delete_schemas(client: MathesarClient, database_id: int, schema_oids: list[int]) -> Any:
    return client.rpc("schemas.delete", {"database_id": database_id, "schema_oids": schema_oids})


def list_tables(client: MathesarClient, database_id: int, schema_oid: int) -> Any:
    return client.rpc("tables.list", {"database_id": database_id, "schema_oid": schema_oid})


def get_table(client: MathesarClient, database_id: int, table_oid: int, metadata: bool = False) -> Any:
    method = "tables.get_with_metadata" if metadata else "tables.get"
    return client.rpc(method, {"database_id": database_id, "table_oid": table_oid})


def create_table(
    client: MathesarClient,
    database_id: int,
    schema_oid: int,
    name: str,
    columns: list[Any] | None = None,
    primary_key: dict[str, Any] | None = None,
    constraints: list[Any] | None = None,
    owner_oid: int | None = None,
    comment: str | None = None,
) -> Any:
    return client.rpc(
        "tables.add",
        compact_params(
            {
                "database_id": database_id,
                "schema_oid": schema_oid,
                "table_name": name,
                "pkey_column_info": primary_key,
                "column_data_list": normalize_table_columns(columns) if columns else None,
                "constraint_data_list": constraints,
                "owner_oid": owner_oid,
                "comment": comment,
            }
        ),
    )


def delete_table(client: MathesarClient, database_id: int, table_oid: int, cascade: bool = False) -> Any:
    return client.rpc("tables.delete", {"database_id": database_id, "table_oid": table_oid, "cascade": cascade})


def patch_table(
    client: MathesarClient,
    database_id: int,
    table_oid: int,
    name: str | None = None,
    description: str | None = None,
    columns: list[Any] | None = None,
) -> Any:
    return client.rpc(
        "tables.patch",
        {
            "database_id": database_id,
            "table_oid": table_oid,
            "table_data_dict": compact_params(
                {
                    "name": name,
                    "description": description,
                    "columns": columns,
                }
            ),
        },
    )


def list_columns(client: MathesarClient, database_id: int, table_oid: int, metadata: bool = False) -> Any:
    method = "columns.list_with_metadata" if metadata else "columns.list"
    return client.rpc(method, {"database_id": database_id, "table_oid": table_oid})


def add_columns(client: MathesarClient, database_id: int, table_oid: int, columns: list[Any]) -> Any:
    return client.rpc("columns.add", {"database_id": database_id, "table_oid": table_oid, "column_data_list": columns})


def patch_columns(client: MathesarClient, database_id: int, table_oid: int, columns: list[Any]) -> Any:
    return client.rpc("columns.patch", {"database_id": database_id, "table_oid": table_oid, "column_data_list": columns})


def delete_columns(client: MathesarClient, database_id: int, table_oid: int, attnums: list[int]) -> Any:
    return client.rpc(
        "columns.delete",
        {"database_id": database_id, "table_oid": table_oid, "column_attnums": attnums},
    )


def list_records(
    client: MathesarClient,
    database_id: int,
    table_oid: int,
    limit: int | None = None,
    offset: int | None = None,
    order: list[Any] | None = None,
    filter: dict[str, Any] | None = None,
    grouping: dict[str, Any] | None = None,
    joined_columns: list[Any] | None = None,
    summaries: bool = False,
) -> Any:
    return client.rpc(
        "records.list",
        compact_params(
            {
                "database_id": database_id,
                "table_oid": table_oid,
                "limit": limit,
                "offset": offset,
                "order": order,
                "filter": filter,
                "grouping": grouping,
                "joined_columns": joined_columns,
                "return_record_summaries": summaries,
            }
        ),
    )


def get_record(client: MathesarClient, database_id: int, table_oid: int, record_id: Any, summaries: bool = False) -> Any:
    return client.rpc(
        "records.get",
        {
            "database_id": database_id,
            "table_oid": table_oid,
            "record_id": record_id,
            "return_record_summaries": summaries,
        },
    )


def add_record(
    client: MathesarClient,
    database_id: int,
    table_oid: int,
    data: dict[str, Any],
    summaries: bool = False,
) -> Any:
    return client.rpc(
        "records.add",
        {
            "database_id": database_id,
            "table_oid": table_oid,
            "record_def": data,
            "return_record_summaries": summaries,
        },
    )


def patch_record(
    client: MathesarClient,
    database_id: int,
    table_oid: int,
    record_id: Any,
    data: dict[str, Any],
    summaries: bool = False,
) -> Any:
    return client.rpc(
        "records.patch",
        {
            "database_id": database_id,
            "table_oid": table_oid,
            "record_id": record_id,
            "record_def": data,
            "return_record_summaries": summaries,
        },
    )


def delete_records(client: MathesarClient, database_id: int, table_oid: int, record_ids: list[Any]) -> Any:
    return client.rpc(
        "records.delete",
        {
            "database_id": database_id,
            "table_oid": table_oid,
            "record_ids": record_ids,
        },
    )
