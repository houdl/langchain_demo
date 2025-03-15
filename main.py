from contextlib import asynccontextmanager
from fastapi import FastAPI
from chainlit.utils import mount_chainlit
import mcp_client as mcp_client

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: setup code here
    # start mcp servers
    mcp_client_instance = mcp_client.create_mcp_client()
    await mcp_client_instance.__aenter__()
    app.state.mcp_client = mcp_client_instance
    app.state.mcp_tools = mcp_client_instance.get_tools()
    yield
    # Shutdown: cleanup code here (if any)
    await app.state.mcp_client.__aexit__(None, None, None)

app = FastAPI(title="DEMO API", lifespan=lifespan)

# Initialize MCP client reference
mcp_client.initialize_app_reference(app)

@app.get("/")
def read_main():
    return {"message": "Hello World from main app"}

mount_chainlit(app=app, target="chainlit_app.py", path="/chainlit")