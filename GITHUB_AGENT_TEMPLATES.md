# GitHub Agent MCP Configuration Templates

This file provides ready-to-use MCP configuration templates for different GitHub agent implementations.

## Standard GitHub Agent Configuration

### Basic Configuration (.mcp.json)

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GHIDRA_HOME": "/opt/ghidra",
        "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64"
      },
      "cwd": "/app",
      "description": "Ghidra and APK analysis server for reverse engineering and security analysis"
    }
  }
}
```

### GitHub Copilot Workspace Configuration (.vscode/settings.json)

```json
{
  "extensions": {
    "github.copilot-chat": {
      "mcp": {
        "enabled": true,
        "servers": {
          "ghidra-apk-analyzer": {
            "command": "python",
            "args": ["mcp_server.py"],
            "env": {
              "GHIDRA_HOME": "/opt/ghidra",
              "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64"
            },
            "cwd": "/app",
            "description": "Ghidra and APK analysis server for reverse engineering and security analysis"
          }
        }
      }
    }
  }
}
```

### Docker-based Configuration

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/tmp/uploads:/app/tmp",
        "ghidra-mcp-server:latest",
        "python", "mcp_server.py"
      ],
      "description": "Ghidra and APK analysis server (Docker)"
    }
  }
}
```

### NPM-based Configuration

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "npx",
      "args": ["ghidra-apk-mcp-server"],
      "description": "Ghidra and APK analysis server (npm)"
    }
  }
}
```

## GitHub Actions Integration

### Workflow Configuration (.github/workflows/mcp-server.yml)

```yaml
name: MCP Server Deployment
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  deploy-mcp-server:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Validate MCP Server
        run: |
          python validate_mcp.py
      
      - name: Build Docker image
        run: |
          docker build -t ghidra-mcp-server:${{ github.sha }} .
          docker tag ghidra-mcp-server:${{ github.sha }} ghidra-mcp-server:latest
      
      - name: Deploy MCP Server
        run: |
          docker run -d \
            --name mcp-server-${{ github.run_id }} \
            -p 8080:8080 \
            ghidra-mcp-server:latest
```

## Custom Environment Configurations

### Local Development

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GHIDRA_HOME": "/usr/local/ghidra",
        "JAVA_HOME": "/usr/lib/jvm/default-java",
        "MCP_LOG_LEVEL": "DEBUG"
      },
      "cwd": ".",
      "description": "Ghidra and APK analysis server (local development)"
    }
  }
}
```

### Production Environment

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GHIDRA_HOME": "/opt/ghidra",
        "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64",
        "MCP_LOG_LEVEL": "INFO",
        "MAX_FILE_SIZE": "100MB",
        "ANALYSIS_TIMEOUT": "600"
      },
      "cwd": "/app",
      "description": "Ghidra and APK analysis server (production)"
    }
  }
}
```

### High-Security Environment

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",
        "--read-only",
        "--tmpfs", "/tmp",
        "-v", "/secure/uploads:/app/tmp:ro",
        "ghidra-mcp-server:latest",
        "python", "mcp_server.py"
      ],
      "description": "Ghidra and APK analysis server (high-security)"
    }
  }
}
```

## Agent-Specific Configurations

### GitHub Copilot Enterprise

```json
{
  "extensions": {
    "github.copilot-chat": {
      "mcp": {
        "enabled": true,
        "serverTimeout": 30000,
        "servers": {
          "ghidra-apk-analyzer": {
            "command": "python",
            "args": ["mcp_server.py"],
            "env": {
              "GHIDRA_HOME": "/opt/ghidra",
              "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64"
            },
            "cwd": "/app",
            "description": "Ghidra and APK analysis server for reverse engineering and security analysis",
            "capabilities": ["tools", "resources"],
            "timeout": 60000
          }
        }
      }
    }
  }
}
```

### Custom GitHub Agent

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "type": "local",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GHIDRA_HOME": "/opt/ghidra",
        "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64",
        "AGENT_NAME": "CustomSecurityAgent",
        "ANALYSIS_MODE": "security_focused"
      },
      "cwd": "/app",
      "description": "Ghidra and APK analysis server for reverse engineering and security analysis",
      "transport": "stdio",
      "capabilities": ["tools", "resources"],
      "tools": [
        "analyze_binary",
        "analyze_apk",
        "upload_file", 
        "get_analysis_status"
      ]
    }
  }
}
```

## Validation

To validate any configuration, run:

```bash
python validate_mcp.py
```

This will verify:
- Configuration file syntax
- Required environment variables
- Server accessibility
- Tool availability
- GitHub agent compatibility

## Usage Examples

After configuration, GitHub agents can use the server like this:

```python
# Connect to MCP server
client = mcp.Client("ghidra-apk-analyzer")
await client.connect("stdio", ["python", "mcp_server.py"])

# List available tools
tools = await client.list_tools()
print("Available tools:", [tool.name for tool in tools.tools])

# Analyze a binary
result = await client.call_tool("analyze_binary", {
    "file_path": "/app/tmp/sample.exe",
    "project_name": "security_analysis"
})

print("Analysis result:", result)
```