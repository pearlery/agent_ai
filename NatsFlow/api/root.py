# api/root.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

root_router = APIRouter()

@root_router.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
        <head>
            <title>Nats API</title>
        </head>
        <body>
            <h1>Welcome to the Agent API</h1>
            <p>ReadMe:</p>
            <p>This is the main entry point for interacting with the agent via Nats Using API.</p>
            <ul>
                <li>To try to test the Model via Nats services</li>
                <li>Publish the log to the model via Publish-JS</li>
                <li>For default channel use agent-type.Input for publish</li>
                <li>For checking the reply Subscribe-JS to agent-type.Output</li>
                <li>The Output can be seen in the log files in the docker folder of the NatsFlow</li>
                <li>The Output can also be view via get-lastest-messages api. Make sure to <b style="color:red;">NOT</b> set durable_name as default</li>
                <li>Ensure the NATS server has JetStream enabled for this functionality</li>
                <li>Configuration of server location can be adjusted in the .env file</li>
            <p>To visit the <a href="/docs">Swagger UI</a>.</p>
        </body>
    </html>
    """
    return html_content
