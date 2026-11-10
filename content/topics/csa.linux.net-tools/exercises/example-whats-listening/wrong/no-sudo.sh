# Wrong: the listening table was saved without sudo, so the services that
# run as other users have no process name next to their port.
mkdir -p ~/example
sudo tcpdump -nn -i eth1 -c 3 'tcp port 8080' > ~/example/handshake.txt & sleep 1; from-office curl -s http://shop.internal:8080/ > /dev/null; wait
sudo tcpdump -nn -i eth1 -c 2 'tcp port 5432' > ~/example/refused.txt & sleep 1; from-office nc -z -w 2 shop.internal 5432; wait
ip route | awk '/^default/ {print $3}' > ~/example/gateway.txt
ss -ltnp > ~/example/listening.txt
from-office dig +short www.shop.internal > ~/example/names.txt
