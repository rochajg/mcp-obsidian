# MCP server for Obsidian

MCP server to interact with Obsidian via the Local REST API community plugin.

<a href="https://glama.ai/mcp/servers/3wko1bhuek"><img width="380" height="200" src="https://glama.ai/mcp/servers/3wko1bhuek/badge" alt="server for Obsidian MCP server" /></a>

## Server Modes

This server can run in two modes:

1. **STDIO Mode (default)**: For local MCP protocol communication via stdin/stdout
2. **HTTP Mode**: For external communication via HTTP REST API

## Components

### Tools

The server implements multiple tools to interact with Obsidian:

- list_files_in_vault: Lists all files and directories in the root directory of your Obsidian vault
- list_files_in_dir: Lists all files and directories in a specific Obsidian directory
- get_file_contents: Return the content of a single file in your vault.
- search: Search for documents matching a specified text query across all files in the vault
- patch_content: Insert content into an existing note relative to a heading, block reference, or frontmatter field.
- append_content: Append content to a new or existing file in the vault.
- delete_file: Delete a file or directory from your vault.

### Example prompts

Its good to first instruct Claude to use Obsidian. Then it will always call the tool.

The use prompts like this:
- Get the contents of the last architecture call note and summarize them
- Search for all files where Azure CosmosDb is mentioned and quickly explain to me the context in which it is mentioned
- Summarize the last meeting notes and put them into a new note 'summary meeting.md'. Add an introduction so that I can send it via email.

## Configuration

### Obsidian REST API Key

There are two ways to configure the environment with the Obsidian REST API Key. 

1. Add to server config (preferred for STDIO mode)

```json
{
  "mcp-obsidian": {
    "command": "uvx",
    "args": [
      "mcp-obsidian"
    ],
    "env": {
      "OBSIDIAN_API_KEY": "<your_api_key_here>",
      "OBSIDIAN_HOST": "<your_obsidian_host>",
      "OBSIDIAN_PORT": "<your_obsidian_port>"
    }
  }
}
```
Sometimes Claude has issues detecting the location of uv / uvx. You can use `which uvx` to find and paste the full path in above config in such cases.

2. Create a `.env` file in the working directory with the following required variables:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=your_obsidian_host
OBSIDIAN_PORT=your_obsidian_port
```

Note:
- You can find the API key in the Obsidian plugin config
- Default port is 27124 if not specified
- Default host is 127.0.0.1 if not specified

### HTTP Server Configuration (Optional)

For HTTP mode, additional environment variables are available:

```
MCP_HTTP_HOST=0.0.0.0
MCP_HTTP_PORT=8000
MCP_HTTP_API_KEY=your_secure_api_key_here
```

Note:
- `MCP_HTTP_HOST`: Host to bind the HTTP server (default: 0.0.0.0)
- `MCP_HTTP_PORT`: Port for the HTTP server (default: 8000)
- `MCP_HTTP_API_KEY`: Optional API key for authentication. If not set, server accepts all requests

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the api key.

### Running HTTP Server

To run the server in HTTP mode for external communication:

```bash
# Install dependencies
uv sync

# Set environment variables
export OBSIDIAN_API_KEY=your_api_key_here
export OBSIDIAN_HOST=your_obsidian_host
export OBSIDIAN_PORT=your_obsidian_port
export MCP_HTTP_API_KEY=your_secure_api_key

# Run HTTP server
uv run mcp-obsidian-http
```

Or using uvx (published version):

```bash
uvx mcp-obsidian-http
```

The HTTP server will start on `http://0.0.0.0:8000` by default.

#### HTTP API Endpoints

- `GET /`: Server information
- `GET /health`: Health check
- `GET /tools`: List available tools (requires authentication)
- `POST /tools/call`: Call a tool (requires authentication)

#### Example HTTP Request

```bash
# List tools
curl -H "Authorization: Bearer your_secure_api_key" http://localhost:8000/tools

# Call a tool
curl -X POST http://localhost:8000/tools/call \
  -H "Authorization: Bearer your_secure_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_files_in_vault",
    "arguments": {}
  }'
```

## Integration Guide

### Integrating with Your Application

The HTTP server provides a REST API that can be easily integrated into any application or service. Here are examples in different programming languages:

#### Python

