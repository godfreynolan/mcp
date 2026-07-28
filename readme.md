# R Mobile customer-call MCP example

This example exposes `r_mobile.db` through MCP tools. You can retrieve the five
most recent calls for a customer or change a customer's email address.
Customers can be identified by customer ID, full name, email address, or phone
number.

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Set the API key as an environment variable:

```powershell
$env:OPENAI_API_KEY="your-key"
```

Create two different strong secrets. Keep the admin token only on machines or
with people who are allowed to change customer records:

```powershell
$env:RMOBILE_ADMIN_TOKEN="replace-with-a-random-secret-at-least-32-characters"
$env:RMOBILE_READ_TOKEN="replace-with-a-different-random-secret"
```

Start the Streamable HTTP server:

```powershell
python server.py
```

In another terminal, choose the access level for the client. A read-only
client can retrieve calls but cannot change email addresses:

```powershell
$env:RMOBILE_MCP_TOKEN="the-value-of-RMOBILE_READ_TOKEN"
python test_client.py
```

An administrator can retrieve calls and change email addresses:

```powershell
$env:RMOBILE_MCP_TOKEN="the-value-of-RMOBILE_ADMIN_TOKEN"
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

To update an email address, ask:

```text
Change Jasmine Hughes's email address to jasmine.hughes@example.com
```

If a name is ambiguous, the agent will ask you to choose the intended
customer.

The tokens are sent in the MCP HTTP `Authorization` header and are never
included in the question sent to the model. The server refuses to start when
the admin token is missing, either configured token is too short, or the two
tokens are identical.
