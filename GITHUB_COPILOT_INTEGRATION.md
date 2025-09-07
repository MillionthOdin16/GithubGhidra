# GitHub Copilot MCP Integration Examples

This document provides examples of how to use the Ghidra APK MCP Server with GitHub Copilot.

## Setup

1. Ensure the MCP server configuration is in your workspace `.vscode/settings.json`:

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
            "description": "Ghidra and APK analysis server for reverse engineering"
          }
        }
      }
    }
  }
}
```

2. Or add `.mcp.json` to your project root:

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
      "description": "Ghidra and APK analysis server for reverse engineering"
    }
  }
}
```

## Usage with GitHub Copilot Chat

### Example 1: Binary Analysis

**Prompt to Copilot:**
```
@ghidra-apk-analyzer Can you analyze this binary file for me? I've uploaded it as malware.exe and want to understand its function signatures and entry points.
```

**Expected MCP Calls:**
1. `analyze_binary` with file_path="/app/tmp/malware.exe"
2. `get_analysis_status` to retrieve results

### Example 2: APK Security Analysis  

**Prompt to Copilot:**
```
@ghidra-apk-analyzer Please analyze this Android APK for security issues. Check for dangerous permissions and potential malware indicators.
```

**Expected MCP Calls:**
1. `upload_file` to upload the APK
2. `analyze_apk` to perform security analysis
3. `get_analysis_status` to get detailed results

### Example 3: Workflow Integration

**Prompt to Copilot:**
```
@ghidra-apk-analyzer I have a suspicious Android app. Can you:
1. Upload the APK file 
2. Analyze it for security issues
3. Generate a summary report of findings

The APK is at /path/to/suspicious_app.apk
```

## Available Tools

### 1. analyze_binary
- **Purpose**: Reverse engineer binary files using Ghidra
- **Input**: file_path, project_name (optional)
- **Output**: Function signatures, entry points, strings, symbols

### 2. analyze_apk  
- **Purpose**: Security analysis of Android APK files
- **Input**: file_path
- **Output**: Permissions, activities, services, manifest analysis

### 3. upload_file
- **Purpose**: Upload files for analysis
- **Input**: file_content (base64), filename
- **Output**: Confirmation and file path

### 4. get_analysis_status
- **Purpose**: Check analysis progress and results
- **Input**: None
- **Output**: Status of all analyses and available files

## Integration Tips

1. **File Uploads**: Use the upload_file tool first for any binary or APK analysis
2. **Project Naming**: Use descriptive project names for Ghidra analysis
3. **Status Checking**: Always check analysis status after running tools
4. **Error Handling**: The server provides detailed error messages for troubleshooting

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   - Verify `.mcp.json` or `.vscode/settings.json` configuration
   - Check that the server is running in Docker

2. **Analysis Failed**
   - Ensure file exists and is accessible
   - Check Ghidra installation in container
   - Verify Java environment variables

3. **Permission Errors**
   - Make sure Docker container has proper file permissions
   - Check that uploaded files are in the correct directory

### Debug Commands

Enable debug logging by setting environment variable:
```bash
export MCP_LOG_LEVEL=DEBUG
```

Check server health:
```python
# Use get_analysis_status to verify server is working
await client.call_tool("get_analysis_status", {})
```