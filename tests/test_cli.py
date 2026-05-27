from __future__ import annotations

import argparse
import json

import pytest

from mathesar_cli.cli import friendly_method_name, html_to_text, merge_params, method_from_parts, parse_param
from mathesar_cli.client import MathesarClient, MathesarConfig
from mathesar_cli.operations import normalize_table_columns


def test_parse_param_decodes_json_values() -> None:
    assert parse_param("database_id=1") == ("database_id", 1)
    assert parse_param("enabled=true") == ("enabled", True)
    assert parse_param("name=customers") == ("name", "customers")
    assert parse_param('record={"name":"Alice"}') == ("record", {"name": "Alice"})


def test_parse_param_rejects_missing_equals() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        parse_param("database_id")


def test_merge_params_prefers_explicit_pairs() -> None:
    params = merge_params('{"database_id": 1, "limit": 10}', [("limit", 20)])
    assert params == {"database_id": 1, "limit": 20}


def test_method_from_parts_accepts_dotted_or_space_separated_names() -> None:
    assert method_from_parts(["records.list"]) == "records.list"
    assert method_from_parts(["records", "list"]) == "records.list"


def test_friendly_method_name_converts_path_to_rpc_method() -> None:
    assert friendly_method_name(["databases", "configured", "list"]) == "databases.configured.list"
    assert friendly_method_name(["schemas", "privileges", "list-direct"]) == "schemas.privileges.list_direct"


def test_html_to_text_strips_mathesar_help_markup() -> None:
    assert html_to_text("<p>Call &quot;records.list&quot;.</p><p>Args: x</p>") == 'Call "records.list".\n\nArgs: x'


def test_normalize_table_columns_accepts_simple_column_types() -> None:
    assert normalize_table_columns([{"name": "day_number", "type": "integer", "nullable": False}]) == [
        {"name": "day_number", "type": {"name": "integer", "options": {}}, "not_null": True}
    ]


def test_rpc_url_uses_mathesar_endpoint() -> None:
    client = MathesarClient(MathesarConfig(base_url="http://localhost:8000"))
    assert client.rpc_url == "http://localhost:8000/api/rpc/v0/"


def test_cookie_header_contains_session_and_csrf() -> None:
    client = MathesarClient(
        MathesarConfig(
            base_url="http://localhost:8000",
            sessionid="session-value",
            csrftoken="csrf-value",
        )
    )
    cookie = client._cookie_header()
    assert cookie is not None
    assert "sessionid=session-value" in cookie
    assert "csrftoken=csrf-value" in cookie


def test_record_argument_examples_are_json_objects() -> None:
    assert json.loads('{"1": "Alice"}') == {"1": "Alice"}
