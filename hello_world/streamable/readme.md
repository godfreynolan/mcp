Set the API key as an environment variable:

```powershell
$env:OPENAI_API_KEY=""
```

Start the Streamable HTTP server:

```powershell
python server.py
```

In another terminal, run the client:

```powershell
python test_client.py
```
