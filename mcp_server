from mcp.server.fastmcp import FastMCP
import requests
import os

mcp = FastMCP("fbdi-agent")

# 🔗 Your Codespaces URL
BASE_URL = "https://probable-robot-95j9g5ww5x3jpx-8080.app.github.dev"

# 🔐 session storage
SESSION_ID = "session1"


# ================= 1. CHECK SERVER =================
@mcp.tool()
def check_server():
    """Check if FastAPI server is running"""
    response = requests.get(f"{BASE_URL}/")
    return response.text


# ================= 2. LOGIN =================
@mcp.tool()
def login(url: str, username: str, password: str):
    """Login to Oracle Fusion"""

    payload = {
        "session_id": SESSION_ID,
        "url": url,
        "username": username,
        "password": password
    }

    response = requests.post(f"{BASE_URL}/login", json=payload)

    return response.json()


# ================= 3. UPLOAD FBDI =================
@mcp.tool()
def upload_fbdi(file_path: str):
    """Upload FBDI zip file"""

    files = {
        "file": open(file_path, "rb")
    }

    data = {
        "session_id": SESSION_ID
    }

    response = requests.post(
        f"{BASE_URL}/upload",
        files=files,
        data=data
    )

    return response.json()


# ================= 4. CHECK STATUS =================
@mcp.tool()
def check_status(request_id: str):
    """Check ESS job status"""

    payload = {
        "session_id": SESSION_ID,
        "request_id": request_id
    }

    response = requests.post(f"{BASE_URL}/status", json=payload)

    return response.json()


# ================= 5. BASE LOAD =================
@mcp.tool()
def base_load(ledger: str, source: str, group_id: str, parameter: str):
    """Trigger Journal Import (Base Load)"""

    payload = {
        "session_id": SESSION_ID,
        "ledger": ledger,
        "source": source,
        "group_id": group_id,
        "parameter": parameter
    }

    response = requests.post(f"{BASE_URL}/base-load", json=payload)

    return response.json()


# ================= RUN =================
if __name__ == "__main__":
    mcp.run()
