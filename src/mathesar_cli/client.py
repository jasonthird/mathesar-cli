from __future__ import annotations

import json
import re
from dataclasses import dataclass
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.cookiejar import CookieJar
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


class MathesarClientError(RuntimeError):
    """Base exception for client-side errors."""


class MathesarHTTPError(MathesarClientError):
    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


class MathesarRPCError(MathesarClientError):
    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        detail = f"RPC {code}: {message}"
        if data is not None:
            detail = f"{detail} ({data})"
        super().__init__(detail)
        self.code = code
        self.message = message
        self.data = data


@dataclass(frozen=True)
class MathesarConfig:
    base_url: str
    sessionid: str | None = None
    csrftoken: str | None = None
    timeout: float = 30.0


class MathesarClient:
    def __init__(self, config: MathesarConfig) -> None:
        self.config = config

    @property
    def rpc_url(self) -> str:
        return urljoin(self.config.base_url.rstrip("/") + "/", "api/rpc/v0/")

    @property
    def login_url(self) -> str:
        return urljoin(self.config.base_url.rstrip("/") + "/", "auth/login/")

    def login(self, username: str, password: str) -> MathesarConfig:
        cookie_jar = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cookie_jar))
        login_page = self._open_text(opener, Request(self.login_url, method="GET"))
        csrf_token = self._cookie_value(cookie_jar, "csrftoken") or self._csrf_from_html(login_page)
        if not csrf_token:
            raise MathesarClientError("Could not find CSRF token on login page")

        form = urlencode(
            {
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": csrf_token,
                "next": "/",
            }
        ).encode("utf-8")
        request = Request(
            self.login_url,
            data=form,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": self.login_url,
            },
            method="POST",
        )
        self._open_text(opener, request)
        sessionid = self._cookie_value(cookie_jar, "sessionid")
        csrftoken = self._cookie_value(cookie_jar, "csrftoken")
        if not sessionid or not csrftoken:
            raise MathesarClientError("Login failed: session cookies were not returned")
        return MathesarConfig(
            base_url=self.config.base_url,
            sessionid=sessionid,
            csrftoken=csrftoken,
            timeout=self.config.timeout,
        )

    def rpc(self, method: str, params: dict[str, Any] | None = None, request_id: int = 1) -> Any:
        body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        response = self._request_json("POST", self.rpc_url, body)
        if "error" in response:
            error = response["error"]
            raise MathesarRPCError(
                int(error.get("code", 0)),
                str(error.get("message", "Unknown RPC error")),
                error.get("data"),
            )
        return response.get("result")

    def list_methods(self) -> list[str]:
        result = self.rpc("system.listMethods")
        if not isinstance(result, list) or not all(isinstance(item, str) for item in result):
            raise MathesarClientError("Unexpected response from system.listMethods")
        return result

    def method_help(self, method_name: str) -> str:
        result = self.rpc("system.methodHelp", {"method_name": method_name})
        if not isinstance(result, str):
            raise MathesarClientError("Unexpected response from system.methodHelp")
        return result

    def method_signature(self, method_name: str) -> Any:
        return self.rpc("system.methodSignature", {"method_name": method_name})

    def _request_json(self, method: str, url: str, body: dict[str, Any]) -> dict[str, Any]:
        encoded_body = json.dumps(body).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        cookie_header = self._cookie_header()
        if cookie_header:
            headers["Cookie"] = cookie_header
        csrf_token = self.config.csrftoken
        if csrf_token:
            headers["X-CSRFToken"] = csrf_token
            headers["X-CSRF-Token"] = csrf_token

        request = Request(url, data=encoded_body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.config.timeout) as response:
                payload = response.read().decode("utf-8")
                status = response.status
        except HTTPError as error:
            payload = error.read().decode("utf-8", errors="replace")
            raise MathesarHTTPError(error.code, payload) from error
        except URLError as error:
            raise MathesarClientError(str(error.reason)) from error

        if status < HTTPStatus.OK or status >= HTTPStatus.MULTIPLE_CHOICES:
            raise MathesarHTTPError(status, payload)
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as error:
            raise MathesarClientError(f"Invalid JSON response: {payload}") from error
        if not isinstance(parsed, dict):
            raise MathesarClientError(f"Expected JSON object response, got {type(parsed).__name__}")
        return parsed

    def _open_text(self, opener: Any, request: Request) -> str:
        try:
            with opener.open(request, timeout=self.config.timeout) as response:
                payload = response.read().decode("utf-8", errors="replace")
                status = response.status
        except HTTPError as error:
            payload = error.read().decode("utf-8", errors="replace")
            raise MathesarHTTPError(error.code, payload) from error
        except URLError as error:
            raise MathesarClientError(str(error.reason)) from error
        if status < HTTPStatus.OK or status >= HTTPStatus.MULTIPLE_CHOICES:
            raise MathesarHTTPError(status, payload)
        return payload

    def _cookie_value(self, cookie_jar: CookieJar, name: str) -> str | None:
        for cookie in cookie_jar:
            if cookie.name == name:
                return cookie.value
        return None

    def _csrf_from_html(self, html: str) -> str | None:
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
        if match:
            return match.group(1)
        return None

    def _cookie_header(self) -> str | None:
        cookie = SimpleCookie()
        if self.config.sessionid:
            cookie["sessionid"] = self.config.sessionid
        if self.config.csrftoken:
            cookie["csrftoken"] = self.config.csrftoken
        if not cookie:
            return None
        return "; ".join(f"{key}={morsel.value}" for key, morsel in cookie.items())
