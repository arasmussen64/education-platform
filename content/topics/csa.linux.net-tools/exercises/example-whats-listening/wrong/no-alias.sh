# Wrong: the name looked up is shop.internal, not www.shop.internal, so the
# answer has no CNAME line; the walkthrough's point was that www is an
# alias.
mkdir -p ~/example
sudo tcpdump -nn -i eth1 -c 3 'tcp port 8080' > ~/example/handshake.txt & sleep 1; from-office curl -s http://shop.internal:8080/ > /dev/null; wait
sudo tcpdump -nn -i eth1 -c 2 'tcp port 5432' > ~/example/refused.txt & sleep 1; from-office nc -z -w 2 shop.internal 5432; wait
ip route | awk '/^default/ {print $3}' > ~/example/gateway.txt
sudo ss -ltnp > ~/example/listening.txt
from-office dig +short shop.internal > ~/example/names.txt
