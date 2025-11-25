from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_mcp_stdio_client(name: str, params):
    """Create a MultiServerMCPClient using stdio transport."""
    config = {
        name: {
            "transport": "stdio",
            **params,
        }
    }

    client = MultiServerMCPClient(config)

    tools = await client.get_tools()

    return client, tools

async def create_mcp_streamable_http_client(name: str, url: str):
    """Create a MultiServerMCPClient using streamable_http transport."""
    config = {
        name: {
            "transport": "streamable_http",
            "url": url,
        }
    }

    client = MultiServerMCPClient(config)

    tools = await client.get_tools()

    return tools
