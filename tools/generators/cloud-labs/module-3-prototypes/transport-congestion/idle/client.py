import socket, sys, time
idle = int(sys.argv[1]); ka = sys.argv[2]
c = socket.socket()
if ka != "off":
    c.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    if ka != "on":
        c.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, int(ka))
        c.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
        c.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
c.settimeout(8)
c.connect(("10.0.2.20", 5432))
f = c.makefile("rwb", buffering=0)
def q(n):
    t = time.time()
    try:
        c.sendall(b"q%d\n" % n); r = f.readline()
        print("query %d: %r in %.2fs" % (n, r, time.time() - t), flush=True)
    except Exception as e:
        print("query %d failed after %.2fs: %s" % (n, time.time() - t, e), flush=True)
q(1); print("local port", c.getsockname()[1], flush=True)
time.sleep(idle)
q(2)
