#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from server import JenkinsMCPServer

app = FastAPI(title="Jenkins MCP Server", version="1.0.0")

jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8080")
jenkins_user = os.getenv("JENKINS_USER")
jenkins_token = os.getenv("JENKINS_TOKEN")

jenkins = JenkinsMCPServer(jenkins_url, jenkins_user, jenkins_token)

class BuildTrigger(BaseModel):
    job_name: str
    parameters: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Jenkins MCP Server", "version": "1.0.0"}

@app.get("/jobs")
async def list_jobs():
    try:
        jobs = await jenkins.list_jobs()
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_name}")
async def get_job(job_name: str):
    try:
        job_info = await jenkins.get_job_info(job_name)
        return job_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/build")
async def trigger_build(build: BuildTrigger):
    try:
        await jenkins.trigger_build(build.job_name, build.parameters)
        return {"message": f"Build triggered for {build.job_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/build/{job_name}/{build_number}")
async def get_build(job_name: str, build_number: int):
    try:
        build_info = await jenkins.get_build_status(job_name, build_number)
        return build_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/console/{job_name}/{build_number}")
async def get_console(job_name: str, build_number: int):
    try:
        console = await jenkins.get_console_output(job_name, build_number)
        return {"console_output": console}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
