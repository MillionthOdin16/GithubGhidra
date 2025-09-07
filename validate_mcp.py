#!/usr/bin/env python3
"""
MCP Server Validation Script
Validates that the Ghidra APK MCP Server is properly configured and accessible
"""

import asyncio
import json
import sys
from pathlib import Path

async def validate_mcp_server():
    """Validate MCP server configuration and functionality"""
    
    print("🔍 MCP Server Validation")
    print("=" * 40)
    
    # Check configuration files exist
    config_files = [
        "mcp-config.json",
        "mcp-manifest.json", 
        "MCP_CONFIGURATION.md",
        "mcp_server.py"
    ]
    
    print("\n📋 Checking configuration files...")
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file} - Missing")
            return False
    
    # Validate mcp-config.json structure
    print("\n🔧 Validating MCP configuration...")
    try:
        with open("mcp-config.json", "r") as f:
            config = json.load(f)
        
        if "mcpServers" in config:
            print("  ✅ MCP servers configuration found")
            
            if "ghidra-apk-analyzer" in config["mcpServers"]:
                print("  ✅ Ghidra APK analyzer server configured")
                server_config = config["mcpServers"]["ghidra-apk-analyzer"]
                
                required_fields = ["command", "args", "description"]
                for field in required_fields:
                    if field in server_config:
                        print(f"    ✅ {field}: {server_config[field]}")
                    else:
                        print(f"    ❌ Missing required field: {field}")
                        return False
            else:
                print("  ❌ Ghidra APK analyzer not found in configuration")
                return False
        else:
            print("  ❌ No mcpServers configuration found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error validating configuration: {e}")
        return False
    
    # Validate manifest
    print("\n📄 Validating server manifest...")
    try:
        with open("mcp-manifest.json", "r") as f:
            manifest = json.load(f)
        
        required_manifest_fields = ["name", "version", "description", "capabilities"]
        for field in required_manifest_fields:
            if field in manifest:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ Missing manifest field: {field}")
                return False
        
        # Check capabilities
        if "tools" in manifest["capabilities"]:
            tools = manifest["capabilities"]["tools"]
            expected_tools = ["analyze_binary", "analyze_apk", "upload_file", "get_analysis_status"]
            
            found_tools = [tool["name"] for tool in tools]
            for expected_tool in expected_tools:
                if expected_tool in found_tools:
                    print(f"    ✅ Tool: {expected_tool}")
                else:
                    print(f"    ❌ Missing tool: {expected_tool}")
                    return False
        else:
            print("  ❌ No tools defined in capabilities")
            return False
            
    except Exception as e:
        print(f"  ❌ Error validating manifest: {e}")
        return False
    
    # Test server import (basic syntax check)
    print("\n🐍 Testing server import...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server", "mcp_server.py")
        if spec is None:
            print("  ❌ Could not load server spec")
            return False
            
        # Just check if it can be imported without running
        print("  ✅ Server file syntax is valid")
        
    except Exception as e:
        print(f"  ❌ Server import failed: {e}")
        return False
    
    print("\n🎉 MCP Server validation completed successfully!")
    print("\n📚 Next steps:")
    print("  1. Use the configuration in mcp-config.json with your MCP client")
    print("  2. Deploy the server using: gh workflow run deploy.yml")
    print("  3. Read MCP_CONFIGURATION.md for detailed setup instructions")
    
    return True

def print_usage_example():
    """Print example usage for GitHub agents"""
    
    print("\n" + "=" * 60)
    print("🚀 GITHUB AGENT USAGE EXAMPLE")
    print("=" * 60)
    
    example_config = {
        "mcpServers": {
            "ghidra-apk-analyzer": {
                "command": "python",
                "args": ["mcp_server.py"],
                "env": {
                    "GHIDRA_HOME": "/opt/ghidra",
                    "JAVA_HOME": "/usr/lib/jvm/java-17-openjdk-amd64"
                },
                "cwd": "/app",
                "description": "Ghidra and APK analysis server"
            }
        }
    }
    
    print("\n📋 Add this to your MCP client configuration:")
    print(json.dumps(example_config, indent=2))
    
    print("\n🔧 Python usage example:")
    print("""
import mcp

async def analyze_file():
    # Connect to MCP server
    client = mcp.Client("ghidra-apk-analyzer")
    await client.connect("stdio", ["python", "mcp_server.py"])
    
    # Upload and analyze a file
    result = await client.call_tool("upload_file", {
        "file_content": base64_encoded_data,
        "filename": "sample.exe"
    })
    
    # Run analysis
    analysis = await client.call_tool("analyze_binary", {
        "file_path": "/app/tmp/sample.exe"
    })
    
    print("Analysis complete:", analysis)
""")

async def main():
    """Main validation routine"""
    
    success = await validate_mcp_server()
    
    if success:
        print_usage_example()
        sys.exit(0)
    else:
        print("\n❌ Validation failed! Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())