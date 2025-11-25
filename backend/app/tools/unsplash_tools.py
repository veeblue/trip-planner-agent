from backend.app.utils.mcp import create_mcp_stdio_client


async def unsplash_tools():
    """Create Unsplash MCP tool client."""
    params = {
        "command": "python",
        "args": ["-m", "backend.app.mcps.unsplash_mcp"],
    }

    client, tools = await create_mcp_stdio_client("unsplash_mcp", params)

    return tools