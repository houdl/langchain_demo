# jampp MCP server

Jampp Partner MCP server

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>

```
"mcpServers": {
  "jampp": {
    "command": "uv",
    "args": [
      "--directory",
      "./jampp",
      "run",
      "jampp"
    ]
  }
}
```

</details>

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`bun`](https://bun.sh/docs/cli/install) with this command:

```bash
bun x @modelcontextprotocol/inspector uv --directory ./ run jampp -e TEXTNOW_API_CLIENT_SECRET=your_token_here
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
