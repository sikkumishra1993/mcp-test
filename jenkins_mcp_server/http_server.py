"""
HTTP MCP Server wrapper for Jenkins operations.

This server exposes the Jenkins MCP Server over HTTP using the Streamable HTTP transport.
Exposed at /mcp-jenkins endpoint for routing with other MCP servers.
"""
import os
import sys
import json
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
import uvicorn

from jenkins_mcp_server.server import JenkinsServer


class HTTPJenkinsMCPServer:
    """HTTP wrapper for the Jenkins MCP Server."""
    
    def __init__(self, jenkins_url: str, username: str, token: str, verify_ssl: bool = True):
        self.jenkins_url = jenkins_url
        self.username = username
        self.token = token
        self.verify_ssl = verify_ssl
        self.jenkins_server = JenkinsServer(jenkins_url, username, token, verify_ssl)
        
    async def handle_mcp_request(self, request: Request) -> Response:
        """Handle MCP JSON-RPC requests over HTTP."""
        if request.method == "GET":
            return JSONResponse({
                "name": "Jenkins MCP Server",
                "version": "0.1.0",
                "transport": "Streamable HTTP",
                "endpoint": "/mcp-jenkins",
                "methods": ["POST"],
                "note": "Send JSON-RPC requests to this endpoint via POST"
            })
        
        try:
            body = await request.json()
            method = body.get("method")
            request_id = body.get("id")
            params = body.get("params", {})
            
            print(f"[Jenkins MCP Request] Method: {method}, ID: {request_id}", file=sys.stderr)
            
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "experimental": {}
                    },
                    "serverInfo": {
                        "name": "jenkins-mcp-server",
                        "version": "0.1.0"
                    }
                }
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                })
            
            elif method == "notifications/initialized":
                print(f"[Jenkins MCP] Client initialized notification received", file=sys.stderr)
                return JSONResponse({})
            
            elif method == "tools/list":
                tools = await self.jenkins_server.list_tools_handler()
                tools_list = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools_list}
                })
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                print(f"[Jenkins MCP] Calling tool: {tool_name} with args: {arguments}", file=sys.stderr)
                
                result = await self.jenkins_server.call_tool_handler(tool_name, arguments)
                
                # Convert MCP TextContent to JSON
                content = []
                for item in result:
                    content.append({
                        "type": item.type,
                        "text": item.text
                    })
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": content}
                })
            
            else:
                print(f"[Jenkins MCP] Unknown method: {method}", file=sys.stderr)
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })
        
        except Exception as e:
            print(f"[Jenkins MCP Error] {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint for Kubernetes."""
        return JSONResponse({"status": "ok"})
    
    async def readiness_check(self, request: Request) -> Response:
        """Readiness check endpoint for Kubernetes."""
        if not self.jenkins_url or not self.username or not self.token:
            return JSONResponse(
                {"status": "not ready", "reason": "Jenkins credentials not configured"},
                status_code=503
            )
        return JSONResponse({"status": "ready"})
    
    async def root_handler(self, request: Request) -> Response:
        """Root endpoint with server information."""
        host = request.headers.get("host", "localhost:8080")
        scheme = "https" if request.headers.get("x-forwarded-proto") == "https" else "http"
        
        return JSONResponse({
            "name": "Jenkins MCP Server",
            "version": "0.1.0",
            "protocol": "MCP Streamable HTTP",
            "status": "running",
            "jenkins_url": self.jenkins_url,
            "mcp_endpoint": "/mcp-jenkins",
            "mcp_url": f"{scheme}://{host}/mcp-jenkins",
            "health_check": "/health",
            "readiness_check": "/readiness",
            "vs_code_config": {
                "mcp": {
                    "servers": {
                        "jenkins": {
                            "type": "http",
                            "url": f"{scheme}://{host}/mcp-jenkins"
                        }
                    }
                }
            }
        })


def create_app(jenkins_url: str, username: str, token: str, verify_ssl: bool = True) -> Starlette:
    """Create the Starlette application."""
    server = HTTPJenkinsMCPServer(jenkins_url, username, token, verify_ssl)
    
    app = Starlette(
        routes=[
            Route("/", server.root_handler, methods=["GET"]),
            Route("/mcp-jenkins", server.handle_mcp_request, methods=["GET", "POST"]),
            Route("/health", server.health_check, methods=["GET"]),
            Route("/readiness", server.readiness_check, methods=["GET"]),
        ]
    )
    
    return app


def main():
    """Main entry point for HTTP MCP server."""
    jenkins_url = os.environ.get("JENKINS_URL")
    username = os.environ.get("JENKINS_USERNAME")
    token = os.environ.get("JENKINS_TOKEN")
    verify_ssl = os.environ.get("JENKINS_VERIFY_SSL", "true").lower() == "true"
    
    if not jenkins_url or not username or not token:
        print("ERROR: JENKINS_URL, JENKINS_USERNAME, and JENKINS_TOKEN must be set.", file=sys.stderr)
        sys.exit(1)
    
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    
    print(f"Starting Jenkins MCP Server with Streamable HTTP transport...", file=sys.stderr)
    print(f"Jenkins URL: {jenkins_url}", file=sys.stderr)
    print(f"SSL Verification: {verify_ssl}", file=sys.stderr)
    print(f"Listening on: {host}:{port}", file=sys.stderr)
    print(f"MCP endpoint: http://{host}:{port}/mcp-jenkins", file=sys.stderr)
    print(f"Health check: http://{host}:{port}/health", file=sys.stderr)
    print(f"", file=sys.stderr)
    if not verify_ssl:
        print(f"WARNING: SSL verification is DISABLED for Jenkins connections!", file=sys.stderr)
    print(f"VS Code can connect to this server remotely!", file=sys.stderr)
    print(f"See http://{host}:{port}/ for configuration instructions.", file=sys.stderr)
    
    app = create_app(jenkins_url, username, token, verify_ssl)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
