"""An MCP server that exposes recent customer calls from r_mobile.db."""

import sqlite3
from contextlib import closing
from os import environ
from pathlib import Path
from re import fullmatch
from secrets import compare_digest
from typing import Any

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP


class EnvironmentTokenVerifier:
    """Grant read or admin scopes using secrets configured on the server."""

    async def verify_token(self, token: str) -> AccessToken | None:
        admin_token = environ.get("RMOBILE_ADMIN_TOKEN", "")
        read_token = environ.get("RMOBILE_READ_TOKEN", "")

        if admin_token and compare_digest(token, admin_token):
            return AccessToken(
                token=token,
                client_id="r-mobile-admin",
                scopes=["customer:read", "customer:write"],
            )
        if read_token and compare_digest(token, read_token):
            return AccessToken(
                token=token,
                client_id="r-mobile-reader",
                scopes=["customer:read"],
            )
        return None


mcp = FastMCP(
    "r-mobile",
    token_verifier=EnvironmentTokenVerifier(),
    auth=AuthSettings(
        issuer_url="http://127.0.0.1:8000",
        resource_server_url="http://127.0.0.1:8000",
        required_scopes=["customer:read"],
    ),
)
DATABASE_PATH = Path(__file__).with_name("r_mobile.db").resolve()


def _find_customers(
    connection: sqlite3.Connection,
    customer: str,
) -> list[sqlite3.Row]:
    """Resolve a customer reference to at most 11 matching records."""
    if customer.isdigit():
        return connection.execute(
            """
            SELECT customer_id, full_name, email, phone_number
            FROM customers
            WHERE customer_id = ?
            """,
            (int(customer),),
        ).fetchall()

    matches = connection.execute(
        """
        SELECT customer_id, full_name, email, phone_number
        FROM customers
        WHERE full_name = ? COLLATE NOCASE
           OR email = ? COLLATE NOCASE
           OR phone_number = ?
        ORDER BY customer_id
        LIMIT 11
        """,
        (customer, customer, customer),
    ).fetchall()

    if matches:
        return matches

    pattern = f"%{customer}%"
    return connection.execute(
        """
        SELECT customer_id, full_name, email, phone_number
        FROM customers
        WHERE full_name LIKE ? COLLATE NOCASE
           OR email LIKE ? COLLATE NOCASE
           OR phone_number LIKE ?
        ORDER BY full_name, customer_id
        LIMIT 11
        """,
        (pattern, pattern, pattern),
    ).fetchall()


def _customer_error(
    customer: str,
    matches: list[sqlite3.Row],
) -> dict[str, Any] | None:
    """Return a useful not-found or ambiguous response, if applicable."""
    if not matches:
        return {"error": f"No customer matched {customer!r}."}

    if len(matches) > 1:
        return {
            "error": "The customer reference is ambiguous. Ask the user to choose one.",
            "matches": [dict(row) for row in matches[:10]],
            "more_matches_exist": len(matches) > 10,
        }

    return None


@mcp.tool()
def get_recent_calls(customer: str) -> dict[str, Any]:
    """Return the five most recent calls for one customer.

    The customer may be identified by customer ID, full name, email address,
    or phone number. If a name or partial value matches multiple customers,
    the result lists the matches so the user can choose the intended customer.
    """
    customer = customer.strip()
    if not customer:
        return {"error": "Please provide a customer ID, name, email, or phone number."}

    database_uri = f"{DATABASE_PATH.as_uri()}?mode=ro"
    with closing(sqlite3.connect(database_uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row

        matches = _find_customers(connection, customer)
        if error := _customer_error(customer, matches):
            return error

        selected_customer = dict(matches[0])
        calls = connection.execute(
            """
            SELECT
                call_id,
                call_type,
                start_time,
                duration_seconds,
                customer_phone,
                other_party_phone,
                is_missed,
                is_roaming,
                cell_tower_city,
                cell_tower_country,
                cost_usd
            FROM call_records
            WHERE customer_id = ?
            ORDER BY datetime(start_time) DESC, call_id DESC
            LIMIT 5
            """,
            (selected_customer["customer_id"],),
        ).fetchall()

    return {
        "customer": selected_customer,
        "calls": [dict(row) for row in calls],
        "call_count": len(calls),
    }


@mcp.tool()
def update_customer_email(customer: str, new_email: str) -> dict[str, Any]:
    """Change one customer's email address.

    The customer may be identified by customer ID, full name, current email
    address, or phone number. If the reference matches multiple customers, the
    result lists them so the user can choose the intended customer.
    """
    access_token = get_access_token()
    if access_token is None or "customer:write" not in access_token.scopes:
        return {
            "error": (
                "Not authorized to update customer email addresses. "
                "Connect with an admin token."
            )
        }

    customer = customer.strip()
    new_email = new_email.strip()

    if not customer:
        return {"error": "Please provide a customer ID, name, email, or phone number."}
    if not fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", new_email):
        return {"error": f"{new_email!r} is not a valid email address."}

    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        matches = _find_customers(connection, customer)
        if error := _customer_error(customer, matches):
            return error

        selected_customer = dict(matches[0])
        old_email = selected_customer["email"]

        if old_email == new_email:
            return {
                "customer_id": selected_customer["customer_id"],
                "full_name": selected_customer["full_name"],
                "old_email": old_email,
                "new_email": new_email,
                "changed": False,
            }

        connection.execute(
            "UPDATE customers SET email = ? WHERE customer_id = ?",
            (new_email, selected_customer["customer_id"]),
        )
        connection.commit()

    return {
        "customer_id": selected_customer["customer_id"],
        "full_name": selected_customer["full_name"],
        "old_email": old_email,
        "new_email": new_email,
        "changed": True,
    }


def _validate_auth_configuration() -> None:
    """Refuse to start with missing or accidentally shared credentials."""
    admin_token = environ.get("RMOBILE_ADMIN_TOKEN", "")
    read_token = environ.get("RMOBILE_READ_TOKEN", "")

    if len(admin_token) < 32:
        raise RuntimeError(
            "Set RMOBILE_ADMIN_TOKEN to a strong secret of at least 32 characters."
        )
    if read_token and len(read_token) < 32:
        raise RuntimeError(
            "Set RMOBILE_READ_TOKEN to a strong secret of at least 32 characters."
        )
    if read_token and compare_digest(read_token, admin_token):
        raise RuntimeError("RMOBILE_READ_TOKEN must differ from RMOBILE_ADMIN_TOKEN.")


if __name__ == "__main__":
    _validate_auth_configuration()
    mcp.run(transport="streamable-http")