```python
import requests

class ObsidianMCPClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def list_tools(self):
        response = requests.get(f"{self.base_url}/tools", headers=self.headers)
        return response.json()
    
    def call_tool(self, tool_name: str, arguments: dict):
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        response = requests.post(
            f"{self.base_url}/tools/call",
            headers=self.headers,
            json=payload
        )
        return response.json()

# Usage
client = ObsidianMCPClient("http://localhost:8000", "your_api_key")

# List all files in vault
result = client.call_tool("obsidian_list_files_in_vault", {})
print(result)

# Search for content
result = client.call_tool("obsidian_simple_search", {"query": "meeting notes"})
print(result)

# Get file contents
result = client.call_tool("obsidian_get_file_contents", {"filepath": "notes/daily.md"})
print(result)
```

#### JavaScript/TypeScript

```typescript
class ObsidianMCPClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  async listTools() {
    const response = await fetch(`${this.baseUrl}/tools`, {
      headers: this.getHeaders(),
    });
    return response.json();
  }

  async callTool(toolName: string, args: Record<string, any>) {
    const response = await fetch(`${this.baseUrl}/tools/call`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        name: toolName,
        arguments: args,
      }),
    });
    return response.json();
  }
}

// Usage
const client = new ObsidianMCPClient('http://localhost:8000', 'your_api_key');

// List all files
const files = await client.callTool('obsidian_list_files_in_vault', {});
console.log(files);

// Search
const searchResults = await client.callTool('obsidian_simple_search', {
  query: 'project documentation'
});
console.log(searchResults);
```

#### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

type ObsidianMCPClient struct {
    BaseURL string
    APIKey  string
    Client  *http.Client
}

type ToolCallRequest struct {
    Name      string                 `json:"name"`
    Arguments map[string]interface{} `json:"arguments"`
}

type ToolCallResponse struct {
    Success bool                     `json:"success"`
    Result  []map[string]interface{} `json:"result,omitempty"`
    Error   string                   `json:"error,omitempty"`
}

func NewObsidianMCPClient(baseURL, apiKey string) *ObsidianMCPClient {
    return &ObsidianMCPClient{
        BaseURL: baseURL,
        APIKey:  apiKey,
        Client:  &http.Client{},
    }
}

func (c *ObsidianMCPClient) CallTool(toolName string, args map[string]interface{}) (*ToolCallResponse, error) {
    payload := ToolCallRequest{
        Name:      toolName,
        Arguments: args,
    }
    
    jsonData, err := json.Marshal(payload)
    if err != nil {
        return nil, err
    }
    
    req, err := http.NewRequest("POST", c.BaseURL+"/tools/call", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }
    
    req.Header.Set("Authorization", "Bearer "+c.APIKey)
    req.Header.Set("Content-Type", "application/json")
    
    resp, err := c.Client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }
    
    var result ToolCallResponse
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, err
    }
    
    return &result, nil
}

func main() {
    client := NewObsidianMCPClient("http://localhost:8000", "your_api_key")
    
    // List files
    result, err := client.CallTool("obsidian_list_files_in_vault", map[string]interface{}{})
    if err != nil {
        panic(err)
    }
    
    fmt.Printf("Success: %v\n", result.Success)
    fmt.Printf("Result: %v\n", result.Result)
}
```

### Common Use Cases

#### Automated Note Creation

```python
# Create a daily note with a template
client.call_tool("obsidian_append_content", {
    "filepath": "Daily/2024-01-06.md",
    "content": "# Daily Note\n\n## Tasks\n- [ ] Review emails\n- [ ] Team meeting\n\n## Notes\n"
})
```

#### Search and Aggregate Information

```python
# Search for all meeting notes and aggregate
results = client.call_tool("obsidian_simple_search", {
    "query": "meeting",
    "context_length": 200
})

for item in results['result']:
    print(f"Found in: {item['text']}")
```

#### Sync External Data to Obsidian

```python
# Fetch data from external API and save to Obsidian
external_data = fetch_from_external_api()

client.call_tool("obsidian_put_content", {
    "filepath": "External/data-sync.md",
    "content": f"# Data Sync\n\nLast updated: {datetime.now()}\n\n{external_data}"
})
```

#### Webhook Integration

```python
from flask import Flask, request

