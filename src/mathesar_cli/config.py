from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .client import MathesarConfig


CONFIG_DIR_ENV = "MATHESAR_CLI_CONFIG_DIR"
CONFIG_FILE_NAME = "config.json"


def default_config_dir() -> Path:
    override = os.environ.get(CONFIG_DIR_ENV)
    if override:
        return Path(override).expanduser()
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config).expanduser() / "mathesar-cli"
    return Path.home() / ".config" / "mathesar-cli"


def config_path() -> Path:
    return default_config_dir() / CONFIG_FILE_NAME


def load_config(path: Path | None = None) -> dict[str, Any]:
    target = path or config_path()
    if not target.exists():
        return {}
    with target.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {target}")
    return data


def save_config(values: dict[str, Any], path: Path | None = None) -> Path:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = load_config(target)
    existing.update({key: value for key, value in values.items() if value is not None})
    with target.open("w", encoding="utf-8") as file:
        json.dump(existing, file, indent=2, sort_keys=True)
        file.write("\n")
    try:
        target.chmod(0o600)
    except PermissionError:
        pass
    return target


def build_client_config(
    *,
    url: str | None,
    sessionid: str | None,
    csrftoken: str | None,
    timeout: float,
    require_auth: bool = True,
) -> MathesarConfig:
    stored = load_config()
    base_url = url or os.environ.get("MATHESAR_URL") or stored.get("url")
    if not base_url:
        raise ValueError("Missing Mathesar URL. Set MATHESAR_URL or run `mathesar config set --url URL`.")
    resolved_sessionid = sessionid or os.environ.get("MATHESAR_SESSIONID") or stored.get("sessionid")
    resolved_csrftoken = csrftoken or os.environ.get("MATHESAR_CSRFTOKEN") or stored.get("csrftoken")
    if require_auth and not resolved_sessionid:
        raise ValueError("Missing Mathesar session. Run `mathesar --url URL login --username USERNAME`.")
    return MathesarConfig(
        base_url=base_url,
        sessionid=resolved_sessionid,
        csrftoken=resolved_csrftoken,
        timeout=timeout,
    )
