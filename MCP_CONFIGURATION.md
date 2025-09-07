# MCP Server Configuration Guide

This guide explains how to configure and connect GitHub agents to the Ghidra APK MCP Server for reverse engineering and security analysis.

## Overview

The Model Context Protocol (MCP) is an open standard that enables AI agents to connect to external tools and data sources. This server provides Ghidra binary analysis and APK reverse engineering capabilities through the MCP protocol.

## Quick Configuration

### 1. MCP Client Configuration

Add the following configuration to your MCP client setup:

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GHIDRA_HOME": "/opt/ghidra",
        "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64"
      },
      "cwd": "/app",
      "description": "Ghidra and APK analysis server for reverse engineering"
    }
  }
}
```

### 2. Docker-based Configuration

For containerized deployment:

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "ghidra-mcp-server:latest",
        "python", "mcp_server.py"
      ],
      "description": "Ghidra and APK analysis server (Docker)"
    }
  }
}
```

### 3. GitHub Actions Configuration

For GitHub-hosted runners:

```json
{
  "mcpServers": {
    "ghidra-apk-analyzer": {
      "command": "gh",
      "args": [
        "api", "/repos/MillionthOdin16/GithubGhidra/actions/workflows/deploy.yml/dispatches",
        "--method", "POST",
        "--field", "ref=main"
      ],
      "description": "GitHub Actions-based MCP server"
    }
  }
}
```

## Server Capabilities

### Tools Available

1. **analyze_binary**: Ghidra-based binary reverse engineering
2. **analyze_apk**: Android APK security analysis  
3. **upload_file**: File upload with base64 encoding
4. **get_analysis_status**: Analysis status and file management

### Resources Available

- **analysis_results**: Access to Ghidra analysis outputs
- **project_files**: Ghidra project and workspace files

## Usage Examples

### Basic Connection

```python
import mcp

# Initialize MCP client
client = mcp.Client("ghidra-apk-analyzer")
await client.connect("stdio", ["python", "mcp_server.py"])

# List available tools
tools = await client.list_tools()
print("Available tools:", [tool.name for tool in tools.tools])
```

### Binary Analysis Workflow

```python
# 1. Upload binary file
upload_result = await client.call_tool("upload_file", {
    "file_content": base64.b64encode(binary_data).decode(),
    "filename": "malware_sample.exe"
})

# 2. Analyze with Ghidra
analysis_result = await client.call_tool("analyze_binary", {
    "file_path": "/app/tmp/malware_sample.exe",
    "project_name": "malware_analysis_2024"
})

# 3. Get analysis status
status = await client.call_tool("get_analysis_status", {})
```

### APK Security Analysis

```python
# 1. Upload APK
upload_result = await client.call_tool("upload_file", {
    "file_content": base64.b64encode(apk_data).decode(),
    "filename": "suspicious_app.apk"
})

# 2. Analyze APK
apk_analysis = await client.call_tool("analyze_apk", {
    "file_path": "/app/tmp/suspicious_app.apk"
})

# Parse results
analysis_data = json.loads(apk_analysis.content[0].text)
if analysis_data["success"]:
    permissions = analysis_data["analysis"]["androguard_analysis"]["permissions"]
    activities = analysis_data["analysis"]["androguard_analysis"]["activities"]
    print(f"APK has {len(permissions)} permissions and {len(activities)} activities")
```

## GitHub Agent Integration

### Copilot Configuration

To use with GitHub Copilot agents, add to your workspace configuration:

```json
{
  "mcp": {
    "servers": {
      "ghidra-analyzer": {
        "command": "python",
        "args": ["/path/to/mcp_server.py"],
        "capabilities": ["tools", "resources"]
      }
    }
  }
}
```

### Actions Workflow Integration

Create a workflow that uses the MCP server:

```yaml
name: Security Analysis
on:
  workflow_dispatch:
    inputs:
      file_url:
        description: 'URL of file to analyze'
        required: true

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup MCP Server
        run: |
          docker build -t ghidra-mcp-server .
          docker run -d --name mcp-server ghidra-mcp-server
      - name: Run Analysis
        run: |
          python -c "
          import asyncio
          import mcp
          
          async def analyze():
              client = mcp.Client('ghidra-analyzer')
              await client.connect('stdio', ['python', 'mcp_server.py'])
              result = await client.call_tool('analyze_binary', {
                  'file_path': '${{ github.event.inputs.file_url }}'
              })
              print(result)
          
          asyncio.run(analyze())
          "
```

## Environment Setup

### Docker Environment

The server requires these environment variables:

```bash
GHIDRA_HOME=/opt/ghidra
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
PYTHONPATH=/app
```

### Local Development

For local development without Docker:

```bash
# Install Ghidra
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.3_build/ghidra_11.0.3_PUBLIC_20240410.zip
unzip ghidra_11.0.3_PUBLIC_20240410.zip
export GHIDRA_HOME=$(pwd)/ghidra_11.0.3_PUBLIC

# Install dependencies
pip install -r requirements.txt

# Run server
python mcp_server.py
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify MCP client configuration
   - Check server startup logs
   - Ensure proper stdio communication

2. **Ghidra Analysis Errors**
   - Verify Java 17+ installation
   - Check Ghidra installation path
   - Review file permissions

3. **APK Analysis Failed**
   - Ensure APK file is valid
   - Check androguard installation
   - Verify AAPT availability

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run server with debug
python mcp_server.py --debug
```

### Health Check

Verify server health:

```python
async def health_check():
    client = mcp.Client("ghidra-analyzer")
    await client.connect("stdio", ["python", "mcp_server.py"])
    
    # Test basic functionality
    tools = await client.list_tools()
    assert len(tools.tools) == 4
    
    status = await client.call_tool("get_analysis_status", {})
    assert "workspace_files" in status.content[0].text
    
    print("Health check passed!")
```

## Security Considerations

- All analysis runs in isolated containers
- No persistent storage of uploaded files
- Rate limiting and file size restrictions
- GitHub Actions provide audit logs
- Regular security updates for dependencies

## Support

- **Documentation**: [GitHub Repository](https://github.com/MillionthOdin16/GithubGhidra)
- **Issues**: [GitHub Issues](https://github.com/MillionthOdin16/GithubGhidra/issues)
- **MCP Protocol**: [MCP Specification](https://modelcontextprotocol.org)