app = Flask(__name__)
obsidian_client = ObsidianMCPClient("http://localhost:8000", "your_api_key")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Save webhook data to Obsidian
    obsidian_client.call_tool("obsidian_append_content", {
        "filepath": "Webhooks/log.md",
        "content": f"\n\n## {datetime.now()}\n{json.dumps(data, indent=2)}"
    })
    
    return {"status": "saved"}
```

### Authentication

All API endpoints (except `/health` and `/`) require Bearer token authentication. Include your API key in the `Authorization` header:

```
Authorization: Bearer your_secure_api_key
```

Set the `MCP_HTTP_API_KEY` environment variable when starting the server. If not set, the server will accept all requests (not recommended for production).

### Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Request successful
- `401 Unauthorized` - Invalid or missing API key
- `404 Not Found` - Tool not found
- `500 Internal Server Error` - Server error

Response format for errors:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### Using with ChatGPT and Other LLMs

The HTTP server can be integrated with ChatGPT Custom GPTs and other LLMs that support MCP over HTTP.

#### ChatGPT Custom GPT Configuration

When creating a Custom GPT or configuring an Action in ChatGPT:

1. **Name**: `Obsidian MCP Server` (or your preferred name)

2. **Description**: 
   ```
   Connects to your Obsidian vault via MCP server to read, search, and manage notes.
   ```

3. **MCP Server URL** (SSE endpoint): 
   ```
   https://obsidian-api.rochajg.dev:443/sse
   ```
   
   **Important**: ChatGPT requires the SSE endpoint (`/sse`), not the root URL. This endpoint implements the MCP protocol over Server-Sent Events.

4. **Authentication**: 
   - Select **Bearer Token** (if using API key authentication)
   - Token: Your `MCP_HTTP_API_KEY` value
   
   **Note**: If you're not using authentication (not recommended for public endpoints), you can skip this.

5. **How It Works**:
   
   The server provides two types of endpoints:
   
   **A) MCP Protocol (for ChatGPT and MCP clients)**:
   - `GET /sse` - Server-Sent Events stream for MCP communication
   - `POST /messages` - Receives client messages (used automatically by MCP protocol)
   
   ChatGPT will use these endpoints to communicate via the standard MCP protocol and automatically discover all available tools.
   
   **B) REST API (for custom integrations)**:
   - `GET /tools` - List available tools
   - `POST /tools/call` - Call a specific tool
   
   These REST endpoints are for custom integrations (see Integration Guide section below).

#### OpenAPI Schema (Optional)

For better integration with platforms that support OpenAPI/Swagger, the server provides automatic schema generation via FastAPI:

- **OpenAPI JSON**: `https://obsidian-api.rochajg.dev:443/openapi.json`
- **Interactive Docs**: `https://obsidian-api.rochajg.dev:443/docs`
- **ReDoc**: `https://obsidian-api.rochajg.dev:443/redoc`

You can import the OpenAPI schema directly into ChatGPT Actions or other platforms for automatic configuration.

#### Example ChatGPT Instructions

Add these instructions to your Custom GPT to help it understand how to use the tools:

```
You have access to an Obsidian MCP server that can interact with the user's Obsidian vault.

Available capabilities:
- List and browse files in the vault
- Search for content across all notes
- Read file contents
- Create and update notes
- Append content to existing notes
- Delete files

When the user asks about their notes or wants to manage their Obsidian vault:
1. Use the appropriate tool based on their request
2. Always show the results in a clear, formatted way
3. For search results, summarize what you found and offer to show more details
4. Before modifying files, confirm the action with the user

Be proactive in suggesting ways to organize or search their notes.
```

#### Security Considerations for Public Endpoints

If exposing your MCP server publicly (like `https://obsidian-api.rochajg.dev:443`):

1. **Always use HTTPS** (SSL/TLS certificate required)
2. **Enable strong authentication** with `MCP_HTTP_API_KEY`
3. **Use a strong, randomly generated API key**:
   ```bash
   # Generate a secure API key
   openssl rand -hex 32
   ```
4. **Consider IP whitelisting** at your reverse proxy/firewall level
5. **Monitor access logs** for suspicious activity
6. **Rate limiting** - Configure at your reverse proxy (nginx, caddy, etc.)

