# The three faults, each fixed in lb's /etc/haproxy/haproxy.cfg (a learner
# uses nano; s|A|B| replaces A with B):
# 1. The check asked /health, which asks the database every web server
#    shares, so its maintenance job took all three out at once and the shop
#    answered 503. /livez checks the server itself.
# 2. fall 1 rise 1: one failed check took a server out and one good one put
#    it back, so web2, which fails a check now and then, flapped. fall 3
#    rise 2: three failures in a row to go, two good checks to come back. A
#    hung server is still out after about 3 x (1 + 1) = 6 seconds.
# 3. web3, whose pages are broken, was kept out with the runtime API only,
#    which every restart of HAProxy forgets. disabled on its line keeps it
#    out for good.
on lb sed -i 's|GET /health|GET /livez|; s|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
on lb haproxy -c -f /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 3
for i in $(seq 1 6); do on office curl -s -o /dev/null -w '%{http_code}\n' http://10.0.9.1/; done
