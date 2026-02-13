# Use Ubuntu 22.04 with Python 3.10
FROM ubuntu:22.04

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install Python 3.10 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy project files from parent directory context
COPY jenkins_mcp_server/requirements.txt .
COPY jenkins_mcp_server/pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from parent directory context
COPY jenkins_mcp_server/*.py ./jenkins_mcp_server/

# Install the package
RUN pip install --upgrade pip setuptools && \
    pip install . && \
    pip install uvicorn starlette

# Create non-root user
RUN useradd -m -u 1000 jenkinsuser && \
    chown -R jenkinsuser:jenkinsuser /app
USER jenkinsuser

# Expose port 8080 for HTTP MCP service
EXPOSE 8080

# Use HTTP MCP server for remote access (EKS/Kubernetes)
# For stdio mode, override with: --entrypoint python ... -m jenkins_mcp_server.server
ENTRYPOINT ["python", "-m", "jenkins_mcp_server.http_server"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1