#### Reverse Proxy Configuration (nginx example)

If using nginx as reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name obsidian-api.rochajg.dev;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=10r/s;
    limit_req zone=mcp_limit burst=20 nodelay;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (adjust as needed)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }
}
```

#### Testing the Configuration

Before configuring in ChatGPT, test your endpoints:

```bash
# Test health check (no auth required)
curl https://obsidian-api.rochajg.dev:443/health

# Test SSE endpoint (MCP protocol - ChatGPT uses this)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Accept: text/event-stream" \
     https://obsidian-api.rochajg.dev:443/sse

# Test REST API endpoints (for custom integrations)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://obsidian-api.rochajg.dev:443/tools

curl -X POST https://obsidian-api.rochajg.dev:443/tools/call \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"name": "obsidian_list_files_in_vault", "arguments": {}}'
```

**Note**: The SSE endpoint will maintain an open connection and stream events. This is the endpoint ChatGPT uses for MCP communication.

### Running with Docker

To run the HTTP server alongside your Obsidian instance using Docker:

#### Prerequisites

- Docker and Docker Compose installed
- Obsidian running in Docker with REST API plugin enabled
- Both containers on the same Docker network

#### Using Pre-built Image from GitHub Container Registry

The easiest way to run the server is using the pre-built image:

```bash
docker run -d \
  --name mcp-obsidian-http \
  --network obsidian-network \
  -p 8000:8000 \
  -e OBSIDIAN_API_KEY=your_api_key \
  -e OBSIDIAN_HOST=obsidian \
  -e OBSIDIAN_PORT=27124 \
  -e OBSIDIAN_PROTOCOL=https \
  -e MCP_HTTP_API_KEY=your_secure_api_key \
  ghcr.io/rochajg/mcp-obsidian:latest
```

Or using Docker Compose with the pre-built image, update your `docker-compose.yml`:

```yaml
services:
  mcp-obsidian-http:
    image: ghcr.io/rochajg/mcp-obsidian:latest
    container_name: mcp-obsidian-http
    # ... rest of configuration
```

Available tags:
- `latest` - Latest build from main branch
- `v*` - Specific version tags (e.g., `v0.2.1`)

#### Building from Source

If you prefer to build the image yourself:

##### Setup

1. **Create environment file:**

```bash
cp .env.docker.example .env
```

2. **Configure environment variables in `.env`:**

```env
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=obsidian  # Container name of your Obsidian instance
OBSIDIAN_PORT=27124
OBSIDIAN_PROTOCOL=https
MCP_HTTP_PORT=8000
MCP_HTTP_API_KEY=your_secure_api_key
OBSIDIAN_NETWORK=obsidian-network  # Your existing Docker network
```

3. **Build and run:**

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Network Configuration

The MCP HTTP server needs to be on the same Docker network as your Obsidian instance. The `docker-compose.yml` is configured to use an external network named `obsidian-network` by default.

If your Obsidian container uses a different network name, update the `OBSIDIAN_NETWORK` variable in your `.env` file.

#### Docker Run (Alternative)

If you prefer to use `docker run` instead of Docker Compose:

```bash
docker build -t mcp-obsidian-http .

docker run -d \
  --name mcp-obsidian-http \
  --network obsidian-network \
  -p 8000:8000 \
  -e OBSIDIAN_API_KEY=your_api_key \
  -e OBSIDIAN_HOST=obsidian \
  -e OBSIDIAN_PORT=27124 \
  -e OBSIDIAN_PROTOCOL=https \
  -e MCP_HTTP_API_KEY=your_secure_api_key \
  mcp-obsidian-http
```

#### Health Check

The container includes a health check that monitors the `/health` endpoint. Check container status:

```bash
docker ps
docker inspect mcp-obsidian-http | grep -A 10 Health
```

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/mcp-obsidian",
        "run",
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "<your_obsidian_host>",
        "OBSIDIAN_PORT": "<your_obsidian_port>"
      }
    }
  }
}
```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<YOUR_OBSIDIAN_API_KEY>",
        "OBSIDIAN_HOST": "<your_obsidian_host>",
        "OBSIDIAN_PORT": "<your_obsidian_port>"
      }
    }
  }
}
```
</details>

## Development

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-obsidian run mcp-obsidian
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-obsidian.log
```
