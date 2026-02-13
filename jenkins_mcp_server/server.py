"""
Jenkins MCP Server - stdio mode
"""
import os
import sys
import json
from typing import Any
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


class JenkinsServer:
    """Jenkins MCP Server implementation."""
    
    def __init__(self, jenkins_url: str, username: str, token: str, verify_ssl: bool = True):
        self.jenkins_url = jenkins_url.rstrip('/')
        self.username = username
        self.token = token
        self.auth = (username, token)
        self.verify_ssl = verify_ssl
        self.server = Server("jenkins-mcp-server")
        
        self.server.list_tools()(self.list_tools_handler)
        self.server.call_tool()(self.call_tool_handler)
    
    async def list_tools_handler(self) -> list[Tool]:
        """List available Jenkins tools."""
        return [
            Tool(
                name="list_jobs",
                description="List all Jenkins jobs",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="create_job",
                description="Create a new Jenkins job with XML configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the new Jenkins job"
                        },
                        "config_xml": {
                            "type": "string",
                            "description": "XML configuration for the job"
                        }
                    },
                    "required": ["job_name", "config_xml"]
                }
            ),
            Tool(
                name="update_job",
                description="Update/edit a Jenkins job's XML configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job to update"
                        },
                        "config_xml": {
                            "type": "string",
                            "description": "New XML configuration for the job"
                        }
                    },
                    "required": ["job_name", "config_xml"]
                }
            ),
            Tool(
                name="delete_job",
                description="Delete a Jenkins job",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job to delete"
                        }
                    },
                    "required": ["job_name"]
                }
            ),
            Tool(
                name="trigger_build",
                description="Trigger a build for a Jenkins job with optional parameters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Build parameters (optional)",
                            "additionalProperties": True
                        }
                    },
                    "required": ["job_name"]
                }
            ),
            Tool(
                name="get_build_status",
                description="Get the status of a specific build",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job"
                        },
                        "build_number": {
                            "type": "integer",
                            "description": "Build number"
                        }
                    },
                    "required": ["job_name", "build_number"]
                }
            ),
            Tool(
                name="get_last_build",
                description="Get information about the last build of a job",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job"
                        }
                    },
                    "required": ["job_name"]
                }
            ),
            Tool(
                name="get_build_console",
                description="Get console output of a specific build",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job"
                        },
                        "build_number": {
                            "type": "integer",
                            "description": "Build number"
                        }
                    },
                    "required": ["job_name", "build_number"]
                }
            ),
            Tool(
                name="stop_build",
                description="Stop a running build",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_name": {
                            "type": "string",
                            "description": "Name of the Jenkins job"
                        },
                        "build_number": {
                            "type": "integer",
                            "description": "Build number"
                        }
                    },
                    "required": ["job_name", "build_number"]
                }
            )
        ]
