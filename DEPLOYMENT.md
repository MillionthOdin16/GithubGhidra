# GitHub MCP Server Deployment Guide

## Quick Deployment

### Option 1: GitHub Actions (Recommended)
Deploy directly from GitHub using the automated workflow:

```bash
# Trigger manual deployment
gh workflow run deploy.yml -f environment=staging

# Or deploy to production
gh workflow run deploy.yml -f environment=production
```

### Option 2: Local Docker Build
For testing and development:

```bash
# Build the image
docker build -t ghidra-mcp-server .

# Run with Docker Compose
docker compose up -d

# Or run directly
docker run -p 8000:8000 \
  -v ./workspace:/app/workspace \
  -v ./projects:/app/projects \
  -v ./tmp:/app/tmp \
  ghidra-mcp-server
```

## MCP Client Connection

### Python Example
```python
import mcp

# Connect to the MCP server
client = mcp.Client("ghidra-apk-mcp-server")
await client.connect("stdio", ["python", "mcp_server.py"])

# Use the tools
tools = await client.list_tools()
result = await client.call_tool("analyze_binary", {
    "file_path": "/path/to/binary",
    "project_name": "my_analysis"
})
```

### Available Tools
- `analyze_binary`: Ghidra binary analysis
- `analyze_apk`: Android APK analysis  
- `upload_file`: File upload for analysis
- `get_analysis_status`: Status of analyses

## GitHub Agent Integration

This MCP server is designed to work with GitHub agents. Once deployed, agents can connect to perform reverse engineering tasks automatically.

### Example Agent Usage
```yaml
# In GitHub Actions
- name: Analyze Binary
  uses: github/mcp-action@v1
  with:
    server: ghidra-apk-mcp-server
    tool: analyze_binary
    file: ${{ github.workspace }}/binary_to_analyze
```

## Security Considerations

- All analysis runs in isolated Docker containers
- Files are automatically cleaned up after analysis
- Network access is restricted in analysis containers
- All deployment actions are logged and auditable

## Monitoring and Logs

```bash
# View container logs
docker logs ghidra-mcp-server

# Monitor resource usage
docker stats ghidra-mcp-server

# Check GitHub Actions logs
gh run list --workflow=deploy.yml
```