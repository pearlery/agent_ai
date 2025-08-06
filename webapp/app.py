
from flask import Flask, render_template
from nats.aio.client import Client as NATS
import asyncio, json
from config.settings import NATS_URL, OUTPUT_SUBJECT

app = Flask(__name__)

async def fetch_latest_output():
    try:
        nc = await NATS.connect(servers=[NATS_URL])
        js = nc.jetstream()
        sub = await js.subscribe(OUTPUT_SUBJECT, durable="web_preview_agent")
        try:
            msg = await sub.next_msg(timeout=1)
            return json.loads(msg.data.decode())
        except:
            return None
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    data = asyncio.run(fetch_latest_output())
    if not data:
        return render_template("index.html", recommendation="No data available yet.", context=None)
    return render_template("index.html", recommendation=data.get("recommendation_markdown"), context=data.get("context"))
