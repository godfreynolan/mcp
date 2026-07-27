from openai import OpenAI
import config
client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.responses.create(
    model="gpt-5.6-sol",
    input=(
        "Give me the first 5 accounts from ZohoCRM with fields Account_Name"
    ),
    tools=[{
        "type": "mcp",
        "server_label": "ZohoCRM",
        "server_url": config.MCP_SERVER_URL,
        "allowed_tools": ["ZohoCRM_getRecords"],
        "require_approval": "never",
    }],
)

print(response.output_text)

