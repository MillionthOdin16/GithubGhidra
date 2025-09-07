#!/usr/bin/env python3
"""
MCP Server for Ghidra and APK Analysis
Provides reverse engineering capabilities via Model Context Protocol

Server Information:
- Name: ghidra-apk-mcp-server
- Version: 1.0.0
- Protocol: MCP 2024-11-05
- Capabilities: tools, resources
"""

import asyncio
import os
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolResult, ListResourcesResult, ListToolsResult, ReadResourceResult
)
import mcp.server.stdio
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GhidraAnalyzer:
    """Wrapper for Ghidra headless analysis"""
    
    def __init__(self, ghidra_path: str = "/opt/ghidra"):
        self.ghidra_path = ghidra_path
        self.analyzer_path = os.path.join(ghidra_path, "support", "analyzeHeadless")
        self.workspace_dir = "/app/workspace"
        self.projects_dir = "/app/projects"
        
        # Ensure directories exist
        os.makedirs(self.workspace_dir, exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
    
    async def analyze_binary(self, file_path: str, project_name: str = "analysis") -> Dict[str, Any]:
        """Analyze a binary file with Ghidra"""
        try:
            # Create unique project directory
            project_dir = os.path.join(self.projects_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Run Ghidra headless analysis
            cmd = [
                self.analyzer_path,
                project_dir,
                project_name,
                "-import", file_path,
                "-scriptPath", "/app/ghidra_scripts",
                "-postScript", "export_analysis.py",
                "-deleteProject"
            ]
            
            logger.info(f"Running Ghidra analysis: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app"
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "success": process.returncode == 0,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "return_code": process.returncode
            }
            
            # Try to read analysis results
            results_file = os.path.join(project_dir, "analysis_results.json")
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    result["analysis_data"] = json.load(f)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing binary: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class APKAnalyzer:
    """Wrapper for APK analysis tools"""
    
    async def analyze_apk(self, apk_path: str) -> Dict[str, Any]:
        """Analyze an APK file"""
        try:
            result = {}
            
            # Use aapt to get APK info
            aapt_cmd = ["aapt", "dump", "badging", apk_path]
            process = await asyncio.create_subprocess_exec(
                *aapt_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result["aapt_info"] = stdout.decode('utf-8', errors='ignore')
            else:
                result["aapt_error"] = stderr.decode('utf-8', errors='ignore')
            
            # Use androguard for detailed analysis
            try:
                from androguard.core.apk import APK
                apk = APK(apk_path)
                
                result["androguard_analysis"] = {
                    "package_name": apk.get_package(),
                    "app_name": apk.get_app_name(),
                    "version_name": apk.get_androidversion_name(),
                    "version_code": apk.get_androidversion_code(),
                    "min_sdk": apk.get_min_sdk_version(),
                    "target_sdk": apk.get_target_sdk_version(),
                    "permissions": apk.get_permissions(),
                    "activities": apk.get_activities(),
                    "services": apk.get_services(),
                    "receivers": apk.get_receivers(),
                    "providers": apk.get_providers()
                }
                
            except Exception as e:
                result["androguard_error"] = str(e)
            
            return {"success": True, "analysis": result}
            
        except Exception as e:
            logger.error(f"Error analyzing APK: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize analyzers
ghidra_analyzer = GhidraAnalyzer()
apk_analyzer = APKAnalyzer()

# Create MCP server
server = Server("ghidra-apk-mcp-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available analysis tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="analyze_binary",
                description="Analyze a binary file using Ghidra for reverse engineering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the binary file to analyze"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Name for the Ghidra project (optional)",
                            "default": "analysis"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="analyze_apk",
                description="Analyze an Android APK file for security and structure analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the APK file to analyze"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="upload_file",
                description="Upload a file for analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "Base64 encoded file content"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Name of the file"
                        }
                    },
                    "required": ["file_content", "filename"]
                }
            ),
            Tool(
                name="get_analysis_status",
                description="Get the status of running analyses",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "analyze_binary":
            file_path = arguments.get("file_path")
            project_name = arguments.get("project_name", "analysis")
            
            if not os.path.exists(file_path):
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error: File not found: {file_path}"
                    )]
                )
            
            result = await ghidra_analyzer.analyze_binary(file_path, project_name)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Ghidra Analysis Results:\n{json.dumps(result, indent=2)}"
                )]
            )
        
        elif name == "analyze_apk":
            file_path = arguments.get("file_path")
            
            if not os.path.exists(file_path):
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error: APK file not found: {file_path}"
                    )]
                )
            
            result = await apk_analyzer.analyze_apk(file_path)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"APK Analysis Results:\n{json.dumps(result, indent=2)}"
                )]
            )
        
        elif name == "upload_file":
            import base64
            file_content = arguments.get("file_content")
            filename = arguments.get("filename")
            
            # Decode and save the file
            file_data = base64.b64decode(file_content)
            file_path = os.path.join("/app/tmp", filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"File uploaded successfully: {file_path}"
                )]
            )
        
        elif name == "get_analysis_status":
            # Return status of workspace and projects
            workspace_files = os.listdir("/app/workspace") if os.path.exists("/app/workspace") else []
            project_files = os.listdir("/app/projects") if os.path.exists("/app/projects") else []
            tmp_files = os.listdir("/app/tmp") if os.path.exists("/app/tmp") else []
            
            status = {
                "workspace_files": workspace_files,
                "project_files": project_files,
                "uploaded_files": tmp_files
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Analysis Status:\n{json.dumps(status, indent=2)}"
                )]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
            )
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )]
        )

@server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """List available resources"""
    resources = []
    
    # List analysis results
    if os.path.exists("/app/projects"):
        for project_dir in os.listdir("/app/projects"):
            project_path = os.path.join("/app/projects", project_dir)
            if os.path.isdir(project_path):
                resources.append(Resource(
                    uri=f"file:///app/projects/{project_dir}",
                    name=f"Analysis Project: {project_dir}",
                    description=f"Ghidra analysis project for {project_dir}",
                    mimeType="application/json"
                ))
    
    return ListResourcesResult(resources=resources)

@server.read_resource()
async def handle_read_resource(uri: str) -> ReadResourceResult:
    """Read a resource"""
    try:
        if uri.startswith("file:///app/projects/"):
            project_name = uri.replace("file:///app/projects/", "")
            results_file = os.path.join("/app/projects", project_name, "analysis_results.json")
            
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    content = f.read()
                return ReadResourceResult(
                    contents=[TextContent(type="text", text=content)]
                )
            else:
                return ReadResourceResult(
                    contents=[TextContent(
                        type="text", 
                        text=f"No analysis results found for project: {project_name}"
                    )]
                )
        else:
            return ReadResourceResult(
                contents=[TextContent(
                    type="text", 
                    text=f"Resource not found: {uri}"
                )]
            )
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return ReadResourceResult(
            contents=[TextContent(
                type="text", 
                text=f"Error reading resource: {str(e)}"
            )]
        )

async def main():
    """Main entry point"""
    logger.info("Starting Ghidra APK MCP Server...")
    logger.info("Server capabilities: tools, resources")
    logger.info("Available tools: analyze_binary, analyze_apk, upload_file, get_analysis_status")
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ghidra-apk-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())