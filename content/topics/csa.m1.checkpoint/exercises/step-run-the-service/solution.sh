# The one part left: enable the service so it starts on boot, and start it now.
sudo systemctl enable --now shop-api
# Prove it: on this machine, from the office through the firewall, and the
# key login that was already working.
sleep 1
curl -s localhost:8080
from-office curl -s http://10.0.9.1:8080/
ssh -i ~/keys/ben -o StrictHostKeyChecking=no -o BatchMode=yes ben@localhost whoami
