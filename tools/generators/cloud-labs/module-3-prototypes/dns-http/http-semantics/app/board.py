import asyncio, websockets
async def handler(ws, path=None):
    async for msg in ws:
        await ws.send("order board: " + msg)
async def main():
    async with websockets.serve(handler, "127.0.0.1", 8090):
        await asyncio.Future()
asyncio.run(main())
