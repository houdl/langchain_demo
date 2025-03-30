# inmobi MCP server

Inmobi vendor/partner report

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "inmobi": {
      "command": "uv",
      "args": [
        "--directory",
        "./",
        "run",
        "inmobi"
      ],
      "env": {
        "INMOBI_CLIENT_ID": "xxx",
        "INMOBI_CLIENT_SECRET": "xxx"
      }
    }
  }
  ```
</details>

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory ./ run inmobi -e INMOBI_CLIENT_ID=xxx -e INMOBI_CLIENT_SECRET=xxx
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
