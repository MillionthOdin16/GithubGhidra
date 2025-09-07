# GitHub Agents MCP Server Setup Guide

This guide provides comprehensive instructions for setting up and configuring the Ghidra APK MCP Server specifically for GitHub agents integration.

## Overview

The Ghidra APK MCP Server enables GitHub agents to perform reverse engineering and security analysis using:
- **Ghidra**: Binary analysis and reverse engineering
- **APK Tools**: Android application security analysis
- **Model Context Protocol**: Standardized AI agent integration

## Quick Start for GitHub Agents

### 1. MCP Configuration

Add this configuration to your GitHub agent's MCP client:

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
      "description": "Ghidra and APK analysis server for reverse engineering and security analysis"
    }
  }
}
```

### 2. GitHub Copilot Integration

For GitHub Copilot workspace integration, add to `.vscode/settings.json`:

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

### 3. NPM Installation (Optional)

For npm-based deployment:

```bash
# Install the MCP server
npm install ghidra-apk-mcp-server

# Run the server
npm start

# Or run directly
npx ghidra-apk-mcp-server
```

## Available Tools

### 1. analyze_binary
Perform reverse engineering analysis on binary files using Ghidra.

**Parameters:**
- `file_path` (string): Path to the binary file
- `project_name` (string, optional): Ghidra project name

**Output:**
- Function signatures and entry points
- String analysis
- Symbol table information
- Code structure analysis

### 2. analyze_apk
Security analysis of Android APK files.

**Parameters:**
- `file_path` (string): Path to the APK file

**Output:**
- Permissions analysis
- Activity and service enumeration
- Manifest security review
- Potential security issues

### 3. upload_file
Upload files for analysis.

**Parameters:**
- `file_content` (string): Base64-encoded file content
- `filename` (string): Name of the file

**Output:**
- Upload confirmation
- File path for analysis

### 4. get_analysis_status
Check the status of ongoing analyses.

**Parameters:** None

**Output:**
- Analysis progress
- Available results
- Error information

## GitHub Agent Usage Examples

### Example 1: Binary Malware Analysis

```python
# GitHub agent connecting to MCP server
import mcp

async def analyze_malware():
    client = mcp.Client("ghidra-apk-analyzer")
    await client.connect("stdio", ["python", "mcp_server.py"])
    
    # Upload suspicious binary
    upload_result = await client.call_tool("upload_file", {
        "file_content": base64_encoded_binary,
        "filename": "suspicious.exe"
    })
    
    # Analyze with Ghidra
    analysis = await client.call_tool("analyze_binary", {
        "file_path": "/app/tmp/suspicious.exe",
        "project_name": "malware_analysis"
    })
    
    print("Analysis Results:", analysis)
```

### Example 2: APK Security Assessment

```python
async def assess_apk_security():
    client = mcp.Client("ghidra-apk-analyzer")
    await client.connect("stdio", ["python", "mcp_server.py"])
    
    # Analyze APK for security issues
    result = await client.call_tool("analyze_apk", {
        "file_path": "/app/uploads/sample.apk"
    })
    
    print("Security Assessment:", result)
```

### Example 3: GitHub Copilot Chat Integration

When using GitHub Copilot Chat with the MCP server configured:

```
@ghidra-apk-analyzer Can you analyze this Android APK for security vulnerabilities? I've uploaded it as 'banking_app.apk' and want to check for:
1. Dangerous permissions
2. Potential data leaks
3. Insecure network communications
```

Copilot will automatically:
1. Call `analyze_apk` tool
2. Process the security analysis results
3. Provide a comprehensive security report

## Deployment Options

### Option 1: Docker Deployment

```bash
# Build the container
docker build -t ghidra-mcp-server .

# Run with MCP protocol
docker run -i --rm ghidra-mcp-server python mcp_server.py
```

### Option 2: GitHub Actions Integration

```yaml
# .github/workflows/mcp-server.yml
name: Deploy MCP Server
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy MCP Server
        run: |
          docker build -t ghidra-mcp-server .
          docker run -d -p 8080:8080 ghidra-mcp-server
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server
python mcp_server.py

# Validate configuration
python validate_mcp.py
```

## Configuration Validation

Use the included validation script to ensure proper setup:

```bash
python validate_mcp.py
```

This will check:
- ✅ MCP server configuration files
- ✅ GitHub Copilot integration settings
- ✅ Tool availability and functionality
- ✅ Docker container health

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   - Verify `.mcp.json` configuration
   - Check server executable path
   - Ensure proper environment variables

2. **Analysis Failed**
   - Verify Ghidra installation
   - Check file permissions
   - Validate input file format

3. **GitHub Copilot Connection Issues**
   - Verify `.vscode/settings.json` configuration
   - Restart VS Code
   - Check MCP server logs

### Debug Mode

Enable debug logging:

```bash
export MCP_LOG_LEVEL=DEBUG
python mcp_server.py
```

## Support

For issues and support:
- **Issues**: [GitHub Issues](https://github.com/MillionthOdin16/GithubGhidra/issues)
- **Documentation**: See `MCP_CONFIGURATION.md` and `GITHUB_COPILOT_INTEGRATION.md`
- **Validation**: Run `python validate_mcp.py` for diagnostics

## Protocol Compliance

This server implements:
- **MCP Protocol Version**: 2024-11-05
- **Supported Capabilities**: tools, resources
- **Transport**: stdio, HTTP (planned)
- **GitHub Agent Compatibility**: ✅ Full support