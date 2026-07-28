# mcp — Mobile Data & Examples

A small collection of Python example components, demo servers, and a mobile dataset (SQLite) useful for testing integrations and exploring lightweight server/client patterns.

This repository is organized into focused subdirectories rather than a single packaged application. Each subdirectory contains small, runnable Python examples and a `requirements.txt` for the dependencies they need.

## Top-level layout

- `database/` — SQLite dataset (r_mobile.db), a small server (`server.py`), and `test_client.py`. See `database/readme.md` for details.
- `hello_world/` — two tiny example servers demonstrating different IO styles:
  - `hello_world/stdio/` — stdio-based example (server, test_client, requirements)
  - `hello_world/streamable/` — streaming example (server, test_client, requirements)
- `security/` — security-focused scripts and another copy of `r_mobile.db`; includes `server.py` and `test_client.py` with security-related processing. See `security/readme.md`.
- `zoho/` — a minimal Zoho integration script (`app_mcp.py`) and `config.py` (placeholder for credentials/configuration).

## Quick start

1. Clone the repo:

```bash
git clone https://github.com/godfreynolan/mcp.git
cd mcp
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies for the example you want to run (each subdirectory has a `requirements.txt`). For example, to run the streamable hello world:

```bash
pip install -r hello_world/streamable/requirements.txt
python3 hello_world/streamable/server.py
# in another terminal
python3 hello_world/streamable/test_client.py
```

Or run the security demo:

```bash
pip install -r security/requirements.txt
python3 security/server.py
python3 security/test_client.py
```

Notes:
- The repo includes `r_mobile.db` SQLite files in `database/` and `security/` (~2.7MB). These are local SQLite database files — no separate DB server is required.
- Check `zoho/config.py` before running `zoho/app_mcp.py`; it likely needs API keys or endpoints to be added.
- Each subdirectory contains a `readme.md` with additional, per-example details—open those for more information.

