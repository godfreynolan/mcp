"""An MCP server that exposes recent customer calls from r_mobile.db."""

import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("r-mobile")
DATABASE_PATH = Path(__file__).with_name("r_mobile.db").resolve()


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
    with sqlite3.connect(database_uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row

        matches: list[sqlite3.Row]
        if customer.isdigit():
            matches = connection.execute(
                """
                SELECT customer_id, full_name, email, phone_number
                FROM customers
                WHERE customer_id = ?
                """,
                (int(customer),),
            ).fetchall()
        else:
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

            if not matches:
                pattern = f"%{customer}%"
                matches = connection.execute(
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

        if not matches:
            return {"error": f"No customer matched {customer!r}."}

        if len(matches) > 1:
            visible_matches = [dict(row) for row in matches[:10]]
            return {
                "error": "The customer reference is ambiguous. Ask the user to choose one.",
                "matches": visible_matches,
                "more_matches_exist": len(matches) > 10,
            }

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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
