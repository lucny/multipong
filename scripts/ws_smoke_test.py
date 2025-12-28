import asyncio
import json
import sys

import websockets

URL = "ws://127.0.0.1:8000/ws/auto"

async def main():
    try:
        async with websockets.connect(URL) as ws:
            # receive connected
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            if data.get("type") != "connected":
                print("Unexpected first message:", data)
                return 2
            # wait for a snapshot
            # server needs a tiny moment to start game loop; allow multiple messages
            for _ in range(10):
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                data = json.loads(msg)
                if data.get("type") == "snapshot" and "ball" in data:
                    print("SNAPSHOT_OK", int(data["ball"].get("x", 0)), int(data["ball"].get("y", 0)))
                    return 0
            print("No snapshot received in time")
            return 3
    except Exception as e:
        print("ERROR:", e)
        return 1

if __name__ == "__main__":
    # Optional: custom URL as first argument
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    rc = asyncio.run(main())
    sys.exit(rc)
