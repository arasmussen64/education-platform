#!/usr/bin/python3
"""udpfeed.py server|client ...: a price feed over UDP.
server: remembers every address that sent it anything, and pushes an update
        to each of them every PUSH seconds.
client KEEPALIVE: subscribes once, then (if KEEPALIVE > 0) sends a keepalive
        datagram every KEEPALIVE seconds; prints each update with its time."""
import socket, sys, threading, time

if sys.argv[1] == "server":
    push = float(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 7000))
    subs = set()
    def pusher():
        n = 0
        while True:
            time.sleep(push)
            n += 1
            for a in list(subs):
                s.sendto(b"price update %d\n" % n, a)
    threading.Thread(target=pusher, daemon=True).start()
    while True:
        data, addr = s.recvfrom(2048)
        subs.add(addr)
else:
    ka = float(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.0.2.20", 7000))
    s.send(b"subscribe\n")
    t0 = time.time()
    def keep():
        while ka > 0:
            time.sleep(ka)
            s.send(b"keepalive\n")
    threading.Thread(target=keep, daemon=True).start()
    s.settimeout(float(sys.argv[3]))
    try:
        while True:
            d = s.recv(2048)
            print("%5.1fs %s" % (time.time() - t0, d.decode().strip()), flush=True)
    except socket.timeout:
        print("%5.1fs no more updates" % (time.time() - t0), flush=True)
