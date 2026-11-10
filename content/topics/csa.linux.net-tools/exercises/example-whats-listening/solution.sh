ip -br addr
ip route
sudo ss -ltnp
from-office dig +short www.shop.internal; from-office nc -zv shop.internal 8080; from-office nc -zv shop.internal 5432; from-office curl -sI http://shop.internal:8080/ | head -1; from-office traceroute -n shop.internal
mkdir -p ~/example; sudo tcpdump -nn -i eth1 -c 3 'tcp port 8080' > ~/example/handshake.txt & sleep 1; from-office curl -s http://shop.internal:8080/ > /dev/null; wait; cat ~/example/handshake.txt
sudo tcpdump -nn -i eth1 -c 2 'tcp port 5432' > ~/example/refused.txt & sleep 1; from-office nc -z -w 2 shop.internal 5432; wait; cat ~/example/refused.txt
ip route | awk '/^default/ {print $3}' > ~/example/gateway.txt; sudo ss -ltnp > ~/example/listening.txt; from-office dig +short www.shop.internal > ~/example/names.txt; cat ~/example/gateway.txt ~/example/names.txt
