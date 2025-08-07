from nats.aio.client import Client as NATS
from nats.js.errors import NotFoundError

async def close_jetstream_stream(nats_server_url: str, stream_name: str):
    nc = NATS()
    try:
        await nc.connect(servers=[nats_server_url])
        js = nc.jetstream()
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write("Close call on: " + stream_name + "\n")
        try:
            # Try to retrieve stream info first
            info = await js.stream_info(stream_name)
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write("found"+stream_name+"from"+ info.config.name)
        except NotFoundError:
            print(f" Stream '{stream_name}' not found.")
            return {"status": "not_found", "message": f"Stream '{stream_name}' does not exist."}

        # Try to delete the stream
        await js.delete_stream(stream_name)
        print(f"🗑️ Stream '{stream_name}' deleted successfully.")
        return {"status": "success", "message": f"Stream '{stream_name}' deleted successfully."}

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        await nc.drain()
