# filepath: c:\shashi\learning\mcp\testing\jenkins_mcp_server\server.py
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
                    },                    "required": ["job_name", "build_number"]
                }
            )
        ]
    
    async def call_tool_handler(self, name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        if name == "list_jobs":
            return await self._list_jobs()
        elif name == "create_job":
            return await self._create_job(arguments["job_name"], arguments["config_xml"])
        elif name == "update_job":
            return await self._update_job(arguments["job_name"], arguments["config_xml"])
        elif name == "delete_job":
            return await self._delete_job(arguments["job_name"])
        elif name == "trigger_build":
            parameters = arguments.get("parameters", {})
            return await self._trigger_build(arguments["job_name"], parameters)
        elif name == "get_build_status":
            return await self._get_build_status(arguments["job_name"], arguments["build_number"])
        elif name == "get_last_build":
            return await self._get_last_build(arguments["job_name"])
        elif name == "get_build_console":
            return await self._get_build_console(arguments["job_name"], arguments["build_number"])
        elif name == "stop_build":
            return await self._stop_build(arguments["job_name"], arguments["build_number"])
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _list_jobs(self) -> list[TextContent]:
        """List all Jenkins jobs."""
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.get(
                f"{self.jenkins_url}/api/json?tree=jobs[name,color,url]",
                auth=self.auth,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get("jobs", [])
            if not jobs:
                return [TextContent(type="text", text="No jobs found in Jenkins")]
            
            result = "Jenkins Jobs:\n\n"
            for job in jobs:
                status = "🟢" if "blue" in job["color"] else "🔴" if "red" in job["color"] else "⚪"
                result += f"{status} {job['name']}\n"
                result += f"   URL: {job['url']}\n\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _create_job(self, job_name: str, config_xml: str) -> list[TextContent]:
        """Create a new Jenkins job."""
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.post(
                f"{self.jenkins_url}/createItem?name={job_name}",
                auth=self.auth,
                content=config_xml,
                headers={"Content-Type": "application/xml"},
                timeout=30.0
            )
            response.raise_for_status()
            
            result = f"✅ Job '{job_name}' created successfully!\n"
            result += f"URL: {self.jenkins_url}/job/{job_name}\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _update_job(self, job_name: str, config_xml: str) -> list[TextContent]:
        """Update a Jenkins job's XML configuration."""
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.post(
                f"{self.jenkins_url}/job/{job_name}/config.xml",
                auth=self.auth,
                content=config_xml,
                headers={"Content-Type": "application/xml"},
                timeout=30.0
            )
            response.raise_for_status()
            
            result = f"✅ Job '{job_name}' updated successfully!\n"
            result += f"URL: {self.jenkins_url}/job/{job_name}\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _delete_job(self, job_name: str) -> list[TextContent]:
        """Delete a Jenkins job."""
        async with httpx.AsyncClient(verify=self.verify_ssl, follow_redirects=True) as client:
            response = await client.post(
                f"{self.jenkins_url}/job/{job_name}/doDelete",
                auth=self.auth,
                timeout=30.0
            )
            
            # Jenkins returns 302 redirect on success, accept 2xx and 3xx as success
            if response.status_code >= 400:
                raise Exception(f"Failed to delete job: HTTP {response.status_code}")
            
            result = f"✅ Job '{job_name}' deleted successfully!\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _trigger_build(self, job_name: str, parameters: dict) -> list[TextContent]:
        """Trigger a Jenkins build."""
        async with httpx.AsyncClient(verify=self.verify_ssl, follow_redirects=True) as client:
            if parameters:
                response = await client.post(
                    f"{self.jenkins_url}/job/{job_name}/buildWithParameters",
                    auth=self.auth,
                    data=parameters,
                    timeout=30.0
                )
            else:
                response = await client.post(
                    f"{self.jenkins_url}/job/{job_name}/build",
                    auth=self.auth,
                    timeout=30.0
                )
            
            # Jenkins returns 302 redirect on success, accept 2xx and 3xx as success
            if response.status_code >= 400:
                raise Exception(f"Failed to trigger build: HTTP {response.status_code}")
            
            result = f"✅ Build triggered successfully for job: {job_name}\n"
            if parameters:
                result += f"Parameters: {json.dumps(parameters, indent=2)}\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _get_build_status(self, job_name: str, build_number: int) -> list[TextContent]:
        """Get the status of a specific build."""
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.get(
                f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json",
                auth=self.auth,
                timeout=30.0            )
            response.raise_for_status()
            data = response.json()
            
            import datetime
            result_status = data.get('result', 'IN_PROGRESS')
            status = "✅ SUCCESS" if result_status == "SUCCESS" else "❌ FAILURE" if result_status == "FAILURE" else "⏳ IN PROGRESS"
            
            result = f"Build #{data['number']} - {data['fullDisplayName']}\n"
            result += f"Status: {status}\n"
            result += f"Duration: {data['duration'] / 1000:.1f}s\n" if data.get('duration') else "Duration: Running...\n"
            result += f"URL: {data['url']}\n"
            
            if data.get('timestamp'):
                timestamp = datetime.datetime.fromtimestamp(data['timestamp'] / 1000)
                result += f"Started: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            return [TextContent(type="text", text=result)]
    
    async def _get_last_build(self, job_name: str) -> list[TextContent]:
        """Get information about the last build."""
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.get(
                f"{self.jenkins_url}/job/{job_name}/lastBuild/api/json",
                auth=self.auth,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return await self._get_build_status(job_name, data['number'])
    
    async def _get_build_console(self, job_name: str, build_number: int) -> list[TextContent]:
        """Get console output of a build."""
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.get(
                f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText",
                auth=self.auth,
                timeout=30.0
            )
            response.raise_for_status()
            console_output = response.text
            
            lines = console_output.split('\n')
            if len(lines) > 100:
                result = f"Console Output (last 100 lines of {len(lines)}):\n\n"
                result += '\n'.join(lines[-100:])
            else:
                result = f"Console Output:\n\n{console_output}"
            
            return [TextContent(type="text", text=result)]
    
    async def _stop_build(self, job_name: str, build_number: int) -> list[TextContent]:
        """Stop a running build."""
        async with httpx.AsyncClient(verify=self.verify_ssl, follow_redirects=True) as client:
            response = await client.post(
                f"{self.jenkins_url}/job/{job_name}/{build_number}/stop",
                auth=self.auth,
                timeout=30.0
            )
            
            # Jenkins returns 302 redirect on success, accept 2xx and 3xx as success
            if response.status_code >= 400:
                raise Exception(f"Failed to stop build: HTTP {response.status_code}")
            
            return [TextContent(type="text", text=f"✅ Build #{build_number} stopped for job: {job_name}")]
    
    async def run(self):
        """Run the MCP server using stdio transport."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jenkins-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


def main():
    """Main entry point."""
    import asyncio
    
    jenkins_url = os.environ.get("JENKINS_URL")
    username = os.environ.get("JENKINS_USERNAME")
    token = os.environ.get("JENKINS_TOKEN")
    verify_ssl = os.environ.get("JENKINS_VERIFY_SSL", "true").lower() == "true"
    
    if not jenkins_url or not username or not token:
        print("Error: JENKINS_URL, JENKINS_USERNAME, and JENKINS_TOKEN must be set")
        exit(1)
    
    if not verify_ssl:
        print("Warning: SSL verification is disabled for Jenkins connections", file=sys.stderr)
    
    server = JenkinsServer(jenkins_url, username, token, verify_ssl)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
