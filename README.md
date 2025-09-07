# GitHub MCP Server for Ghidra and APK Analysis

This repository provides a **complete Model Context Protocol (MCP) server** that enables GitHub agents and GitHub Copilot to perform reverse engineering and security analysis using Ghidra and APK analysis tools. Everything is pre-configured for seamless GitHub agent integration.

## 🚀 GitHub Agent Ready

**✅ Complete GitHub Agent Integration**
- Standard `.mcp.json` configuration for all GitHub agents
- GitHub Copilot workspace integration via `.vscode/settings.json`
- npm package with proper MCP metadata
- Full protocol compliance with MCP 2024-11-05
- Four production-ready tools: `analyze_binary`, `analyze_apk`, `upload_file`, `get_analysis_status`

## Features

- **🔧 Ghidra Integration**: Headless binary analysis using Ghidra's powerful reverse engineering capabilities
- **📱 APK Analysis**: Android APK decompilation and security analysis using androguard and AAPT
- **🤖 GitHub Agent Ready**: Full Model Context Protocol support for seamless GitHub agent integration
- **☁️ GitHub-Native**: Runs entirely on GitHub Actions and containers - no local setup required
- **🐳 Docker-Based**: Containerized deployment with all dependencies pre-installed
- **📚 Complete Documentation**: Everything needed for GitHub agents setup and usage

## Architecture

```
GitHub Agent/Copilot → MCP Client → MCP Server (Docker) → Ghidra/APK Tools
```

The system consists of:
1. **MCP Server**: Python-based server implementing the Model Context Protocol 2024-11-05
2. **Ghidra Backend**: Headless Ghidra installation for binary analysis
3. **APK Analysis Tools**: androguard, AAPT, and other Android analysis utilities
4. **GitHub Actions**: CI/CD pipeline for building and deploying the server

## 🎯 Quick Start for GitHub Agents

### Standard GitHub Agent Configuration

Add this to your GitHub agent's MCP configuration:

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

### GitHub Copilot Integration

Create or update `.vscode/settings.json` in your project:

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

#### Option B: Global MCP Configuration
Create `.mcp.json` in your project root:

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
    }
  }
}
```

### 2. Deploy the MCP Server

The server is automatically built and deployed via GitHub Actions:

```bash
# Trigger deployment manually
gh workflow run deploy.yml -f environment=staging
```

### 3. Connect to the MCP Server

Once configured, GitHub agents can connect to the MCP server using the standard MCP protocol:

```python
import mcp

# Connect to the MCP server
client = mcp.Client("ghidra-apk-analyzer")
await client.connect("stdio", ["python", "mcp_server.py"])

# List available tools
tools = await client.list_tools()
print("Available tools:", [tool.name for tool in tools.tools])
```

### 4. Analyze Files

#### Binary Analysis with Ghidra
```python
# Upload and analyze a binary file
result = await client.call_tool("upload_file", {
    "file_content": base64_encoded_binary,
    "filename": "sample.exe"
})

# Run Ghidra analysis
analysis = await client.call_tool("analyze_binary", {
    "file_path": "/app/tmp/sample.exe",
    "project_name": "sample_analysis"
})
```

#### APK Analysis
```python
# Upload and analyze an APK
result = await client.call_tool("upload_file", {
    "file_content": base64_encoded_apk,
    "filename": "app.apk"
})

# Run APK analysis
analysis = await client.call_tool("analyze_apk", {
    "file_path": "/app/tmp/app.apk"
})
```

## MCP Configuration Files

This repository includes comprehensive MCP configuration files:

- **`mcp-config.json`**: Standard MCP server configuration for GitHub agents
- **`mcp-manifest.json`**: Server manifest with full capability description  
- **`MCP_CONFIGURATION.md`**: Detailed configuration guide and examples

For detailed setup instructions, see [MCP Configuration Guide](./MCP_CONFIGURATION.md).

## Available Tools

The MCP server provides the following tools:

### `analyze_binary`
Analyze binary files using Ghidra's headless analyzer.

**Parameters:**
- `file_path` (string): Path to the binary file
- `project_name` (string, optional): Name for the Ghidra project

**Returns:**
- Function analysis (signatures, entry points, parameters)
- Symbol table information
- String analysis
- Program metadata

### `analyze_apk`
Analyze Android APK files for security and structure analysis.

**Parameters:**
- `file_path` (string): Path to the APK file

**Returns:**
- Package information (name, version, permissions)
- Component analysis (activities, services, receivers)
- AAPT output and manifest details
- Security-relevant findings

### `upload_file`
Upload files for analysis.

**Parameters:**
- `file_content` (string): Base64-encoded file content
- `filename` (string): Name of the file

**Returns:**
- File path for subsequent analysis

### `get_analysis_status`
Get the status of running analyses and available files.

**Returns:**
- List of workspace files
- Available project results
- Uploaded files

## GitHub Actions Workflows

### Build Workflow (`.github/workflows/build.yml`)
- Runs on every push and PR
- Tests Python code quality (flake8, black, isort)
- Builds and tests Docker image
- Uploads Docker image artifacts

### Deploy Workflow (`.github/workflows/deploy.yml`)
- Manual deployment via workflow_dispatch
- Automatic deployment on main branch changes
- Supports staging and production environments
- Creates deployment artifacts

## Docker Configuration

The system uses a Ubuntu-based Docker container with:
- OpenJDK 17 (required for Ghidra)
- Ghidra 11.0.3 (latest stable release)
- Python 3 with all required packages
- Android analysis tools (AAPT, etc.)

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server locally
python mcp_server.py

# Test with Docker
docker build -t ghidra-mcp-server .
docker run -p 8000:8000 ghidra-mcp-server
```

### Adding New Analysis Features

1. **Extend the MCP Server**: Add new tools in `mcp_server.py`
2. **Create Ghidra Scripts**: Add analysis scripts in `ghidra_scripts/`
3. **Update Documentation**: Document new tools and capabilities

### Code Quality

The project uses:
- **flake8**: Python linting
- **black**: Code formatting
- **isort**: Import sorting

Run quality checks:
```bash
flake8 mcp_server.py --max-line-length=100
black mcp_server.py
isort mcp_server.py
```

## Security Considerations

- All analysis runs in isolated Docker containers
- No persistent storage of uploaded files
- Limited network access from containers
- GitHub Actions provide audit logs for all deployments

## Requirements

### System Requirements
- GitHub repository with Actions enabled
- Docker support in GitHub Actions runners
- Python 3.11+ for local development

### Dependencies
- MCP protocol libraries
- Ghidra (automatically installed in Docker)
- androguard for APK analysis
- Various Python packages (see `requirements.txt`)

## Troubleshooting

### Common Issues

1. **Ghidra Analysis Fails**
   - Check Java version (requires OpenJDK 17+)
   - Verify file permissions in Docker container
   - Review Ghidra logs in analysis output

2. **APK Analysis Errors**
   - Ensure APK file is valid and not corrupted
   - Check androguard version compatibility
   - Verify AAPT tool availability

3. **MCP Connection Issues**
   - Verify MCP client configuration
   - Check server logs for startup errors
   - Ensure proper stdio communication setup

### Logs and Debugging

```bash
# View Docker container logs
docker logs <container_id>

# Debug MCP server startup
python mcp_server.py --debug

# Check GitHub Actions logs
gh run list --workflow=build.yml
gh run view <run_id>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Ensure code quality checks pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- National Security Agency for Ghidra
- The MCP Protocol team
- Android security research community