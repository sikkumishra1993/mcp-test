# Jenkins MCP Server

A Model Context Protocol (MCP) server for Jenkins automation.

## Features

- List Jenkins jobs
- Get job information
- Trigger builds with parameters
- Get build status and console output
- RESTful API interface

## Installation

Install dependencies: pip install -r requirements.txt

## Configuration

Set environment variables:
- JENKINS_URL: Jenkins server URL
- JENKINS_USER: Jenkins username
- JENKINS_TOKEN: Jenkins API token

## Usage

Run the HTTP server: uvicorn http_server:app --host 0.0.0.0 --port 8000

## Docker

Build: docker build -t jenkins-mcp-server .
Run: docker run -p 8000:8000 -e JENKINS_URL=your-url jenkins-mcp-server

## API Endpoints

- GET /jobs - List all jobs
- GET /job/{job_name} - Get job details
- POST /build - Trigger a build
- GET /build/{job_name}/{build_number} - Get build status
- GET /console/{job_name}/{build_number} - Get console output

Created by Jenkins Pipeline
