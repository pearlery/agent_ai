from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# Create an instance of APIRouter
root_router = APIRouter()

# Define the root endpoint for the landing page
@root_router.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
        <head>
            <title>Agent API</title>
        </head>
        <body>
            <h1>Welcome to the Agent API</h1>
            <p>This is the main entry point for interacting with the agent via API.</p>
            <p>You can also check the full API documentation <a href="/docs">here</a>.</p>
        </body>
    </html>
    """
    return html_content
