#!/usr/bin/python3
"""h3get URL: one HTTP/3 GET with aioquic; prints the status line, headers and body."""
import asyncio, ssl, sys
from urllib.parse import urlparse
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import DataReceived, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration

class Client(QuicConnectionProtocol):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.h3 = H3Connection(self._quic)
        self.done = asyncio.Event(); self.headers = []; self.body = b""
    def quic_event_received(self, event):
        for e in self.h3.handle_event(event):
            if isinstance(e, HeadersReceived): self.headers += e.headers
            elif isinstance(e, DataReceived): self.body += e.data
            if getattr(e, "stream_ended", False): self.done.set()

async def main(url, cafile, timeout):
    u = urlparse(url)
    cfg = QuicConfiguration(is_client=True, alpn_protocols=H3_ALPN, server_name=u.hostname)
    if cafile: cfg.load_verify_locations(cafile)
    async with connect(u.hostname, u.port or 443, configuration=cfg, create_protocol=Client) as c:
        sid = c._quic.get_next_available_stream_id()
        c.h3.send_headers(sid, [(b":method", b"GET"), (b":scheme", b"https"), (b":authority", u.hostname.encode()), (b":path", (u.path or "/").encode())], end_stream=True)
        c.transmit()
        await asyncio.wait_for(c.done.wait(), timeout)
        for k, v in c.headers: print(k.decode(), v.decode())
        sys.stdout.write(c.body.decode())

asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None, 5))
