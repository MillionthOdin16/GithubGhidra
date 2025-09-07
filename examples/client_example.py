#!/usr/bin/env python3
"""
Example MCP Client for Ghidra and APK Analysis
Demonstrates how to connect to the MCP server and perform analysis
"""

import asyncio
import base64
import json

class MCPClient:
    """Simplified MCP client for demonstration"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.connected = False
    
    async def connect(self, transport: str, command: list):
        """Connect to the MCP server"""
        print(f"Connecting to {self.server_name} via {transport}...")
        self.connected = True
        return True
    
    async def list_tools(self):
        """List available tools"""
        return {
            "tools": [
                {
                    "name": "analyze_binary",
                    "description": "Analyze a binary file using Ghidra"
                },
                {
                    "name": "analyze_apk", 
                    "description": "Analyze an Android APK file"
                },
                {
                    "name": "upload_file",
                    "description": "Upload a file for analysis"
                }
            ]
        }
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a tool with arguments"""
        print(f"Calling tool: {tool_name}")
        
        # Simulate tool responses
        if tool_name == "upload_file":
            return {"content": [{"type": "text", "text": f"File uploaded: {arguments['filename']}"}]}
        elif tool_name == "analyze_binary":
            return {"content": [{"type": "text", "text": "Binary analysis completed with Ghidra"}]}
        elif tool_name == "analyze_apk":
            return {"content": [{"type": "text", "text": "APK analysis completed"}]}

async def main():
    """Example usage of the MCP client"""
    print("GitHub MCP Server Example")
    print("=" * 30)
    
    client = MCPClient("ghidra-apk-mcp-server")
    await client.connect("stdio", ["python", "mcp_server.py"])
    
    # List tools
    tools = await client.list_tools()
    print("Available tools:")
    for tool in tools["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Example binary analysis
    print("\n=== Binary Analysis ===")
    await client.call_tool("upload_file", {"filename": "sample.exe", "file_content": "..."})
    await client.call_tool("analyze_binary", {"file_path": "/app/tmp/sample.exe"})
    
    # Example APK analysis  
    print("\n=== APK Analysis ===")
    await client.call_tool("upload_file", {"filename": "app.apk", "file_content": "..."})
    await client.call_tool("analyze_apk", {"file_path": "/app/tmp/app.apk"})

if __name__ == "__main__":
    asyncio.run(main())