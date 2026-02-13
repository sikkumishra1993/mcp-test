#!/usr/bin/env python3
import os
import httpx
import json
from typing import Any, Dict, List, Optional

class JenkinsMCPServer:
    def __init__(self, jenkins_url: str, username: str = None, token: str = None):
        self.jenkins_url = jenkins_url.rstrip("/")
        self.auth = (username, token) if username and token else None
        self.client = httpx.Client(verify=False, timeout=30.0)
    
    async def list_jobs(self) -> List[Dict[str, Any]]:
        response = self.client.get(
            f"{self.jenkins_url}/api/json",
            auth=self.auth
        )
        response.raise_for_status()
        data = response.json()
        return data.get("jobs", [])
    
    async def get_job_info(self, job_name: str) -> Dict[str, Any]:
        response = self.client.get(
            f"{self.jenkins_url}/job/{job_name}/api/json",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    async def trigger_build(self, job_name: str, parameters: Optional[Dict] = None) -> bool:
        endpoint = f"/job/{job_name}/buildWithParameters" if parameters else f"/job/{job_name}/build"
        response = self.client.post(
            f"{self.jenkins_url}{endpoint}",
            auth=self.auth,
            data=parameters or {}
        )
        response.raise_for_status()
        return True
    
    async def get_build_status(self, job_name: str, build_number: int) -> Dict[str, Any]:
        response = self.client.get(
            f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    async def get_console_output(self, job_name: str, build_number: int) -> str:
        response = self.client.get(
            f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText",
            auth=self.auth
        )
        response.raise_for_status()
        return response.text

if __name__ == "__main__":
    jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8080")
    username = os.getenv("JENKINS_USER")
    token = os.getenv("JENKINS_TOKEN")
    
    server = JenkinsMCPServer(jenkins_url, username, token)
    print(f"Jenkins MCP Server initialized for {jenkins_url}")
