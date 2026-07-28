# R Mobile customer-call MCP example

This example exposes `r_mobile.db` through a read-only MCP tool. The tool
returns the five most recent calls for a customer identified by customer ID,
full name, email address, or phone number.

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Set the API key as an environment variable:

```powershell
$env:OPENAI_API_KEY="your-key"
```

Start the Streamable HTTP server:

```powershell
python server.py
```

In another terminal, run the client:

```powershell
python test_client.py
```

Then ask a question such as:

```text
What are the 5 most recent calls for Jasmine Hughes?
```

You can also provide the question directly:

```powershell
python test_client.py "Show me the 5 most recent calls for customer 1"
```

If a name is ambiguous, the agent will ask you to choose the intended
customer.
