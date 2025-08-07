# apis/root.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

root_router = APIRouter()

@root_router.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Type Agent Model API</title></head>
        <body>
            <h1>Welcome to the type Agent Model API</h1>
            <p>ReadMe:</p>
            <ul>
            <li>To use normal API function, go to FastAPI Doc page</li>
            <li>Then use predict one to use the model with predictOneApi</li>
            <li>If you want to try the model via NATS chain</li>
            <li>Use open server API, then publish a message to agent-type.Input</li>
            <li>Your output will be published to agent-type.Output</li>
            <li>Keep in mind the NATS server open has to have JS available</li>
            <li>The values written here are default and can be changed in the .env file</li>
            </ul>
            <p>To visit the <a href="/docs">Swagger UI</a>.</p>
        </body>
    </html>
    """
