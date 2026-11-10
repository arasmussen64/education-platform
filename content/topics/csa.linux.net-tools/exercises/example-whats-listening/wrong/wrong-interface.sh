# Wrong: the capture listens on eth0, the cloud side, while the office's
# packets arrive on eth1, so it sees nothing and gives up.
mkdir -p ~/example
sudo timeout 5 tcpdump -nn -i eth0 -c 3 'tcp port 8080' > ~/example/handshake.txt & sleep 1; from-office curl -s http://shop.internal:8080/ > /dev/null; wait
sudo tcpdump -nn -i eth1 -c 2 'tcp port 5432' > ~/example/refused.txt & sleep 1; from-office nc -z -w 2 shop.internal 5432; wait
ip route | awk '/^default/ {print $3}' > ~/example/gateway.txt
sudo ss -ltnp > ~/example/listening.txt
from-office dig +short www.shop.internal > ~/example/names.txt
