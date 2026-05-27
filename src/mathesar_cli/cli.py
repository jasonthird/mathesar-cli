from __future__ import annotations

import argparse
import getpass
import html
import json
import re
import sys
from typing import Any

from .client import MathesarClient, MathesarClientError
from .config import build_client_config, save_config
from .operations import (
    add_columns,
    add_record,
    compact_params,
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
    normalize_table_columns,
    patch_columns,
    patch_table,
    patch_record,
)


def parse_json_value(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def parse_param(value: str) -> tuple[str, Any]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("parameters must be KEY=VALUE")
    key, raw_value = value.split("=", 1)
    if not key:
        raise argparse.ArgumentTypeError("parameter key cannot be empty")
    return key, parse_json_value(raw_value)


def merge_params(params_json: str | None, pairs: list[tuple[str, Any]] | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if params_json:
        parsed = json.loads(params_json)
        if not isinstance(parsed, dict):
            raise ValueError("--params-json must be a JSON object")
        params.update(parsed)
    for key, value in pairs or []:
        params[key] = value
    return params


def json_object(value: str) -> dict[str, Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object")
    return parsed


def json_array(value: str) -> list[Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("Expected a JSON array")
    return parsed


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def html_to_text(value: str) -> str:
    text = re.sub(r"</p>\s*<p>", "\n\n", value)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", help="Mathesar base URL, e.g. http://localhost:8000")
    parser.add_argument("--sessionid", help="Django sessionid cookie value")
    parser.add_argument("--csrftoken", help="Django csrftoken cookie value")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds")


def client_from_args(args: argparse.Namespace) -> MathesarClient:
    return MathesarClient(
        build_client_config(
            url=args.url,
            sessionid=args.sessionid,
            csrftoken=args.csrftoken,
            timeout=args.timeout,
        )
    )


def unauthenticated_client_from_args(args: argparse.Namespace) -> MathesarClient:
    config = build_client_config(
        url=args.url,
        sessionid=args.sessionid,
        csrftoken=args.csrftoken,
        timeout=args.timeout,
        require_auth=False,
    )
    return MathesarClient(config)


def method_from_parts(parts: list[str]) -> str:
    if not parts:
        raise ValueError("Provide a method name, e.g. records.list")
    if len(parts) == 1:
        return parts[0]
    return ".".join(parts)


def handle_config_set(args: argparse.Namespace) -> int:
    if not any([args.url, args.sessionid, args.csrftoken]):
        raise ValueError("Provide at least one value to save.")
    path = save_config(
        {
            "url": args.url,
            "sessionid": args.sessionid,
            "csrftoken": args.csrftoken,
        }
    )
    print(f"Saved config to {path}")
    return 0


def handle_login(args: argparse.Namespace) -> int:
    password = args.password or getpass.getpass("Mathesar password: ")
    config = unauthenticated_client_from_args(args).login(args.username, password)
    path = save_config(
        {
            "url": config.base_url,
            "sessionid": config.sessionid,
            "csrftoken": config.csrftoken,
        }
    )
    print(f"Logged in to {config.base_url}")
    print(f"Saved session to {path}")
    return 0


def handle_rpc(args: argparse.Namespace) -> int:
    result = client_from_args(args).rpc(args.method, merge_params(args.params_json, args.param))
    print_json(result)
    return 0


def handle_call(args: argparse.Namespace) -> int:
    result = client_from_args(args).rpc(method_from_parts(args.method), merge_params(args.params_json, args.param))
    print_json(result)
    return 0


def friendly_method_name(parts: list[str]) -> str:
    if not parts:
        raise ValueError("Provide an API path, e.g. records list")
    return ".".join(part.replace("-", "_") for part in parts)


def handle_api(args: argparse.Namespace) -> int:
    result = client_from_args(args).rpc(friendly_method_name(args.method), merge_params(args.params_json, args.param))
    print_json(result)
    return 0


def handle_methods_list(args: argparse.Namespace) -> int:
    methods = client_from_args(args).list_methods()
    if args.json:
        print_json(methods)
    else:
        for method in methods:
            print(method)
    return 0


def handle_methods_help(args: argparse.Namespace) -> int:
    help_text = client_from_args(args).method_help(args.method)
    print(help_text if args.html else html_to_text(help_text))
    return 0


def handle_methods_signature(args: argparse.Namespace) -> int:
    print_json(client_from_args(args).method_signature(args.method))
    return 0


def rpc_and_print(args: argparse.Namespace, method: str, params: dict[str, Any]) -> int:
    print_json(client_from_args(args).rpc(method, compact_params(params)))
    return 0


def handle_db_list(args: argparse.Namespace) -> int:
    print_json(list_databases(client_from_args(args), args.server_id))
    return 0


def handle_db_get(args: argparse.Namespace) -> int:
    print_json(get_database(client_from_args(args), args.database_id))
    return 0


def handle_schema_list(args: argparse.Namespace) -> int:
    print_json(list_schemas(client_from_args(args), args.database_id))
    return 0


def handle_schema_get(args: argparse.Namespace) -> int:
    print_json(get_schema(client_from_args(args), args.database_id, args.schema_oid))
    return 0


def handle_schema_create(args: argparse.Namespace) -> int:
    print_json(create_schema(client_from_args(args), args.database_id, args.name, args.owner_oid, args.description))
    return 0


def handle_schema_delete(args: argparse.Namespace) -> int:
    print_json(delete_schemas(client_from_args(args), args.database_id, args.schema_oids))
    return 0


def handle_table_list(args: argparse.Namespace) -> int:
    print_json(list_tables(client_from_args(args), args.database_id, args.schema_oid))
    return 0


def handle_table_get(args: argparse.Namespace) -> int:
    print_json(get_table(client_from_args(args), args.database_id, args.table_oid, args.metadata))
    return 0


def handle_table_create(args: argparse.Namespace) -> int:
    print_json(
        create_table(
            client_from_args(args),
            args.database_id,
            args.schema_oid,
            args.name,
            json_array(args.columns) if args.columns else None,
            json_object(args.primary_key) if args.primary_key else None,
            json_array(args.constraints) if args.constraints else None,
            args.owner_oid,
            args.comment,
        )
    )
    return 0


def handle_table_delete(args: argparse.Namespace) -> int:
    print_json(delete_table(client_from_args(args), args.database_id, args.table_oid, args.cascade))
    return 0


def handle_table_patch(args: argparse.Namespace) -> int:
    if not any([args.name is not None, args.description is not None, args.columns is not None]):
        raise ValueError("Provide at least one table alteration: --name, --description, or --columns.")
    print_json(
        patch_table(
            client_from_args(args),
            args.database_id,
            args.table_oid,
            args.name,
            args.description,
            json_array(args.columns) if args.columns else None,
        )
    )
    return 0


def handle_column_list(args: argparse.Namespace) -> int:
    print_json(list_columns(client_from_args(args), args.database_id, args.table_oid, args.metadata))
    return 0


def handle_column_add(args: argparse.Namespace) -> int:
    print_json(add_columns(client_from_args(args), args.database_id, args.table_oid, json_array(args.columns)))
    return 0


def handle_column_patch(args: argparse.Namespace) -> int:
    print_json(patch_columns(client_from_args(args), args.database_id, args.table_oid, json_array(args.columns)))
    return 0


def handle_column_delete(args: argparse.Namespace) -> int:
    print_json(delete_columns(client_from_args(args), args.database_id, args.table_oid, args.attnums))
    return 0


def handle_record_list(args: argparse.Namespace) -> int:
    print_json(
        list_records(
            client_from_args(args),
            args.database_id,
            args.table_oid,
            args.limit,
            args.offset,
            json_array(args.order) if args.order else None,
            json_object(args.filter) if args.filter else None,
            json_object(args.grouping) if args.grouping else None,
            json_array(args.joined_columns) if args.joined_columns else None,
            args.summaries,
        )
    )
    return 0


def handle_record_get(args: argparse.Namespace) -> int:
    print_json(get_record(client_from_args(args), args.database_id, args.table_oid, parse_json_value(args.record_id), args.summaries))
    return 0


def handle_record_add(args: argparse.Namespace) -> int:
    print_json(add_record(client_from_args(args), args.database_id, args.table_oid, json_object(args.data), args.summaries))
    return 0


def handle_record_patch(args: argparse.Namespace) -> int:
    print_json(
        patch_record(
            client_from_args(args),
            args.database_id,
            args.table_oid,
            parse_json_value(args.record_id),
            json_object(args.data),
            args.summaries,
        )
    )
    return 0


def handle_record_delete(args: argparse.Namespace) -> int:
    print_json(
        delete_records(
            client_from_args(args),
            args.database_id,
            args.table_oid,
            [parse_json_value(value) for value in args.record_ids],
        )
    )
    return 0


def add_param_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--params-json", help="JSON object containing named RPC parameters")
    parser.add_argument("-p", "--param", action="append", type=parse_param, help="Named RPC parameter as KEY=JSON_VALUE")


def add_database_id(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-d", "--database-id", type=int, required=True, help="Mathesar database id")


def add_schema_oid(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-s", "--schema-oid", type=int, required=True, help="PostgreSQL schema OID")


def add_table_oid(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-t", "--table-oid", type=int, required=True, help="PostgreSQL table OID")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mathesar", description="CLI JSON-RPC client for Mathesar")
    add_common_options(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config", help="Manage local CLI configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)
    config_set = config_subparsers.add_parser("set", help="Save URL and auth cookie values")
    config_set.add_argument("--url")
    config_set.add_argument("--sessionid")
    config_set.add_argument("--csrftoken")
    config_set.set_defaults(func=handle_config_set)

    login_parser = subparsers.add_parser("login", help="Log in with Mathesar username and password")
    login_parser.add_argument("--username", required=True, help="Mathesar username")
    login_parser.add_argument("--password", help="Mathesar password. Omit to enter it interactively.")
    login_parser.set_defaults(func=handle_login)

    methods_parser = subparsers.add_parser("methods", help="Discover Mathesar RPC methods")
    methods_subparsers = methods_parser.add_subparsers(dest="methods_command", required=True)
    methods_list = methods_subparsers.add_parser("list", help="List every method exposed by system.listMethods")
    methods_list.add_argument("--json", action="store_true", help="Print the method list as JSON")
    methods_list.set_defaults(func=handle_methods_list)

    methods_help = methods_subparsers.add_parser("help", help="Show system.methodHelp for an RPC method")
    methods_help.add_argument("method")
    methods_help.add_argument("--html", action="store_true", help="Print Mathesar's raw HTML help")
    methods_help.set_defaults(func=handle_methods_help)

    methods_signature = methods_subparsers.add_parser("signature", help="Show system.methodSignature for an RPC method")
    methods_signature.add_argument("method")
    methods_signature.set_defaults(func=handle_methods_signature)

    rpc_parser = subparsers.add_parser("rpc", help="Call any Mathesar RPC method")
    rpc_parser.add_argument("method", help="RPC method, e.g. tables.list")
    add_param_options(rpc_parser)
    rpc_parser.set_defaults(func=handle_rpc)

    call_parser = subparsers.add_parser("call", help="Call any RPC method using dotted or space-separated names")
    call_parser.add_argument("method", nargs="+", help="RPC method, e.g. records list or records.list")
    add_param_options(call_parser)
    call_parser.set_defaults(func=handle_call)

    api_parser = subparsers.add_parser(
        "api",
        help="Friendly path-style access to any RPC method, e.g. `api records list`",
    )
    api_parser.add_argument("method", nargs="+", help="RPC path. Hyphens become underscores.")
    add_param_options(api_parser)
    api_parser.set_defaults(func=handle_api)

    db_parser = subparsers.add_parser("db", help="Manage configured databases")
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)
    db_list = db_subparsers.add_parser("list", help="List configured databases")
    db_list.add_argument("--server-id", type=int, help="Only list databases for this server id")
    db_list.set_defaults(func=handle_db_list)
    db_get = db_subparsers.add_parser("get", help="Get one database")
    add_database_id(db_get)
    db_get.set_defaults(func=handle_db_get)

    schema_parser = subparsers.add_parser("schema", help="Manage schemas")
    schema_subparsers = schema_parser.add_subparsers(dest="schema_command", required=True)
    schema_list = schema_subparsers.add_parser("list", help="List schemas")
    add_database_id(schema_list)
    schema_list.set_defaults(func=handle_schema_list)
    schema_get = schema_subparsers.add_parser("get", help="Get one schema")
    add_database_id(schema_get)
    add_schema_oid(schema_get)
    schema_get.set_defaults(func=handle_schema_get)
    schema_create = schema_subparsers.add_parser("create", help="Create a schema")
    add_database_id(schema_create)
    schema_create.add_argument("name", help="Schema name")
    schema_create.add_argument("--owner-oid", type=int)
    schema_create.add_argument("--description")
    schema_create.set_defaults(func=handle_schema_create)
    schema_delete = schema_subparsers.add_parser("delete", help="Delete one or more schemas")
    add_database_id(schema_delete)
    schema_delete.add_argument("schema_oids", nargs="+", type=int, help="Schema OID(s) to delete")
    schema_delete.set_defaults(func=handle_schema_delete)

    table_parser = subparsers.add_parser("table", help="Manage tables")
    table_subparsers = table_parser.add_subparsers(dest="table_command", required=True)
    table_list = table_subparsers.add_parser("list", help="List tables in a schema")
    add_database_id(table_list)
    add_schema_oid(table_list)
    table_list.set_defaults(func=handle_table_list)
    table_get = table_subparsers.add_parser("get", help="Get one table")
    add_database_id(table_get)
    add_table_oid(table_get)
    table_get.add_argument("--metadata", action="store_true", help="Use tables.get_with_metadata")
    table_get.set_defaults(func=handle_table_get)
    table_create = table_subparsers.add_parser("create", help="Create a table")
    add_database_id(table_create)
    add_schema_oid(table_create)
    table_create.add_argument("name", help="Table name")
    table_create.add_argument("--primary-key", help="JSON object for pkey_column_info")
    table_create.add_argument("--columns", help="JSON array for column_data_list")
    table_create.add_argument("--constraints", help="JSON array for constraint_data_list")
    table_create.add_argument("--owner-oid", type=int)
    table_create.add_argument("--comment")
    table_create.set_defaults(func=handle_table_create)
    table_delete = table_subparsers.add_parser("delete", help="Delete a table")
    add_database_id(table_delete)
    add_table_oid(table_delete)
    table_delete.add_argument("--cascade", action="store_true", help="Drop dependent objects too")
    table_delete.set_defaults(func=handle_table_delete)
    table_patch = table_subparsers.add_parser("patch", help="Rename a table, edit description, or alter columns")
    add_database_id(table_patch)
    add_table_oid(table_patch)
    table_patch.add_argument("--name", help="New table name")
    table_patch.add_argument("--description", help="New table description")
    table_patch.add_argument("--columns", help="JSON array of column alterations")
    table_patch.set_defaults(func=handle_table_patch)

    column_parser = subparsers.add_parser("column", help="Manage table columns")
    column_subparsers = column_parser.add_subparsers(dest="column_command", required=True)
    column_list = column_subparsers.add_parser("list", help="List columns")
    add_database_id(column_list)
    add_table_oid(column_list)
    column_list.add_argument("--metadata", action="store_true", help="Use columns.list_with_metadata")
    column_list.set_defaults(func=handle_column_list)
    column_add = column_subparsers.add_parser("add", help="Add columns")
    add_database_id(column_add)
    add_table_oid(column_add)
    column_add.add_argument("--columns", required=True, help="JSON array for column_data_list")
    column_add.set_defaults(func=handle_column_add)
    column_patch = column_subparsers.add_parser("patch", help="Patch columns")
    add_database_id(column_patch)
    add_table_oid(column_patch)
    column_patch.add_argument("--columns", required=True, help="JSON array for column_data_list")
    column_patch.set_defaults(func=handle_column_patch)
    column_delete = column_subparsers.add_parser("delete", help="Delete columns")
    add_database_id(column_delete)
    add_table_oid(column_delete)
    column_delete.add_argument("attnums", nargs="+", type=int, help="Column attnum(s) to delete")
    column_delete.set_defaults(func=handle_column_delete)

    record_parser = subparsers.add_parser("record", help="Manage table records")
    record_subparsers = record_parser.add_subparsers(dest="record_command", required=True)
    record_list = record_subparsers.add_parser("list", help="List records")
    add_database_id(record_list)
    add_table_oid(record_list)
    record_list.add_argument("--limit", type=int)
    record_list.add_argument("--offset", type=int)
    record_list.add_argument("--order", help="JSON array for order")
    record_list.add_argument("--filter", help="JSON object for filter")
    record_list.add_argument("--grouping", help="JSON object for grouping")
    record_list.add_argument("--joined-columns", help="JSON array for joined_columns")
    record_list.add_argument("--summaries", action="store_true", help="Return record summaries")
    record_list.set_defaults(func=handle_record_list)
    record_get = record_subparsers.add_parser("get", help="Get one record by primary key")
    add_database_id(record_get)
    add_table_oid(record_get)
    record_get.add_argument("record_id", help="Primary key value, parsed as JSON when possible")
    record_get.add_argument("--summaries", action="store_true", help="Return record summaries")
    record_get.set_defaults(func=handle_record_get)
    record_add = record_subparsers.add_parser("add", help="Add one record")
    add_database_id(record_add)
    add_table_oid(record_add)
    record_add.add_argument("--data", required=True, help="JSON object keyed by column attnum")
    record_add.add_argument("--summaries", action="store_true", help="Return record summaries")
    record_add.set_defaults(func=handle_record_add)
    record_patch = record_subparsers.add_parser("patch", help="Patch one record")
    add_database_id(record_patch)
    add_table_oid(record_patch)
    record_patch.add_argument("record_id", help="Primary key value, parsed as JSON when possible")
    record_patch.add_argument("--data", required=True, help="JSON object keyed by column attnum")
    record_patch.add_argument("--summaries", action="store_true", help="Return record summaries")
    record_patch.set_defaults(func=handle_record_patch)
    record_delete = record_subparsers.add_parser("delete", help="Delete records by primary key")
    add_database_id(record_delete)
    add_table_oid(record_delete)
    record_delete.add_argument("record_ids", nargs="+", help="Primary key value(s), parsed as JSON when possible")
    record_delete.set_defaults(func=handle_record_delete)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, MathesarClientError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
